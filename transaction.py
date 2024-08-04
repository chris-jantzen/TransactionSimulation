# Individual details of a transaction
# Id
# Op count
# Bool for if it is currently blocked
# Bool for if it has committed
# Bool for if it has rolled back
    # Perhaps the above 3 could be done via a "state" enum
# Count of the number of cycles it has been blocked for
# Should rollback method (maybe)

from random import randint
from enum import Enum

class State(Enum):
    BLOCKED = 'blocked'
    COMMITTED = 'committed'
    ROLLEDBACK = 'rolledback'
    ACTIVE = 'active'

class Operation(Enum):
    READ = 'read'
    WRITE = 'write'

class SQLQuery:
    def __init__(self, dataId, operation):
        self.dataId = dataId
        self.operation = operation

class Transaction:
    def __init__(self, id):
        # Might make sense to take the transactionId as input so the transaction manager
        # can quickly check in the transaction list (or maybe the log) to see if the id it randomly generates
        # is already in use
        # self.transactionId = randint(1, 100000000)
        self.transactionId = id
        self.state = State.ACTIVE
        self.opCount = 0
        self.blockedCycleCount = 0

        # TODO:
        # SQL Query which contains the data id, operation, and lock held (if any)
        self.sqlQuery = None
        self.locks = []

    def updateState(self, newState):
        self.state = newState

    def shouldRollback(self, timeout):
        return self.blockedCycleCount >= timeout

    def setSqlQuery(self, dataId, operation):
        # If SQL Query already exists, should not be able to create a new one
        if self.sqlQuery is not None:
            raise Exception(f"SQL Query already exists for transaction {self.transactionId}")
        self.sqlQuery = SQLQuery(dataId, operation)

    def addLock(self, lock):
        self.locks.append(lock)

    def hasLockOnDataItem(self, dataId):
        for l in self.locks:
            if dataId == l.dataId:
                return True
        return False

    def removeALock(self, lock):
        self.locks.remove(lock)
