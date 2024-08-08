from util import DB_PATH, getInverseValue

class BufferManager():
    __instance = None

    @staticmethod
    def getInstance():
        if BufferManager.__instance is None:
            BufferManager()
        return BufferManager.__instance

    def __init__(self):
        if BufferManager.__instance is not None:
            raise Exception('Singleton cannot be instantiated more than once')

        with open(DB_PATH, 'r') as dbFile:
            self.__buffer = dbFile.read()

        BufferManager.__instance = self

    def flip(self, dataId: str):
        flippedValue = getInverseValue(self.__buffer[dataId])
        self.__buffer = self.__buffer[:dataId] + flippedValue + self.__buffer[dataId + 1:]

    def getValueAtLocation(self, dataId: str):
        return self.__buffer[dataId]

    def setValueAtLocation(self, dataId: str, value: str):
        self.__buffer = self.__buffer[:dataId] + value + self.__buffer[dataId + 1:]

    def flush(self):
        with open(DB_PATH, 'w') as dbFile:
            dbFile.write(self.__buffer)