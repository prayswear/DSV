import datetime

client_list = {}
client_list['lijq'] = {'client_name': 'lijq', 'total_storage': 0, 'remain_storage': 0,
                           'last_modify_time': datetime.datetime.now()}

print(client_list['lijq']['total_storage'])
