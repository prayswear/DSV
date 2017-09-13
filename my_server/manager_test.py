from my_server.client_manager import ClientServer
from dao import db

server_ip, server_port = "127.0.0.1", 47523

mydb = db.mappingdb()
mydb.db_reset()

myServer = ClientServer(server_ip, server_port)
myServer.info_init()
myServer.start()
