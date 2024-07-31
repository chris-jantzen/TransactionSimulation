# TODO:
# need to read in the variables from the input and assign them to global variables
#
# cycles - number of cycles for the simulation
# transaction size - The size of a transaction in number of operations
# start probability - The probability of a new transaction starting in this cycle
# write probability - The probability that the transaction's operation on this cycle will be a write (decimal < 1)
# rollback probability - The probability of a rollback operation (decimal < 1)
# timeout - The timeout to wait in the event of a deadlock

# Ex log entries
# 0,S (transactionId, Start)
# 0,0,1,F (transactionId, old value, new value, Operation (i.e. write))
# 0,R (transactionId, rollback)
# 0,C (transactionId, commit)

# Need to read the log file and DB file to make sure that the DB is in the correct state

# FOR EACH CYCLE
#
#   Determine if a new transaction starts (rng based on start prob)
#     If it does, add it to the running list (a transaction needs a unique identifier)
#     Make a start entry for the log (transactionId, S for that it's a start type log)
#
#   For each active transaction
#     Submit an operation consisting of one of the folowing:
#       1. (TransactionId, DataId (i.e. the index of the data item, randomly selected 0 - 31), and opration (read/write determined by write probability input))
#       2. (TransactionId rollback) - if the random rollback has been hit decided based on rollback probability
#       3. (TransactionId, commit) - If the size has reached transaction size
#    Handle locking for each transaction operation
#    If a transaction has been blocked for a number of cycles, then apply the timeout (QUESTION: What is that number of cycles)
#      If a transaction is blocked, mark it as blocked in the transaction runlist so it won't try to create a new operation (will need to note what operation and on what dataId it's waiting for)
#
#   If a transaction is marked as terminated, it should be skipped
#
#   If at a multiple of 25 cycles, write the database updates to the disk and any logs associated with those updates should similarly be flushed to the log file (do the logs first).




# When the number of cycles has been reached, then the system "crashes", so you the logs will not be flushed (unless the termination point is at a multiple of 25)
