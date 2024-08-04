# TODO: re-familiarize with strict 2PL to make sure I do all the rules right.
# generally, I think it's just that you can't free any locks until commiting, and after you commit,
# you can start freeing them all.

# Can you free multiple locks in one cycle?

from enum import Enum

class LockType(Enum):
    SHARED = "shared"
    EXCLUSIVE = "exclusive"

class Lock:
    def __init__(self, transactionId, dataId, type):
        self.transactionId = transactionId
        self.dataId = dataId
        self.type = type

class LockManager():
    __instance = None

    # Dictionary that tracks locks on data items and the queue of transactions waiting for them
    #    Might not even actually need to track who is waiting, since it's first come first served
    #    can maybe just note the id of the transaction that has it right now along with the type of lock.

    def getInstance(self):
        if LockManager.__instance is None:
            LockManager()
        return LockManager.__instance

    def __init__(self):
        if LockManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        self.locks = dict.fromkeys(range(0, 32), [])

        LockManager.__instance = self

    # Method to request a lock on a data item
    def requestLock(self, dataId, transactionId, type) -> bool:
        if dataId not in range(0, 31):
            raise Exception(f"Invalid dataId: {dataId}")

        lockEntry = self.locks.get(dataId)

        if len(lockEntry) == 0:
            self.locks.update({ dataId: Lock(transactionId, dataId, type)})
            return True
        elif type is LockType.SHARED and len([l for l in lockEntry if l.type is LockType.SHARED]) == len(lockEntry):
            # Can grant lock, all locks on this item are shared
            self.locks.update({ dataId: [*lockEntry, Lock(transactionId, dataId, type)] })
            return True
        elif type is LockType.EXCLUSIVE and len(lockEntry) != 0:
            # Cannot grant lock where there already exists any kind of lock
            return False
        else:
            return False

    # Method to free a lock on a data item
    def freeLock(self, dataId, transactionId):
        # Verify that the lock actually exists
        lockEntry = self.locks.get(dataId)
        lockFound = False
        for l in lockEntry:
            if l.transactionId == transactionId:
                lockFound = True
                break
        if lockFound is False:
            raise Exception(f"Lock with transactionId {transactionId} not found for data item {dataId}")

        # Free up the lock
        newLockEntry = []
        for l in lockEntry:
            if l.transactionId is not transactionId:
                newLockEntry.append(l)
        self.locks.update({dataId: newLockEntry})

    # Grant lock method? Should the next lock in the queue automaticaly be granted a lock or is starvation allowed?
        # I think first draft, I'm good with allowing starvation

