from enum import Enum
import csv

from bufferManager import BufferManager

class LogType(Enum):
    START = "S"
    FLIP = "F"
    ROLLBACK = "R"
    COMMIT = "C"
    REDO = "REDO"

    def __str__(self):
        return str(self.value)

class Log():
    def __init__(self, logType, transactionId, dataId = None, newValue = None):
        self.logType = logType
        self.transactionId = transactionId
        self.dataId = dataId
        self.newValue = newValue

    def formatLog(self):
        log = [self.transactionId]
        if self.dataId is not None:
            log.append(self.dataId)
        if self.newValue is not None:
            log.append(self.newValue)
        log.append(str(self.logType))
        return log

class RecoveryManager():
    __instance = None

    def getInstance(self):
        if RecoveryManager.__instance is None:
            RecoveryManager()
        return RecoveryManager.__instance

    def __init__(self):
        if RecoveryManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        self.__logBuffer = []
        self.__undoList = []

        RecoveryManager.__instance = self

    def createLog(self, logType, transactionId, dataId = None, newValue = None):
        # Use a semaphore (MUTEX) to place a hold on the log buffer

        log = None
        if logType is LogType.START or logType is LogType.COMMIT or logType is LogType.ROLLBACK:
            log = Log(logType, transactionId)
            self.__logBuffer.append(log)
        elif logType is LogType.FLIP:
            if dataId is None:
                raise Exception("DataId cannot be None for a Flip log")
            if newValue is None:
                raise Exception("NewValue cannot be None for a Flip log")

            log = Log(logType, transactionId, dataId, newValue)
            self.__logBuffer.append(log)
        else:
            raise Exception(f"Invalid Logtype {logType}")

        with open('log.csv', 'a', newline='\n') as logfile:
            log_writer = csv.writer(logfile)
            log_writer.writerow(log.formatLog())

        # Release the semaphore on the log buffer

    def getLogsReverseScan(self):
        for log in reversed(self.__logBuffer):
            yield log

    def recover(self):
        bm = BufferManager.getInstance()

        # Go through the log buffer forwards
        with open('log.csv', 'r') as logfile:
            log_reader = csv.reader(logfile)
            for logLine in log_reader:
                logType = logLine[-1]
                transactionId = logLine[0]
                dataId = None
                newValue = None

                if len(logLine) == 4:
                    dataId = logLine[1]
                    newValue = logLine[2]

                if logType is LogType.START.value:
                    # Add transaction to the undo list as start log is seen
                    self.__undoList.append(transactionId)

                if logType is LogType.COMMIT.value or logType is LogType.ROLLBACK.value:
                    # Remove transactions from the undo list as rollback and commit type logs are seen
                    self.__undoList.remove(transactionId)

                # Redo every flip and redo operation seen
                if logType is LogType.FLIP.value or logType is LogType.REDO.value:
                    # invert the new value and update the buffer
                    if newValue == '1':
                        bm.setValueAtLocation(dataId, '0')
                    else:
                        bm.setValueAtLocation(dataId, '1')


        # Finally just rollback any transactions that remain in the undo list and add rollback logs for each (would normally be abort logs)
        with open('log.csv', 'r') as logfile:
            log_reader = csv.reader(logfile)
            # Read backwards from the end this time
            for logLine in reversed(log_reader):
                if logLine[0] not in self.__undoList:
                    continue

                logType = logLine[-1]
                transactionId = logLine[0]

                if logType is LogType.START.value:
                    self.__undoList.remove(transactionId)
                    continue

                dataId = logLine[1]
                newValue = logLine[2]

                if logType is LogType.FLIP.value or logType is LogType.REDO.value:
                    # TODO: See if it works out okay to have these redo logs at the end of the log of if they need inserted immediately after
                    # the rollback log. I think it should work okay, as long as it is after
                    if newValue == '1':
                        bm.setValueAtLocation(dataId, '0')
                        self.createLog(LogType.REDO, transactionId, dataId, '0')
                    else:
                        bm.setValueAtLocation(dataId, '1')
                        self.createLog(LogType.REDO, transactionId, dataId, '1')
