import config 
import couchdb

couchdb_url = config.COUCHDB_URL
db_server = couchdb.Server(couchdb_url)
latency_db = db_server['workflow_latency']
