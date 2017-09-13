from util.logger import log_init
from my_storage import client


log_init("storage_test.log")
server_ip,server_port="127.0.0.1",47521
mysocket=client.get_socket(server_ip,server_port)

