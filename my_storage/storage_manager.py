import logging.config
from dao import db

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class StorageManager():
    def __init__(self):
        self.mydb = db.DsvDb()
        self.add_sto('total', 'ff:ff:ff:ff:ff:ff', 0)
        logger.info('Init storage over')

    def add_sto(self, name, mac, total_storage):
        item = {'storage_name': name, 'mac': mac, 'total_storage': total_storage, 'remain_storage': total_storage}
        self.mydb.add('storage_tbl', item)
        total_info = self.mydb.query('storage_tbl', {'storage_name': 'total'})
        self.mydb.update('storage_tbl', {'storage_name': 'total'},
                         {'total_storage': total_info['total_storage'] + total_storage,
                          'remain_storage': total_info['remain_storage'] + total_storage})

    def remove_sto(self, name):
        # cp data for not to lose user's file
        rm_info = self.mydb.query('storage_tbl', {'storage_name': name})
        rm_total = rm_info['total_storage']
        rm_remain = rm_info['remain_storage']
        total_info = self.mydb.query('storage_tbl', {'storage_name': 'total'})
        self.mydb.update('storage_tbl', {'storage_name': 'total'},
                         {'total_storage': total_info['total_storage'] - rm_total,
                          'remain_storage': total_info['remain_storage'] - rm_remain})


if __name__ == '__main__':
    myStorageManager = StorageManager()
    myStorageManager.add_sto('local', '00:11:22:33:44:55', 1073741824)
