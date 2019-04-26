# -*- coding: utf-8 -*-

import random
import uuid
import requests
import string
import socket
import struct

HOME_HOST = "http://127.0.0.1:8000/pyrat3_server/api/"

def random_string(str_length):
    """Generate a random string of fixed length """
    listtt = ''.join([i for i in string.ascii_uppercase if 'O' not in i])
    chars = listtt + string.digits
    return ''.join(random.choice(chars) for i in range(str_length))

def random_ip():
    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    return ip

os_list = [
    'Windows XP',
    'Windows 7',
    'Windows 8',
    'Windows 8.1',
    'Windows 10',
]

names = [
    'Thick',
    'ASUS',
    'HP-WORKSTATION',
    'Tomek',
    'Notebook',
    'MyComputer',
    'T442ASX-01'
]

user_data = {
    'pc_uuid': str(uuid.uuid4()).upper(),
    'mac': random_string(12),
    'os': random.choice(os_list),
    'name': random.choice(names),
    'int_ip': random_ip(),
    'ext_ip': random_ip(),
    'country': 'PL',
}

get_status = requests.post(HOME_HOST, json=user_data)
