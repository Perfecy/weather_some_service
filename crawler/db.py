from sshtunnel import SSHTunnelForwarder
import pymongo
import config

MONGO_HOST = config.MONGO_HOST
MONGO_DB = config.MONGO_DB
MONGO_USER = config.MONGO_USER
MONGO_PASS = config.MONGO_PASS

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=("0.0.0.0", 27017),
)

server.start()

client = pymongo.MongoClient("0.0.0.0", server.local_bind_port)
db = client[MONGO_DB]
merged_data = db.merged_data
unmerged_data = db.unmerged_data
