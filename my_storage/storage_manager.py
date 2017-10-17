import logging.config
from dao import db

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class StorageManager():
    def __init__(self):
        self.mydb = db.DsvDb()
        if self.mydb.query('storage_tbl', {'storage_name': 'total'})==None:
            self.add_sto('total', 'ff:ff:ff:ff:ff:ff', 0)
        logger.info('Init storage over')

    def add_sto(self, name, mac, total_storage):
        query_info=self.mydb.query('storage_tbl',{'storage_name':name})
        if not query_info==None:
            return False
        item = {'storage_name': name, 'mac': mac, 'total_storage': total_storage, 'remain_storage': total_storage}
        self.mydb.add('storage_tbl', item)
        total_info = self.mydb.query('storage_tbl', {'storage_name': 'total'})
        self.mydb.update('storage_tbl', {'storage_name': 'total'},
                         {'total_storage': total_info['total_storage'] + total_storage,
                          'remain_storage': total_info['remain_storage'] + total_storage})
        return True

    def remove_sto(self, name):
        # cp data for not to lose user's file
        rm_info = self.mydb.query('storage_tbl', {'storage_name': name})
        if rm_info==None:
            return False
        rm_total = rm_info['total_storage']
        rm_remain = rm_info['remain_storage']
        total_info = self.mydb.query('storage_tbl', {'storage_name': 'total'})
        self.mydb.update('storage_tbl', {'storage_name': 'total'},
                         {'total_storage': total_info['total_storage'] - rm_total,
                          'remain_storage': total_info['remain_storage'] - rm_remain})
        self.mydb.remove('storage_tbl',{'storage_name':name})
        return True


if __name__ == '__main__':
    myStorageManager = StorageManager()
    myStorageManager.add_sto('local', '00:11:22:33:44:55', 1073741824)
