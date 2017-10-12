#!/usr/bin/env python

import os
import re
import math


class gpu_control():
    def __init__(self, control_files_dict):

        # For controlling the PWM
        self.res = 255  # 8bits
        self.control_files_dict = control_files_dict

        # file = open(self.control_files_dict['pwm1'], 'r')
        # self.value = int(file.read())
        # file.close()

        # file = open(self.control_files_dict['pwm1_enable'], 'r')
        # self.enable = int(file.read())
        # file.close()
        self.pwm = self.get_fan_pwm()


        #For controlling the overclock
        #TODO


    def set_fan_pwm(self, duty_cycle):
        self.pwm = duty_cycle
        self.value = math.ceil((self.pwm / 100) * self.res)

        if (self.value > self.res): #make sure it does not go higher then 100
            self.value = self.res
            self.pwm = (self.value / self.res) * 100 # correct it if it went above max

        file = open(self.control_files_dict['pwm1'], 'w')
        file.write(str(self.value))
        file.close()

    def change_fan_pwm(self, delta):
        self.pwm += delta
        self.value = math.ceil((self.pwm / 100) * self.res)

        if (self.value > self.res): #make sure it does not go higher then 100
            self.value = self.res
            self.pwm = (self.value / self.res) * 100 # correct it if it went above max

        file = open(self.control_files_dict['pwm1'], 'w')
        file.write(str(self.value))
        file.close()

    def get_fan_pwm(self):
        file = open(self.control_files_dict['pwm1'], 'r')
        self.value = int(file.read())
        file.close()

        return math.ceil((self.value / self.res) * 100)

    def get_temperature(self):
        file = open(self.control_files_dict['temp1_input'], 'r')
        temperature = int(file.read()) / 1000
        file.close()
        return int(temperature)

    # def set_min_pwm(self, v):
    #     None
    #
    # def set_max_pwm(self, v):
    #     None

    def enable_fan_pwm_control(self, v):
        file = open(self.control_files_dict['pwm1_enable'], 'w')
        if v == True:
            file.write("1")
            self.enable = True
        elif v == False:
            file.write("0")
            self.enable = False
        file.close()


def find_gpu_cards():
    working_base_dir = '/sys/class/drm/'
    filename = 'pwm'

    cards = []

    for (dirpath, dirnames, filenames) in os.walk(working_base_dir):
        for dir_l0 in dirnames:
            if re.match('card\d$', dir_l0): #finds for example card0, which ends after the number. $ is the anchor
                #Walk into the subdir
                dir_l1 = dirpath + dir_l0 + '/device/hwmon/'
                for (dirpath, dirnames, filenames) in os.walk(dir_l1):
                    for dir_l2 in dirnames:
                        if re.match('hwmon\d$', dir_l2): #get into hwmonX
                            dir_l3 = dirpath + dir_l2

                            filenames = os.listdir(dir_l3)
                            control_files_dict = {}
                            for filename in filenames:
                                if filename.startswith('pwm1') or filename.startswith('temp1'):
                                    control_files_dict[filename] = dir_l3 + '/' + filename #grab the files used to control the pwm

                            if len(control_files_dict) > 0:
                                cards.append(gpu_control(control_files_dict))

    return cards



cards = find_gpu_cards()
card0 = cards[0]
card0.set_fan_pwm(70)
print(cards)