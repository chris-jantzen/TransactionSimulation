class DbManager():
    __instance = None

    def getInstance(self):
        if DbManager.__instance is None:
            DbManager()
        return DbManager.__instance

    def __init__(self):
        if DbManager.__instance is not None:
            raise Exception("Singleton cannot be instantiated more than once")

        self.buffer = "0".zfill(32)

        DbManager.__instance = self

    def flip(self, dataId):
        if self.buffer[dataId] == "0":
            self.buffer[dataId] = "1"
        else:
            self.buffer[dataId] = "0"

    def flush(self):
        # Write the buffer contents to the database
        pass