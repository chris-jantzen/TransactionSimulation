from enum import Enum

class LogType(Enum):
    START = "S"
    FLIP = "F"
    ROLLBACK = "R"
    COMMIT = "C"

class Log():
    def __init__(self, logType, transactionId, dataId = None, newValue = None):
        self.type = logType
        self.transactionId = transactionId
        self.dataId = dataId
        self.newValue = newValue

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
        # Use a semaphore to place a hold on the log buffer

        if logType is LogType.START or logType is LogType.COMMIT or logType is LogType.ROLLBACK:
            self.__logBuffer.append(Log(logType, transactionId))
        elif logType is LogType.FLIP:
            if dataId is None:
                raise Exception("DataId cannot be None for a Flip log")
            if newValue is None:
                raise Exception("NewValue cannot be None for a Flip log")

            self.__logBuffer.append(Log(logType, transactionId, dataId, newValue))
        else:
            raise Exception(f"Invalid Logtype {logType}")

        # Release the semaphore on the log buffer
        return

    def flushLogs(self):
        pass
