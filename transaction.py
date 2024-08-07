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
        self.transactionId = id # ID comes in from transactionManager
        self.state = State.ACTIVE
        self.opCount = 0
        self.__blockedCycleCount = 0

        self.__sqlQuery = None
        self.__locks = []

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

    def resetSqlQuery(self):
        self.__sqlQuery = None

    def addLock(self, dataId):
        '''dataId is the data item that has a lock on it'''
        self.__locks.append(dataId)

    def hasLockOnDataItem(self, dataId):
        for l in self.__locks:
            if dataId == l.dataId:
                return True
        return False

    def releaseLocks(self):
        self.__locks = []

    def getLocks(self):
        for l in self.__locks:
            yield l
