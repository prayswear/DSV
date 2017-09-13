import logging
import socket


def get_socket(ip,port):
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect((ip, port))
    logging.info("Connect to server " + str(ip) + ":" + str(port))
    return mysocket


