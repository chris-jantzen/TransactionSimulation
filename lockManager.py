from enum import Enum
from collections import deque

class LockType(Enum):
    SHARED = "shared"
    EXCLUSIVE = "exclusive"

class LockHoldingState(Enum):
    CORRECT_TYPE = "correctType"
    WRONG_TYPE = "wrongType"
    DOES_NOT_HOLD = "doesNotHold"

class LockDetails():
    def __init__(self, transactionId: int, type: LockType):
        self.transactionId = transactionId
        self.type = type
        self.waitingForUpgrade = False

class LockInstance:
    def __init__(self):
        self.lockHolder = []
        self.queue = deque()

class LockManager():
    __instance = None

    @staticmethod
    def getInstance():
        if LockManager.__instance is None:
            LockManager()
        return LockManager.__instance

    def __init__(self):
        if LockManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        # Map of DataId => LockInstance (Details of lock holder and queue waiting for the lock)
        # self.__dataItemLockMap = dict.fromkeys(range(0, 32), LockInstance())
        self.__dataItemLockMap = dict([(i, LockInstance()) for i in range(0, 32)])

        LockManager.__instance = self

    # Method to request a lock on a data item
    def requestLock(self, dataId: int, transactionId: int, type: LockType) -> bool:
        if dataId not in range(0, 32):
            raise Exception(f"Invalid dataId: {dataId}")

        lockInstance = self.__dataItemLockMap.get(dataId)

        if len(lockInstance.lockHolder) == 0:
            # Nothing holds the lock
            lockInstance.lockHolder.append(LockDetails(transactionId, type))
            return True
        # elif len(list(filter(lambda l: l.transactionId == transactionId, lockInstance.lockHolder))) != 0:
        elif self.__already_holds_lock_with_correct_type(lockInstance, transactionId, type) is LockHoldingState.CORRECT_TYPE:
            # If you already have a lock on this item, then you should be able to upgrade it to an exclusive lock
            # If some other transaction also has a shared lock on this item, then place the exclusive type lock in the queue

            # Transaction already has a lock on this item TODO: be sure to check that you have an exclusive lock on this item
            return True
        elif self.__already_holds_lock_with_correct_type(lockInstance, transactionId, type) is LockHoldingState.WRONG_TYPE:
            if type is LockType.EXCLUSIVE:
                # Need to upgrade the shared lock to exclusive
                # If the transaction already has a lock on this item, then it should be able to upgrade it to an exclusive lock, but
                # if another transaction also has a shared lock on this item, then place the exclusive type lock request in the queue

                if len(lockInstance.lockHolder) > 1:
                    lockInstance.queue.append(LockDetails(transactionId, type))
                    # TODO: On "releaseLock", when a shared lock is released, should check to see if any waitingForUpgrade transactions can be upgraded
                    return False
                else:
                    # Upgrade the lock type to exclusive
                    lockInstance.lockHolder[0].type = LockType.EXCLUSIVE
                    return True
            else:
                # An exclusive lock will work fine for a read, so no action needs to be done
                return True
        elif type is LockType.SHARED and len(list(filter(lambda l: l.type is not LockType.SHARED, lockInstance.lockHolder))) == 0:
            # All existing holders of the lock are compatible (all lockholders have shared locks)
            lockInstance.lockHolder.append(LockDetails(transactionId, type))
            return True
        else:
            # Lock is held by an incompatible lock, must wait in queue
            lockInstance.queue.append(LockDetails(transactionId, type))
            return False

    def __already_holds_lock_with_correct_type(self, lockInstance: LockInstance, transactionId: str, type: LockType) -> LockHoldingState:
        for holder in lockInstance.lockHolder:
            if transactionId != holder.transactionId:
                continue

            if type == holder.type:
                return LockHoldingState.CORRECT_TYPE
            else:
                return LockHoldingState.WRONG_TYPE

        return LockHoldingState.DOES_NOT_HOLD
        # Check that the lock type I'm asking for now is already there
        # If I already have a shared lock, but want an exclusive lock, then make sure that no other transaction has a shared lock
            # If a transaction does have a shared lock on this item, then add an exclusive lock to the queue

    # Method to release a lock on a data item
    def releaseLock(self, dataId: int, transactionId: int):
        # Verify that the lock exists on the data item for the transaction
        lockInstance = self.__dataItemLockMap.get(dataId)
        lockFound = False
        for l in lockInstance.lockHolder:
            if l.transactionId == transactionId:
                lockFound = True
                break
        if lockFound is False:
            raise Exception(f"TransactionId {transactionId} not found to be holding a lock for dataId {dataId}")

        # Release the lock held on dataId of transactionId
        lockInstance.lockHolder = list(filter(lambda l: l.transactionId != transactionId, lockInstance.lockHolder))

        if len(lockInstance.lockHolder) == 1:
            # Check to see if there are any transactions in the queue waiting for a lock type upgrade
            for index, item in enumerate(lockInstance.queue):
                if item.waitForLockTypeUpgrade is True and item.transactionId == lockInstance.lockHolder[0]:
                    # remove this item from the queue
                    del lockInstance.queue[index]
                    # Upgrade the lock type of the lock holder
                    lockInstance.lockHolder.type = LockType.EXCLUSIVE
            return

        # If some other transaction still holds a shared lock on this item, then exit
        if len(lockInstance.lockHolder) > 0:
            return

        # If there's no other transaction still holding the lock, then check the queue, and bring in the next lock in line
        if len(lockInstance.queue) > 0:
            lockInstance.lockHolder.append(lockInstance.queue[0])
            lockInstance.queue.popleft()
            # If the lockholder that has just been added is a shared type and there are also other shared lock type transaction ops
            # waiting in the queue, grant them the lock as well.
            if lockInstance.lockHolder[0].type is LockType.SHARED:
                for l in lockInstance.queue:
                    if l.type is LockType.SHARED:
                        lockInstance.lockHolder.append(l)

    def hasLockBeenGranted(self, dataId: int, transactionId: int):
        details = self.__dataItemLockMap.get(dataId)
        for holder in details.lockHolder:
            if holder.transactionId == transactionId:
                return True
        return False