from lockManager import LockManager
from recoveryManager import LogType, RecoveryManager
from transaction import OperationType, Transaction, State
from random import randint

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

        self.transactions = []

        self.opCount = 0

        TransactionManager.__instance = self

    def __does_id_already_exist(self, id):
        return (next(filter(lambda x: x.transactionId == id, self.transactions), False) is not False)

    def __get_transaction(self, transactionId):
        for transaction in self.transactions:
            if transaction.transactionId == transactionId:
                return transaction
        return None

    def createTransaction(self):
        t_id = randint(0, 100000000)
        transaction = Transaction(t_id)
        if not self.__does_id_already_exist(t_id):
            self.transactions.append(transaction)
            return
        else:
            self.createTransaction()

    def getTransactions(self):
        for t in self.transactions:
            if t.state is not State.COMMITTED and t.state is not State.ROLLEDBACK:
                yield t

    def executeOperation(self, transactionId) -> bool:
        # Get the transaction, look at the transactions sqlQuery operation, request lock, if lock granted execute transaction
        transaction = self.__get_transaction(transactionId)
        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} not found")

        # if operation sqlQuery operation is a write and can be executed, increment the opCount variable
        if transaction.getSqlQuery().operationType is OperationType.WRITE:
            transaction.opCount += 1 # TODO: Make opcount increment method on the transaction class
            self.opCount += 1 # Write op happening, increment count to know when to flush to disk
            # Do the operation
            # if the opCount variable reaches 25, then use the DbManager singleton class instance to flush the buffer to the DB
            if self.opCount == 25:
                self.opCount = 0
                return True # FLUSH BUFFER TO DISK
            return False # DON'T FLUSH BUFFER TO DISK
        elif transaction.getSqlQuery().operationType is OperationType.READ:
            # Do the operation
            # Free the shared lock (strict 2PL only requires holding the exclusive locks until committing)
            pass

    def commitTransaction(self, transactionId):
        transaction = None
        for t in self.transactions:
            if t.transactionId == transactionId:
                transaction = t

        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} does not exist; cannot commit")

        # create commit log with the recoveryManager and make sure it goes to storage
        rm = RecoveryManager.getInstance()
        rm.createLog(LogType.COMMIT, transaction.transactionId)

        # Flush logs to the log file (Optional, right now just planning to push logs directly to the log file as soon as they're made)

        lm = LockManager.getInstance()
        # Free locks associated with the transaction
        for lock in transaction.getLocks():
            lm.releaseLock(lock.dataId, transaction.transactionId)

    def rollbackTransaction(self, transactionId):
        # Insert a rollback log with the recoveryManager
        rm = RecoveryManager.getInstance()
        rm.createLog(LogType.ROLLBACK, transactionId)

        # Use the recoveryManager to look at the logs
            # Go backwards from the end looking for where the transactionId matches
        for log in rm.getLogsReverseScan():
            if log.transactionId == transactionId and log.logType is LogType.FLIP:
                # Need to take the dataId and update the buffer in the bufferManager wit the inverse of the new value
                # Whenever we replace the NewValue with the old Value, append an update log <t_id, data_id, old_value, RB> TODO: Add rollback LogType
                pass
            if log.transactionId == transactionId and log.Type is LogType.START:
                # done, no need to keep looking back through the logs
                break

        pass

