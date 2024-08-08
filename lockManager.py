from enum import Enum
from collections import deque

class LockType(Enum):
    SHARED = "shared"
    EXCLUSIVE = "exclusive"

class LockDetails():
    def __init__(self, transactionId: str, type: LockType):
        self.transactionId = transactionId
        self.type = type

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
        self.__dataItemLockMap = dict.fromkeys(range(0, 32), LockInstance())

        LockManager.__instance = self

    # Method to request a lock on a data item
    def requestLock(self, dataId: str, transactionId: str, type: LockType) -> bool:
        if dataId not in range(0, 31):
            raise Exception(f"Invalid dataId: {dataId}")

        lockInstance = self.__dataItemLockMap.get(dataId)

        if len(lockInstance.lockHolder) == 0:
            # Nothing holds the lock
            lockInstance.lockHolder.append(LockDetails(transactionId, type))
            return True
        elif type is LockType.SHARED and len(list(filter(lambda l: l.type is not LockType.SHARED, lockInstance.lockHolder))) == 0:
            # All existing holders of the lock are compatible (all lockholders have shared locks)
            lockInstance.lockHolder.append(LockDetails(transactionId, type))
            return True
        else:
            # Lock is held by an incompatible lock, must wait in queue
            lockInstance.queue.append(LockDetails(transactionId, type))
            return False

    # Method to release a lock on a data item
    def releaseLock(self, dataId: str, transactionId: str):
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

    def hasLockBeenGranted(self, dataId: str, transactionId: str):
        details = self.__dataItemLockMap.get(dataId)
        for holder in details.lockHolder:
            if holder.transactionId == transactionId:
                return True
        return False