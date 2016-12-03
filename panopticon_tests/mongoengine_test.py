import pymongo

# Connection to Mongo DB
try:
    conn=pymongo.MongoClient(host='192.168.99.100')
    print("Connected successfully!!!")
except pymongo.errors.ConnectionFailure as e:
   print("Could not connect to MongoDB: %s" % e)
print(conn)

db = conn.biw
print(conn.database_names())
print(list(db.biw1_robots.find()))