import logging.config
import hashlib
import struct
import os
import socket

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class Dsv():
    def __init__(self):
        self.BUFFER_SIZE = 1024
        self.HEAD_STRUCT = '128sIq32s'
        self.info_size = struct.calcsize(self.HEAD_STRUCT)
        self.username = "default"
        self.is_signed = False
        self.total_storage = 0
        self.remain_storage = 0
        self.file_list = []

    def set_recv_info(self, ip, port):
        self.data_recv_ip = ip
        self.data_recv_port = port
        logger.info("Self data recieve face is set as " + str(self.data_recv_ip) + ":" + str(self.data_recv_port))

    def set_server(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        logger.info("Target server is set as " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))

    def set_name(self,username):
        self.username=username

    def request_for_reply(self, request):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reply = 'EMPTY'
        try:
            sock.connect((self.SERVER_IP, self.SERVER_PORT))
            logger.info("Connect to server " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))
            sock.send(request.encode("utf-8"))
            logger.info("Request: " + request + " has been sent.")
            reply = sock.recv(self.BUFFER_SIZE).decode("utf-8")
            logger.info("Reply is: " + reply)
        except socket.error as e:
            logger.error(e)
        finally:
            sockname = sock.getsockname()
            sock.close()
            logger.info('Socket: ' + str(sockname) + ' has been closed.')
        return reply

    def sign_up(self, username):
        request = "REQ@@@SIGNUP@@@" + username
        reply = self.request_for_reply(request)
        if reply.startswith("REP@@@OK"):
            self.username = username
            self.is_signed = True
            logger.info('Sign up success, username is ' + username)
            return True
        else:
            logger.warning("Sign up failed.")
            return False

    def sign_out(self):
        request = 'REQ@@@SIGNOUT@@@' + self.username
        reply = self.request_for_reply(request)
        if reply.startswith('REP@@@OK'):
            return True
        else:
            return False

    def request_storage(self, size):
        request = "REQ@@@STO_REQ@@@" + self.username + '@@@' + str(size)
        logger.info("Request is: " + request)
        reply = self.request_for_reply(request)
        if reply == "REP@@@OK":
            self.total_storage += size
            self.remain_storage += size
            logger.info('Request storage ' + str(size) + ' success.')
            return True
        elif reply == "REP@@@NO":
            logger.warning("Storage size " + str(size) + " request failed!")
            return False

    def sync_user_info(self):
        request = 'SYNC@@@' + self.username
        reply = self.request_for_reply(request)
        if reply.startswith('REP@@@OK'):
            self.is_signed = True
            self.total_storage = int(reply.split('@@@')[2])
            self.remain_storage = int(reply.split('@@@')[3])
            logger.info('Synchron success.')
            return True
        else:
            logger.info('Synchron failed.')
            return False

    def query_file_list(self):
        request = 'REQ@@@FILELIST@@@' + self.username
        reply = self.request_for_reply(request)
        logger.info(reply)
        if reply.startswith('REP@@@'):
            filelist = list(eval(reply.split('@@@')[1]))
            self.file_list = filelist
            return filelist
        else:
            return None

    def upload_request(self, dst_path, filename, filesize):
        request = 'REQ@@@UPLOAD@@@' + self.username + '@@@' + dst_path + '@@@' + filename + '@@@' + str(filesize)
        reply = self.request_for_reply(request)
        if reply.startswith('REP@@@ERROR_NAME'):
            logger.warning('Filename in this path is already exist.')
            return None
        elif reply.startswith('REP@@@ERROR_STO'):
            logger.warning('You do not have enough storage.')
            return None
        elif reply.startswith('REP@@@OK'):
            logger.info('You can now upload your file.')
            return reply.split('@@@')[2]

    def upload_file(self, data_service_port, filepath):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.SERVER_IP, data_service_port)
        file_name, file_name_len, file_size, md5 = self.get_file_info(filepath)
        file_head = struct.pack(self.HEAD_STRUCT, file_name.encode('utf-8'), file_name_len, file_size,
                                md5.encode('utf-8'))
        sock.connect(server_address)
        sock.send(file_head)
        sent_size = 0
        with open(filepath, 'rb') as fr:
            while sent_size < file_size:
                remained_size = file_size - sent_size
                send_size = self.BUFFER_SIZE if remained_size > self.BUFFER_SIZE else remained_size
                send_file = fr.read(send_size)
                sent_size += send_size
                sock.send(send_file)
        reply = sock.recv(self.BUFFER_SIZE).decode('utf-8')
        if reply.startswith('REP@@@OK'):
            logger.info('Upload file success.')
            flag = True
        else:
            logger.warning('Upload file failed.')
            flag = False
        sock.close()
        return flag

    def download_file(self, dst_path, filepath):
        request = 'REQ@@@DOWNLOAD@@@' + self.username + '@@@' + filepath + '@@@' + self.data_recv_ip + '@@@' + str(
            self.data_recv_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.SERVER_IP, self.SERVER_PORT))
            logger.info("Connect to server " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))
            sock.send(request.encode("utf-8"))
            logger.info("Request: " + request + " has been sent.")
        except socket.error as e:
            logger.error(e)
        finally:
            logger.info('Socket: ' + str(sock.getsockname()) + ' has been closed.')
            sock.close()
        flag = self.recieve_data(dst_path)
        return flag

    def recieve_data(self, dst_path):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.data_recv_ip, self.data_recv_port))
        logger.info("Server socket bind to " + str(self.data_recv_ip) + ":" + str(self.data_recv_port))
        server_socket.listen(1)
        logger.info("Start listening")
        logger.info("Waiting for connect...")
        data_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        file_info_package = data_socket.recv(self.info_size)
        file_name, file_size, md5_recv = self.unpack_file_info(file_info_package)
        if file_name == 'REP@@@NO':
            logger.warning('File does not exist.')
            flag = False
        else:
            recved_size = 0
            dir = dst_path
            if not os.path.exists(dir):
                os.makedirs(dir)
                logger.info('Make dir over.')
            else:
                logger.warning('Dir already exists.')
            filepath = dst_path + '\\' + file_name
            with open(filepath, 'wb') as fw:
                while recved_size < file_size:
                    remained_size = file_size - recved_size
                    recv_size = self.BUFFER_SIZE if remained_size > self.BUFFER_SIZE else remained_size
                    recv_file = data_socket.recv(recv_size)
                    recved_size += recv_size
                    fw.write(recv_file)
            md5 = self.cal_md5(filepath)
            if md5 == md5_recv:
                logger.info('Received successfully.')
                flag = True
            else:
                os.remove(filepath)
                logger.warning('MD5 compared fail!')
                flag = False
        data_socket.close()
        return flag

    def unpack_file_info(self, file_info):
        file_name, file_name_len, file_size, md5 = struct.unpack(self.HEAD_STRUCT, file_info)
        file_name = file_name[:file_name_len]
        return file_name.decode('utf-8'), file_size, md5.decode('utf-8')

    def remove_file(self, filepath):
        request = 'REQ@@@REMOVE@@@' + self.username + '@@@' + filepath
        reply = self.request_for_reply(request)
        if reply.startswith('REP@@@OK'):
            return True
        elif reply.startswith('REP@@@NO'):
            return False

    def cal_md5(self, file_path):
        with open(file_path, 'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def get_file_info(self, file_path):
        file_name = os.path.basename(file_path)
        file_name_len = len(file_name)
        file_size = os.path.getsize(file_path)
        md5 = self.cal_md5(file_path)
        return file_name, file_name_len, file_size, md5
