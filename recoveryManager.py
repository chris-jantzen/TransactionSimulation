from enum import Enum
import csv

class LogType(Enum):
    START = "S"
    FLIP = "F"
    ROLLBACK = "R"
    COMMIT = "C"

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
        return

    def flushLogs(self):
        # TODO: I think maybe rather than flushing the log buffer, I'll just immediately write the logs to the log file
        # Seems easier to have the logs in memory than having to read them back.
        #
        # Alternatively, I could flush the logs to the buffer and then clean my in memory log so it would be purely just
        # starting from the beginning after a flush and then just appending to the log, but then handling rollbacks may be tough
        pass
