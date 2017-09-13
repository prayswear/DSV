import socket
import threading
import logging.config
from dao import db
import datetime
import hashlib
import struct


class ClientServer():
    def __init__(self, ip, port):
        self.server_ip = ip
        self.server_port = port
        self.dataport = 47520
        self.BUFFER_SIZE = 1024
        self.HEAD_STRUCT = '128sIq32s'
        self.info_size = struct.calcsize(self.HEAD_STRUCT)
        self.remain_storage = 0
        self.client_list = {}
        self.file_list = {}
        self.storage_list = {}
        self.mydb = db.DsvDb()

    def info_init(self):
        # get basic info from database
        self.remain_storage = self.mydb.query('storage_tbl', {'storage_name': 'total'})
        logger.info('ClientServer remain storage is ' + self.remain_storage)
        client_result = self.mydb.query_all('client_tbl', {})
        file_result = self.mydb.query_all('file_tbl', {})
        storage_result = self.mydb.query_all('storage_tbl', {})

        if not client_result == None:
            for i in client_result:
                self.client_list[i['client_name']] = i
        if not file_result == None:
            for i in file_result:
                self.file_list[i['filepath']] = i
        if not storage_result == None:
            for i in storage_result:
                self.storage_list[i['server_name']] = i
        logger.info('ClientServer info init over.')

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.server_ip, self.server_port))
        logger.info("Server socket bind to " + str(self.server_ip) + ":" + str(self.server_port))
        server_socket.listen(5)
        logger.info("Start listening")
        while True:
            logger.info("Waiting for connect...")
            client_socket, address = server_socket.accept()
            logger.info("Connect to client, socket is " + str(address))
            threading._start_new_thread(self.request_handler, (client_socket, address))

    def request_handler(self, client_socket, address):
        request = client_socket.recv(self.BUFFER_SIZE).decode("utf-8")
        reply = ''
        if request.startswith("REQ@@@SIGNUP"):
            reply = self.sign_up_handler(request)
        elif request.startswith('REQ@@@SIGNOUT'):
            reply = self.sign_out_handler(request)
        elif request.startswith("REQ@@@STO_REQ"):
            reply = self.storage_request_handler(request)
        elif request.startswith('REQ@@@UPLOAD'):
            reply = self.upload_handler(request)
        elif request.startswith('SYNC@@@'):
            reply = self.sync_handler(request)
        else:
            pass

        client_socket.send(reply.encode("utf-8"))
        client_socket.close()
        logger.info("Socket: " + str(address) + " has been closed.")

    def sign_up_handler(self, request):
        # request is like: REQ@@@SIGNUP@@@lijq
        username = request.split("@@@")[2]
        logger.info("Sign up name is " + username)
        if not self.name_exist(username):
            # TODO check if db operate success
            self.mydb.client_tbl_add(username, datetime.datetime.now())
            self.client_list[username] = {'username': username, 'total_storage': 0, 'remain_storage': 0,
                                          'lmt': datetime.datetime.now()}
            logger.info('Sign up a new user: ' + username)
            reply = "REP@@@OK"
        else:
            reply = "REP@@@NO"
        return reply

    def sign_out_handler(self, request):
        # request is like: REQ@@@SIGNOUT@@@lijq
        username = request.split("@@@")[2]
        if not self.name_exist(username):
            # TODO check if db operate success
            self.mydb.remove('client_tbl', {'username': username})
            del self.client_list[username]
            # TODO clear user's file
            logger.info('Remove an user: ' + username)
            reply = "REP@@@OK"
        else:
            reply = "REP@@@NO"
        return reply

    def name_exist(self, username):
        # check if the name is exist
        if username in self.client_list.keys():
            return True
        else:
            return False

    def sync_handler(self, request):
        # request is like: SYNC@@@lijq
        username = request.split('@@@')[1]
        if self.name_exist(username):
            reply = 'REP@@@OK@@@' + self.client_list[username]['total_storage'] + '@@@' + self.client_list[username][
                'remain_storage']
        else:
            reply = 'REP@@@NO'
        return reply

    def check_storage(self, name, size):
        # TODO need to add user max request size
        if size <= self.remain_storage:
            return True
        else:
            return False

    def storage_request_handler(self, request):
        # reqest is like: REQ@@@STO_REQ@@@lijq@@@1048576
        username = request.split("@@@")[2]
        size = int(request.split("@@@")[3])
        logger.info('Client ' + username + ' requests for ' + str(size) + ' storage.')
        if self.check_storage(username, size):
            self.client_list[username]['total_storage'] += size
            self.client_list[username]['remain_storage'] += size
            self.mydb.update('client_tbl', {'username': username},
                             {'total_storage': self.client_list[username]['total_storage'],
                              'remain_storage': self.client_list[username]['remain_storage']})
            msg = "REPLY@@@OK"
        else:
            msg = "REPLY@@@NO"
        return msg

    def upload_handler(self, request):
        request_split = request.split('@@@')
        username = request_split[2]
        dst_path = request_split[3]
        file_name = request_split[4]
        file_size = request_split[5]

        if self.filepath_exist(username, dst_path + file_name):
            reply = 'REP@@@ERROR_NAME'
        elif not self.check_user_storage(username, file_size):
            reply = 'REP@@@ERROR_STO'
        else:
            # TODO update db
            self.client_list[username]['remain_storage'] -= file_size
            self.mydb.update('client_tbl', {'username': username},
                             {'remain_storage': self.client_list[username]['remain_storage']})
            threading._start_new_thread(self.data_recv_handler, ())
            reply = 'REP@@@OK' + '@@@' + str(self.dataport)
        return reply

    def filepath_exist(self, user_name, filepath):
        if (user_name + '\\' + filepath) in self.file_list.keys():
            return True
        else:
            return False

    def check_user_storage(self, username, filesize):
        logger.info(self.client_list[username]['remain_storage'])
        if int(filesize) <= int(self.client_list[username]['remain_storage']):
            return True
        else:
            return False

    def data_recv_handler(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, data_port = "127.0.0.1", 47520
        server_socket.bind((host, data_port))
        server_socket.listen(1)
        logger.info("Server socket bind to " + str(host) + ":" + str(data_port))
        logger.info("Start listening")
        logger.info("Waiting for connect...")
        data_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        file_info_package = data_socket.recv(self.info_size)
        file_name, file_size, md5_recv = self.unpack_file_info(file_info_package)
        recved_size = 0
        with open(file_name, 'wb') as fw:
            while recved_size < file_size:
                remained_size = file_size - recved_size
                recv_size = self.BUFFER_SIZE if remained_size > self.BUFFER_SIZE else remained_size
                recv_file = data_socket.recv(recv_size)
                recved_size += recv_size
                fw.write(recv_file)
        md5 = self.cal_md5(file_name)
        if md5 == md5_recv:
            reply = 'REP@@@OK'
            logger.info('Received successfully')
        else:
            reply = 'REP@@@NO'
            logger.warning('MD5 compared fail!')
        data_socket.close()

    def add_storage(self):
        pass

    def remove_storage(self):
        pass

    def unpack_file_info(self, file_info):
        file_name, file_name_len, file_size, md5 = struct.unpack(self.HEAD_STRUCT, file_info)
        file_name = file_name[:file_name_len]
        return file_name.decode('utf-8'), file_size, md5.decode('utf-8')

    def cal_md5(self, file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5


if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('myLogger')
