import logging.config
from scapy.all import *
import datetime

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

if __name__=='__main__':

    #pkt=Ether(dst='F0:76:1C:9F:B1:A6',src='F0:76:1C:9F:B1:A4')/'lijq'
    # pkt= IP(src='192.168.46.101', dst='192.168.100.149')/TCP(sport=12345,dport=5555)/'lijq'
    # pkt.show()
    # send(pkt, inter=1, count=1)
    print(datetime.datetime.now())
    a = Ether() / IP(dst="www.slashdot.org") / TCP() / "GET /index.html HTTP/1.0 \n\n"
    b=a.show2()
    print(b)
    send(a)
    print(datetime.datetime.now())

