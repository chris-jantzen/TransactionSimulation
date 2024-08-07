class BufferManager():
    __instance = None

    def getInstance(self):
        if BufferManager.__instance is None:
            BufferManager()
        return BufferManager.__instance

    def __init__(self):
        if BufferManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        with open("db.txt", "r") as dbFile:
            self.__buffer = dbFile.read()

        BufferManager.__instance = self

    def flip(self, dataId):
        if self.__buffer[dataId] == "0":
            self.__buffer[dataId] = "1"
        else:
            self.__buffer[dataId] = "0"

    def getValueAtLocation(self, dataId):
        return self.__buffer[dataId]

    def setValueAtLocation(self, dataId, value):
        self.__buffer[dataId] = value

    def flush(self):
        with open("db.txt", "w") as dbFile:
            dbFile.write(self.__buffer)