import sys
import os
import random
from lockManager import LockManager, LockType
from transaction import OperationType, State
from transactionManager import TransactionManager

cycles = sys.argv[1]
t_size = sys.argv[2]
start_prob = sys.argv[3]
write_prob = sys.argv[4]
rollback_prob = sys.argv[5]
timeout = sys.argv[6]

db_path = "db.txt"

if os.path.exists(db_path):
    with open(db_path, 'r') as file:
        print(file.read())
else:
    with open(db_path, 'x') as file:
        file.write("0".zfill(32))

log_path = "log.csv"

if not os.path.exists(log_path):
    with open(log_path, 'x') as file:
        file.write()

# 1. Read in the log file and start the recovery process (TODO: see if there's an easy way to parse the csv lines)
#  Redo back from the beginning (this is where having had redo logs may help to make it easy to redo what the rollbacks undid)
#  Undo the transactions that didn't have a commit or rollback

# 2. Begin simulation process
transactionManager = TransactionManager.getInstance()
lockManager = LockManager.getInstance()
for cycle in cycles:
    # Determine if a new cycle starts (if it does, create a new one in the transaction manager)
    if start_prob <= random.random():
        transactionManager.createTransaction()

    # For each active transaction in the transaction list (method in manager to get active transactions? Maybe use a generator with yield)
    for transaction in transactionManager.getTransactions():
        # Submit an operation to either read or write based on write_prob
        if transaction.state == State.BLOCKED:
            # Look at sqlQuery
            query = transaction.getSqlQuery()
            # Request lock again
            granted = lockManager.requestLock(query.dataId, transaction.transactionId, query.operationType)
            # If still blocked, check shouldRollBack
            if granted is False and transaction.shouldRollBack(timeout):
                # Initiate rollback if it should
                pass
        elif rollback_prob <= random.random():
            # INITIATE ROLLBACK
            # TODO: Handle rollback
            pass
        elif write_prob <= random.random():
            # Schedule sqlQuery
            dataId = random.randomint(0, 31)
            transaction.setSqlQuery(dataId, OperationType.WRITE)
            # Would need to request an exclusive lock
            requestStatus = lockManager.requestLock(dataId, transaction.transactionId, LockType.EXCLUSIVE)
            if requestStatus is True:
                transaction.addLock(dataId)
                transaction.resetBlockedCycleCount()
            else:
                transaction.state = State.BLOCKED
                transaction.incrementBlockedCycleCount
            pass
        else:
            # Schedule sql read query
            dataId = random.randomint(0, 31)
            transaction.setSqlQuery(dataId, OperationType.WRITE)
            # Would need to request a shared lock
            lockManager.requestLock(dataId, transaction.transactionId, LockType.SHARED)

        # Commit if op count has reached t_size
        if transaction.op_count == t_size:
            transactionManager.commitTransaction(transaction.transactionId)
        pass

    pass

# Needs:
#   Locking Manager
#     Handle shared and exclusive type locks
#     Track what transaction has what lock on what data item
#   Transaction Manager
#   Logging Manager
#   Buffer Manager