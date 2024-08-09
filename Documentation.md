# Chris Jantzen Transaction Simulator

## Running Instructions

How to run the simulation

```shell
python3 sim.py cycles t_size start_prob write_prob rollback_prob timeout
```

### Example

```shell
python3 sim.py 50 5 .5 0.4 0.2 6
```

### Python Version Info

Python version information: I wrote this using python 3.12.4. I've utilized type hints, which I think is probably the newest feature used here which seems to just require python 3.5.

## Code Documentation

I've pretty heavily commented the code describing flow and what most branches are for, but the general pattern is as follows:

The main simulation loop is in sim.py where it first ensures that the db file and the log file both at least exist and ensures the db file has the 32 bits it is supposed to if it is empty.

Following, the recovery manager is used to initiate the recovery process. The recovery manager also manages handling all of the logging.
    For handling rollbacks, as we had discussed in class, I've opted to implement redo type logs to make it easier for handling the redo phase of the recovery process.

The transaction manager manages creating, executing, committing, and rolling back transactions.

The buffer manager is used for tracking the in-memory data as well as flushing the data to the disk or reading it in on restart.

The lock manager manages the locks on each data item in the db. It supports exclusive and shared locks for each item as well as a queue of locks waiting for the data item where when a lock is released, it will automatically do among the following -
    - Grant the lock to the next item in the queue.
    - If a transaction holds the only shared lock on the item and was waiting for an exclusive lock promotion in the queue, promote that lock type to exclusive to allow the transaction to perform a write operation.
    - If the next item in the queue is a shared lock, and there were other shared lock requests waiting in the queue after it, then grant all of those shared lock requests and add them to the lock holder list

    Supports requesting locks, releasing locks, and checking to see if the manager has granted the lock (or the lock promotion) since the last cycle

The transaction object itself tracks the query it is trying to make as well as operation count details, the data item locks it holds, and information on how long its been blocked.

Throughout, there are many Enums for modeling state, such as OperationType and transaction State, lock types, log types, etc. that exist in the same file as the manager they most closely relate to for ease of locating if needed.

Code hosted at https://github.com/chris-jantzen/TransactionSimulation