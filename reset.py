# Read what the file was
dbFile = open("db.txt", "r")
txt = dbFile.read()
print(txt)

# Reset the file to just be 0's
dbFile = open("db.txt", "w")
dbFile.write("0".zfill(32))

