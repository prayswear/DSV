import logging.config
from my_client.dsv import Dsv
import os

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("myLogger")

mydsv = Dsv()
mydsv.set_server("127.0.0.1", 47523)
username = 'lijq'
storage = 1048576

path = 'C:\\Users\\47521\\Desktop\\'
# filename = 'test.txt'
filename = '123.png'
filesize = os.path.getsize(path + filename)

#mydsv.sign_up(username)

mydsv.username = username
mydsv.sync_user_info()
print(mydsv.is_signed)
#mydsv.request_storage(storage)
print(mydsv.remain_storage)

#data_service_port = mydsv.upload_request('mypic\\', filename, filesize)
#print(data_service_port)
#mydsv.upload_file(47520, path + filename)

print(mydsv.query_file_list())
#mydsv.set_recv_info('127.0.0.1',47777)
#mydsv.download_file('\\','mypic\\123.png')

