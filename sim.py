import sys
import random
from bufferManager import BufferManager
from lockManager import LockManager, LockType
from recoveryManager import RecoveryManager
from transaction import OperationType, State
from transactionManager import TransactionManager
from util import Action, getAction, initDbAndLogIfMissing

CYCLES = int(sys.argv[1])
T_SIZE = int(sys.argv[2])
START_PROB = float(sys.argv[3])
WRITE_PROB = float(sys.argv[4])
ROLLBACK_PROB = float(sys.argv[5])
TIMEOUT = int(sys.argv[6])

# Ensure the db and log files exist
initDbAndLogIfMissing()

# 1. Begin recovery phase
RecoveryManager.getInstance().recover()

# 2. Begin simulation process
transactionManager = TransactionManager.getInstance()
lockManager = LockManager.getInstance()

for cycle in range(CYCLES):
    # Determine if a new cycle starts (if it does, create a new one in the transaction manager)
    if START_PROB >= random.random():
        transactionManager.createTransaction()

    # For each active transaction in the transaction list
    for transaction in transactionManager.getTransactions():
        # Commit if op count has reached t_size
        if transaction.isReadyToCommit(T_SIZE):
            transactionManager.commitTransaction(transaction.transactionId)
            continue

        if transaction.getState() is State.BLOCKED:
            # Look at sqlQuery
            query = transaction.getSqlQuery()
            # Request lock again
            requestGranted = lockManager.hasLockBeenGranted(query.dataId, transaction.transaction)
            # If still blocked, check shouldRollBack
            if requestGranted is False:
                transaction.incrementBlockedCycleCount()
                if transaction.shouldRollback(TIMEOUT):
                    # Initiate rollback if it should
                    transactionManager.rollbackTransaction(transaction.transactionId)
            else:
                # Unblocked, do the operation
                transactionManager.executeOperation(transaction.transactionId)
        else:
            # Get what kind of action to take {Write, Rollback, Read}
            action = getAction(WRITE_PROB, ROLLBACK_PROB)
            if action is Action.WRITE:
                # Schedule write sqlQuery
                dataId = random.randint(0, 31)
                transaction.setSqlQuery(dataId, OperationType.WRITE)
                # Need to request an exclusive lock
                requestGranted = lockManager.requestLock(dataId, transaction.transactionId, LockType.EXCLUSIVE)
                if requestGranted is True:
                    # do the operation
                    transactionManager.executeOperation(transaction.transactionId)
                else:
                    # transaction is blocked
                    transaction.setState(State.BLOCKED)
                    transaction.incrementBlockedCycleCount()
            elif action is Action.ROLLBACK:
                # Initiate Rollback
                transactionManager.rollbackTransaction(transaction.transactionId)
            else:
                # Schedule sql read query
                dataId = random.randint(0, 31)
                transaction.setSqlQuery(dataId, OperationType.READ)
                # Would need to request a shared lock
                requestGranted = lockManager.requestLock(dataId, transaction.transactionId, LockType.SHARED)
                if requestGranted is True:
                    transaction.addLock(dataId)
