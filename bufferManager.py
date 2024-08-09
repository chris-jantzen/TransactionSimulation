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

        # self.__buffer = dict((i, '0') for i in range(0, 32))

        with open(DB_PATH, 'r') as dbFile:
            db = dbFile.read()
            # self.__buffer = dict((i, db[i]) for i in range(0, 32))
            self.__buffer = [db[i] for i in range(0, 32)]

        BufferManager.__instance = self

    def convertToBufferString(self):
        return ''.join(self.__buffer.values())
        # return ''.join(self.__buffer)

    def flip(self, dataId: int):
        flippedValue = getInverseValue(self.__buffer[dataId])
        self.__buffer[dataId] = flippedValue
        # self.__buffer.update({ dataId: flippedValue })

    def getValueAtLocation(self, dataId: str):
        return self.__buffer[dataId]

    def setValueAtLocation(self, dataId: int, value: str):
        self.__buffer[dataId] = value
        # self.__buffer.update({ dataId: value })

    def flush(self):
        with open(DB_PATH, 'w') as dbFile:
            dbFile.write(self.convertToBufferString())