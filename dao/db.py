import pymongo
import logging.config
import datetime

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class DsvDb():
    # class for basic database operate

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

    def get_db(self, ip, port, db_name):
        # make connect and get a db entry
        db_client = pymongo.MongoClient(ip, port)
        logger.info('Get connection client.')
        db = db_client[db_name]
        logger.info('Get database: ' + db_name)
        return db

    def add(self, tbl, item):
        item['lmt'] = datetime.datetime.now()
        self.db[tbl].insert(item)
        logger.info('Add new item: ' + str(item) + ' to ' + tbl)

    def update(self, tbl, condition, value):
        value['lmt'] = datetime.datetime.now()
        self.db[tbl].update(condition, {"$set": value})
        logger.info('Update ' + str(condition) + ' item in ' + tbl)

    def query(self, tbl, condition):
        result = self.db[tbl].find_one(condition)
        logger.info('Find ' + str(condition) + ' item in ' + tbl + ', result is ' + str(result))
        return result

    def query_all(self, tbl, condition):
        result = self.db[tbl].find(condition)
        logger.info('Find all ' + str(condition) + ' item in ' + tbl + ', result is ' + str(result))
        return result

    def remove(self, tbl, condition):
        result = self.db[tbl].remove(condition)
        logger.info('Remove item' + str(condition) + ' item from ' + tbl)

    def remove_all(self, tbl):
        self.db[tbl].remove({})
        logger.info('Remove all data from ' + tbl)

    def client_tbl_add(self, name):
        item = {'username': name, 'total_storage': 0, 'remain_storage': 0}
        self.add('client_tbl', item)

    def file_tbl_add(self, filename, owner, size, path, server_name, md5):
        item = {'filepath': path + filename, 'filename': filename, 'owner': owner, 'size': size, 'path': path,
                'storage_name': server_name, 'md5': md5}
        self.add('file_tbl', item)
