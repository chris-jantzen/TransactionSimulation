import os
import random
from enum import Enum

DB_PATH = "db.txt"
LOG_PATH = "log.csv"

def initDbAndLogIfMissing():
    # Initialize database file if it doesn't exist
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'x') as file:
            file.write('0'.zfill(32))

    # Fill db file if it doesn't have anything in it
    hasContents = True
    with open(DB_PATH, 'r') as dbfile:
        contents = dbfile.read()
        if contents is None or not contents.strip():
            hasContents = False
    if not hasContents:
        with open(DB_PATH, 'w') as dbfile:
            dbfile.write('0'.zfill(32))

    # Initialize log file if it doesn't exist
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'x') as file:
            file.write('')

def getInverseValue(value: str):
    if value == '1':
        return '0'
    else:
        return '1'

class Action(Enum):
    WRITE = "write"
    READ = "read"
    ROLLBACK = "rollback"

def getAction(WRITE_PROB: float, ROLLBACK_PROB: float):
    randomNumber = random.random()
    if WRITE_PROB >= randomNumber:
        return Action.WRITE
    elif WRITE_PROB + ROLLBACK_PROB >= randomNumber:
        return Action.ROLLBACK
    else:
        return Action.READ