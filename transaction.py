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

class OperationType(Enum):
    READ = 'read'
    WRITE = 'write'

class SQLQuery:
    def __init__(self, dataId, operationType):
        self.dataId = dataId
        self.operation = operationType

class Transaction:
    def __init__(self, id):
        # Might make sense to take the transactionId as input so the transaction manager
        # can quickly check in the transaction list (or maybe the log) to see if the id it randomly generates
        # is already in use
        # self.transactionId = randint(1, 100000000)
        self.transactionId = id
        self.state = State.ACTIVE
        self.opCount = 0
        self.__blockedCycleCount = 0

        # TODO:
        # SQL Query which contains the data id, operation, and lock held (if any)
        self.__sqlQuery = None
        self.locks = []

    def updateState(self, newState):
        self.state = newState

    def incrementTimout(self):
        self.__blockedCycleCount += 1

    def resetBlockedCycleCount(self):
        self.__blockedCycleCount = 0

    def shouldRollback(self, timeout):
        return self.__blockedCycleCount >= timeout

    def setSqlQuery(self, dataId, operation):
        # If SQL Query already exists, should not be able to create a new one
        # TODO: Clear the sql query when the lock can be acquired and the operation completed
        if self.__sqlQuery is not None:
            raise Exception(f"SQL Query already exists for transaction {self.transactionId}")
        self.__sqlQuery = SQLQuery(dataId, operation)

    def getSqlQuery(self):
        return self.__sqlQuery

    def addLock(self, dataId):
        '''dataId is the data item that has a lock on it'''
        self.locks.append(dataId)

    def hasLockOnDataItem(self, dataId):
        for l in self.locks:
            if dataId == l.dataId:
                return True
        return False

    def removeALock(self, lock):
        self.locks.remove(lock)
