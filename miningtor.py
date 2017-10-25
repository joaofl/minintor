#!/usr/bin/env python
# from urllib import *

from requests import get
from time import *
from math import floor
import logging
import numpy as np
import os
import gpu_control
import threading
import blynk_monitor



###################################################
class circular_buffer():
    def __init__(self, n_samples):

        self.__n_samples = n_samples
        self.__buffer = [0 for _ in range(self.__n_samples)]
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

    def reset(self):
        self.__buffer = [0 for _ in range(self.__n_samples)]
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
    except Exception as e:
        print('Claymore client not found. Got an error code:{}',format(e))
        return -1
        # exit(-1)

    return values

def print_values(values):
    print('--------------------------------------------------')
    print('Now: {:02}:{:02}. Started at: {:02}:{:02}'.format(now_h, now_m, start_h, start_m))
    print('Time running: ' + format_time(values['uptime']))
    print('Mining rate: {} Mh/s'.format(values['rate']))
    print('Total shares: {}'.format(values['shares']))
    print('Average shares rate: {:.2f} shares/h'.format(values['shares']/(values['uptime']/60)))
    print('One hour avg shares: {}'.format(stats_shares_hour.get_sum()))
    print('Current hour shares: {} (since {:02}h)'.format(stats_shares_current_hour.get_sum(), now_h))
    print('Last hour shares: {} (from {:02}h to {:02}h)'.format(one_hour_shares, now_h-1, now_h))
    print('--------------------------------------------------')

###########################################################################################


def control_fan_speed(gpu):
    while(True):

        global pwm, t

        gpu.control_temperature()

        t = gpu.get_temperature()
        pwm = (gpu.get_fan_pwm()/255)*100

        print('GPU Temperature: {}C, setpoint {}C (fan at {:.1f}%)'.format(t, gpu.get_temperature_setpoint(), pwm))

        sleep(20)

def update_blynk():
    global claymore_values
    blynk = blynk_monitor.blynk()

    while(True):

        blynk.set_value('V0', claymore_values['rate'])
        blynk.set_value('V1', claymore_values['shares']/(claymore_values['uptime']/60))

        blynk.set_value('V10', pwm)
        blynk.set_value('V11', t)

        sleep(20)


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
#logger.addHandler(handler)
###########################################################################################

stats_shares_hour = circular_buffer(60) #one sample per min
stats_shares_current_hour = circular_buffer(60) #one sample per min

shares_previous = 0
one_hour_shares = 0

start_h, start_m = localtime()[3:5]
logger.info('Started...')

gpus = gpu_control.find_gpu_cards()

t_control = threading.Thread(target=control_fan_speed, args=[gpus[0]])
t_control.start()

update_blynk_th = threading.Thread(target=update_blynk)

pwm = 0
t=0

while(True):
    claymore_values = query_claymore()
    if claymore_values == -1:
        print('Claymore not ready. Waiting 10s...')
        sleep(10)
    else:
        break

shares_previous = claymore_values['shares']

update_blynk_th.start()

while(True):
    claymore_values = query_claymore()

    if claymore_values == -1:
        logger.info('Error connecting to Claymore client')
        sleep(10)
        continue

    now_h, now_m = localtime()[3:5]

    if now_m == 0:
        one_hour_shares = stats_shares_hour.get_sum()
        stats_shares_current_hour.reset()
        # logger.info('Shares: {}'.format(one_hour_shares))
        #save to logfile here

    last_min_shares = claymore_values['shares'] - shares_previous

    stats_shares_hour.add(last_min_shares)
    stats_shares_current_hour.add(last_min_shares)

    shares_previous = claymore_values['shares']

    print_values(claymore_values)

    # exit(0)
    sleep(60)



t_control.join()
exit()
