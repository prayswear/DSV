import logging.config
from my_client.dsv import Dsv
import os

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("myLogger")

mydsv = Dsv()
mydsv.set_server("127.0.0.1", 47523)
username = 'lijq'
storage = '1048576'

'''
mydsv.username=username
if not mydsv.sync_user_info():
    exit(0)
'''

if not mydsv.sign_up(username):
    exit(0)

if not mydsv.request_storage(storage):  # 1M
    exit(0)

path = 'C:\\Users\\47521\\Desktop\\'
# filename = 'test.txt'
filename = '123.png'
filesize = os.path.getsize(path + filename)

data_service_port = mydsv.upload_request('mypic\\', path + filename, filesize)
logger.info('File data upload port is ' + data_service_port)

if data_service_port == None:
    logger.error('Request upload failed.')
else:
    mydsv.upload_file(int(data_service_port), path + filename)
