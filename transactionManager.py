from transaction import Transaction, State
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

    def executeTransaction(self, transactionId):
        # Get the transaction, look at the transactions sqlQuery operation, request lock, if lock granted execute transaction
        transaction = self.__get_transaction(transactionId)
        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} not found")

        # if operation sqlQuery operation is a write and can be executed, increment the opCount variable
            # if the opCount variable reaches 25, then use the DbManager singleton class instance to flush the buffer to the DB
        pass

    def commitTransaction(self, transactionId):
        transaction = None
        for t in self.transactions:
            if t.transactionId == transactionId:
                transaction = t

        if transaction is None:
            raise Exception(f"Transaction with ID {transactionId} does not exist; cannot commit")

        # Flush logs to the log file

        # Free locks associated with the transaction
