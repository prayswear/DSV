from my_storage.storage_manager import StorageManager
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

if __name__=='__main__':
    mySM=StorageManager()
    mySM.add_sto('sto_server_1', '00:11:22:33:44:55', 1073741824)
    # mySM.remove_sto('sto_server_1')
