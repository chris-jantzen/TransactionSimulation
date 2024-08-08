from typing import Generator
from bufferManager import BufferManager
from lockManager import LockManager
from recoveryManager import LogType, RecoveryManager
from transaction import OperationType, Transaction, State
from random import randint
from util import getInverseValue

class TransactionManager:
    __instance = None

    @staticmethod
    def getInstance():
        if TransactionManager.__instance is None:
            TransactionManager()
        return TransactionManager.__instance

    def __init__(self):
        if TransactionManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        self.__transactions = []
        self.__writeOpCount = 0

        TransactionManager.__instance = self

    def __does_id_already_exist(self, id: str):
        return (next(filter(lambda x: x.transactionId == id, self.__transactions), False) is not False)

    def __getTransactionById(self, transactionId: str) -> Transaction | None:
        for transaction in self.__transactions:
            if transaction.transactionId == transactionId:
                return transaction
        return None

    def createTransaction(self):
        rm = RecoveryManager.getInstance()
        transactionId = randint(0, 100000000)
        transaction = Transaction(transactionId)

        if not self.__does_id_already_exist(transactionId):
            rm.createLog(LogType.START, transactionId)
            self.__transactions.append(transaction)
            return
        else:
            self.createTransaction()

    def getTransactions(self) -> Generator[Transaction]:
        for t in self.__transactions:
            # Get only transactions that aren't inactive (i.e. committed or rolled back)
            if t.getState() is not State.COMMITTED and t.getState() is not State.ROLLEDBACK:
                yield t

    def executeOperation(self, transactionId: str):
        # Get the transaction, look at the transactions sqlQuery operation, request lock, if lock granted execute transaction
        transaction = self.__getTransactionById(transactionId)
        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} not found")

        sqlQuery = transaction.getSqlQuery()
        transaction.setState(State.ACTIVE)
        transaction.addLock(transaction.getSqlQuery().dataId)
        transaction.resetBlockedCycleCount()
        transaction.resetSqlQuery()

        rm = RecoveryManager.getInstance()
        bm = BufferManager.getInstance()

        # if operation sqlQuery operation is a write and can be executed, increment the opCount variable
        if sqlQuery.operation is OperationType.WRITE:
            transaction.incrementOpCount()
            self.__writeOpCount += 1 # Write op happening, increment count to know when to flush to disk
            oldValue = bm.getValueAtLocation(sqlQuery.dataId)
            newValue = getInverseValue(oldValue)
            rm.createLog(LogType.FLIP, transactionId, sqlQuery.dataId, newValue)

            # Do the write operation
            bm.flip(sqlQuery.dataId)

            # if the opCount variable belonging to the transaction manager reaches 25, then use the BufferManager to flush to disk
            if self.__writeOpCount == 25:
                self.__writeOpCount = 0
                # Logs are already in "stable storage", so can flush to DB
                bm.flush()
        elif sqlQuery.operation is OperationType.READ:
            # Do the read operation
            _ = bm.getValueAtLocation(sqlQuery.dataId)
            transaction.incrementOpCount()

    def commitTransaction(self, transactionId: str):
        transaction = self.__getTransactionById(transactionId)
        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} does not exist; cannot commit")

        # create commit log with the recoveryManager and make sure it goes to storage
        rm = RecoveryManager.getInstance()
        rm.createLog(LogType.COMMIT, transaction.transactionId)

        # TODO: Delete comment when sure I won't be doing it this way
        # Flush logs to the log file (Optional, right now just planning to push logs directly to the log file as soon as they're made)

        lm = LockManager.getInstance()
        # Free locks associated with the transaction
        for dataIdWithLock in transaction.getLocks():
            lm.releaseLock(dataIdWithLock, transaction.transactionId)
        transaction.releaseLocks()
        transaction.setState(State.COMMITTED)

    def rollbackTransaction(self, transactionId: str):
        # Insert a rollback log with the recoveryManager
        rm = RecoveryManager.getInstance()
        rm.createLog(LogType.ROLLBACK, transactionId)

        # Use the recoveryManager to look at the logs
            # Go backwards from the end looking for where the transactionId matches
        bm = BufferManager.getInstance()
        for log in rm.getLogsReverseScan():
            if log.transactionId == transactionId and log.logType is LogType.FLIP:
                # Need to take the dataId and update the buffer in the bufferManager wit the inverse of the new value
                oldValue = getInverseValue(log.newValue)
                # Whenever we replace the NewValue with the old Value, append redo log <t_id, data_id, old_value, RB>
                rm.createLog(LogType.REDO, transactionId, log.dataId, oldValue)
                bm.setValueAtLocation(log.dataId, oldValue)
            if log.transactionId == transactionId and log.Type is LogType.START:
                # done, no need to keep looking back through the logs
                break

        transaction = self.__getTransactionById(transactionId)
        transaction.setState(State.ROLLEDBACK)


