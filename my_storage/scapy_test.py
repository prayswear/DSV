import logging.config
from scapy.all import *



if __name__=='__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('myLogger')


    #pkt=Ether(dst='F0:76:1C:9F:B1:A6',src='F0:76:1C:9F:B1:A4')/'lijq'
    pkt= IP(src='10.0.3.83', dst='10.0.3.88')/TCP(sport=12345,dport=5555)/'lijq'
    pkt.show()
    send(pkt, inter=1, count=1)