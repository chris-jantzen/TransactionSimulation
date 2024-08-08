from enum import Enum
from typing import Generator, Optional

class State(Enum):
    BLOCKED = 'blocked'
    COMMITTED = 'committed'
    ROLLEDBACK = 'rolledback'
    ACTIVE = 'active'

class OperationType(Enum):
    READ = 'read'
    WRITE = 'write'

class SQLQuery:
    def __init__(self, dataId: str, operationType: OperationType):
        self.dataId = dataId
        self.operation = operationType

class Transaction:
    def __init__(self, id: str):
        self.transactionId = id
        self.__state = State.ACTIVE
        self.__opCount = 0
        self.__blockedCycleCount = 0

        self.__sqlQuery = None
        self.__locks = [] # DataIds where this transaciton holds locks

    def setState(self, newState: State):
        self.__state = newState

    def getState(self) -> State:
        return self.__state

    def incrementBlockedCycleCount(self):
        self.__blockedCycleCount += 1

    def resetBlockedCycleCount(self):
        self.__blockedCycleCount = 0

    def shouldRollback(self, timeout: int) -> bool:
        return self.__blockedCycleCount >= timeout

    def incrementOpCount(self):
        self.__opCount += 1

    def isReadyToCommit(self, transactionSize: int) -> bool:
        return self.__opCount == transactionSize

    def setSqlQuery(self, dataId: str, operation: OperationType):
        # If SQL Query already exists, should not be able to create a new one
        if self.__sqlQuery is not None:
            raise Exception(f"SQL Query already exists for transaction {self.transactionId}")
        self.__sqlQuery = SQLQuery(dataId, operation)

    def getSqlQuery(self) -> Optional[SQLQuery]:
        return self.__sqlQuery

    def resetSqlQuery(self):
        self.__sqlQuery = None

    def addLock(self, dataId: str):
        # dataId is the data item that has a lock held on it by this transaction
        self.__locks.append(dataId)

    def hasLockOnDataItem(self, dataId: str):
        for l in self.__locks:
            if dataId == l.dataId:
                return True
        return False

    def releaseLocks(self):
        self.__locks = []

    def getLocks(self) -> Generator[str]:
        for l in self.__locks:
            yield l
