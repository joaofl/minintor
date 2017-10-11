#!/usr/bin/env python
# from urllib import *

from requests import get
from time import *
from math import floor
import logging
import numpy as np
import os



###################################################
class circular_buffer():
    def __init__(self, n_samples):

        self.__buffer = [0 for _ in range(n_samples)]
        self.__index = 0

    def add(self, value):

        if self.__index >= len(self.__buffer)-1:
            self.__buffer[0] = value
            self.__index = 1
        else:
            self.__buffer[self.__index] = value
            self.__index += 1

    def get_mean(self):
        return np.mean(self.__buffer)

    def get_sum(self):
        return np.sum(self.__buffer)
####################################################


def format_time(min):
    h = floor(min / 60)
    m = min % 60
    return '{:02}:{:02}'.format(h,m)

def query_claymore():
    try:
        response = get('http://localhost:3333/').content.decode()

        l = response.find('[') + 1
        r = response.find(']')

        content = response[l:r].replace('"', '').replace(' ', '').replace(';', ',').split(',')

        values = {
            'uptime': int(content[1]),
            'rate': int(content[2]) / 1000,
            'shares': int(content[3]),
            'temperature': int(content[10]),
            'fan': int(content[11])
        }
        # print(content)
    except URLError as e:
        print('Claymore client not found. Got an error code:{}',format(e))
        exit(-1)

    return values

##########################################################################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# create a file handler
current_dir = os.getcwd()
handler = logging.FileHandler(current_dir + '/miningtor.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)

###########################################################################################
stats_shares_hour = circular_buffer(60) #one sample per min
shares_previous = query_claymore()['shares'];
one_hour_shares = 0

logger.info('Started...')

while(True):
    now_h, now_m = localtime()[3:5]

    if now_m == 0:
        one_hour_shares = stats_shares_hour.get_sum()
        logger.info('Shares: {}'.format(one_hour_shares))
        #save to logfile here

    values = query_claymore()

    # if values['shares'] != shares_previous:
    stats_shares_hour.add(values['shares'] - shares_previous)
    shares_previous = values['shares']


    print('--------------------------------')
    print('Now: {:02}:{:02}'.format(now_h, now_m))
    print('Time running: ' + format_time(values['uptime']))
    print('Mining rate: {} Mh/s'.format(values['rate']))
    print('Total shares: {}'.format(values['shares']))
    print('Average shares rate: {:.2f} shares/h'.format(values['shares']/(values['uptime']/60)))
    print('One hour avg shares: {}'.format(stats_shares_hour.get_sum()))
    print('Last hour shares: {} (from {:02}h to {:02}h)'.format(one_hour_shares, now_h-1, now_h))
    print('--------------------------------')
    print('GPU Temperature: {}C (fan at {}%)'.format(values['temperature'], values['fan']))

    # exit(0)
    sleep(60)


