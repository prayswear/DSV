import pymongo
import logging.config
import datetime

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class DsvDb():
    # this class for basic database operate

    def __init__(self):
        # init var
        self.ip = '127.0.0.1'
        self.port = 27017
        self.db_name = 'dsv'
        self.db = self.get_db(self.ip, self.port, self.db_name)

    def db_reset(self):
        # remove all data in dsv's tables
        self.remove_all('storage_tbl')
        self.remove_all('client_tbl')
        self.remove_all('file_tbl')
        self.storage_tbl_add('total', 'ff:ff:ff:ff:ff:ff', 0, 0, datetime.datetime.now())
        self.storage_tbl_add('local', '00:11:22:33:44:55', 1073741824, 1073741824, datetime.datetime.now())
        self.update('storage_tbl', {'storage_name': 'total'},
                    {'total_storage': 1073741824, 'remain_storage': 1073741824})

    def get_db(self, ip, port, db_name):
        # make connect and get a db entry
        db_client = pymongo.MongoClient(ip, port)
        logger.info('Get connection client.')
        db = db_client[db_name]
        logger.info('Get database: ' + db_name)
        return db

    def add(self, tbl, item):
        self.db[tbl].insert(item)
        logger.info('Add new item: ' + str(item) + ' to ' + tbl)

    def update(self, tbl, condition, value):
        self.db[tbl].update(condition, {"$set": value})
        logger.info('Update ' + str(condition) + 'item in ' + tbl)

    def query(self, tbl, condition):
        result = self.db[tbl].find_one(condition)
        logger.info('Find ' + str(condition) + ' item in ' + tbl + ', result is ' + str(result))
        return result

    def query_all(self, tbl, condition):
        result = self.db[tbl].find(condition)
        return result

    def remove(self, tbl, condition):
        result = self.db[tbl].remove(condition)
        logger.info('Remove item' + str(condition) + ' item from ' + tbl)

    def remove_all(self, tbl):
        self.db[tbl].remove({})
        logger.info('Remove all data from ' + tbl)

    def client_tbl_add(self, name, lmt):
        item = {'username': name, 'total_storage': 0, 'remain_storage': 0,
                'lmt': lmt}
        self.add('client_tbl', item)

    def storage_tbl_add(self, name, mac, total_storage, remain_storage, lmt):
        item = {'storage_name': name, 'mac': mac, 'total_storage': total_storage, 'remain_storage': remain_storage,
                'lmt': lmt}
        self.add('storage_tbl', item)

    def file_tbl_add(self, filename, owner, size, path, server_name, lmt):
        item = {'filepath': path + filename, 'filename': filename, 'owner': owner, 'size': size, 'path': path,
                'storage_name': server_name, 'lmt': lmt}
        self.add('file_tbl', item)
