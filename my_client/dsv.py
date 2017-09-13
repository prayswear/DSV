import logging.config
import hashlib
import struct
import os
import socket

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('myLogger')


class Dsv():
    def __init__(self):
        self.BUFFER_SIZE = 1024
        self.HEAD_STRUCT = '128sIq32s'
        self.username = "default"
        self.is_signed = False
        self.total_storage = 0
        self.remain_storage = 0

    def set_server(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        logger.info("Target server is set as " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))

    def request_for_reply(self, request):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.SERVER_IP, self.SERVER_PORT))
            logger.info("Connect to server " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))
            sock.send(request.encode("utf-8"))
            logger.info("Request: " + request + " has been sent.")
            reply = sock.recv(BUFFER_SIZE).decode("utf-8")
            logger.info("Reply is: " + reply)
        except socket.error as e:
            logger.error(e)
        finally:
            sock.close()
            logger.info('Socket: ' + sock.getsockname() + ' has been closed.')
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
        if reply == "REPLY@@@OK":
            self.total_storage += size
            self.remain_storage += size
            logger.info('Request storage ' + size + ' success.')
            return True
        elif reply == "REPLY@@@NO":
            logger.warning("Storage size " + str(size) + " request failed!")
            return False

    def sync_user_info(self):
        request = 'SYNC@@@' + self.username
        reply = self.request_for_reply(request)
        if reply.startswith('REP@@@OK'):
            self.is_signed = True
            self.total_storage = reply.split('@@@')[2]
            self.remain_storage = reply.split('@@@')[3]
            logger.info('Synchron success.')
            return True
        else:
            logger.info('Synchron failed.')
            return False

    def query_file_list(self):
        pass

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

    def download_file(self, file):
        # 下载文件
        pass

    def remove_file(self, filepath):
        request = 'REQ@@@REMOVE@@@' + self.username + '@@@' + filepath
        reply = self.request_for_reply(request)
        if reply.startswith('REPLY@@@OK'):
            return True
        elif reply.startswith('REPLY@@@NO'):
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
