#!/usr/bin/env python

import os
import re
import math


class gpu_control():
    def __init__(self, index, control_files_dict):

        self.index = index
        self.control_files_dict = control_files_dict

        # For controlling the PWM
        self.res = 255  # 8bits
        self.t_setpoint = 73 #operates at 70 degrees by default

        self.pwm = 180 #set initially at 70%
        self.set_fan_pwm(self.pwm)

    def set_temperature_setpoint(self, v):
        if v < 40 or v > 85:
            print('Not recommended temperature setpoint. Better between 50C and 85C. Not setting.')
            return

        self.t_setpoint = v

    def get_temperature_setpoint(self):
        return self.t_setpoint

    def control_temperature(self):
        #Simple proportional controller
        t_actual = self.get_temperature()
        C = 4
        diff = t_actual - self.t_setpoint

        if diff == 0:
            return

        self.pwm += diff * C
        self.set_fan_pwm(self.pwm)

    def set_fan_pwm(self, value):
        if (value > self.res): #make sure it does not go higher then 255
            print('Invalid fan speed. Instead setting it to 100%.')
            self.pwm = self.res
        elif value < 70:
            print('Invalid fan speed. Instead setting it to ~30%.')
            self.pwm = 70
        else:
            self.pwm = value

        file = open(self.control_files_dict['pwm1'], 'w')
        file.write(str(int(self.pwm)))
        file.close()
        print('Writen {}'.format(self.pwm))

    def get_fan_pwm(self):
        file = open(self.control_files_dict['pwm1'], 'r')
        pwm = int(file.read())
        file.close()
        print('Read {}'.format(pwm))
        return pwm

    def get_temperature(self):
        file = open(self.control_files_dict['temp1_input'], 'r')
        temperature = int(file.read()) / 1000
        file.close()
        return int(temperature)

    def set_core_freq(self, v):
        if v > 1150 or v < 650:
            print('Core clock out of range (650-1150 MHz). Not setting anything.')
        else:
            print('Setting GPU{} core frequency to {} MHz.'.format(self.indexv))
            cmd = './ ohgodatool -i {} --core-state -1 --core-clock {}'.format(self.index, v)
            # run(cmd)
            print(cmd)


    def get_core_freq(self, v):
        cmd = './ohgodatool -i {} --show-core'.format(self.index)
        # r = run(cmd)
        # print(r)

    def set_min_pwm(self, v):
        # TODO: implement
        None

    def set_max_pwm(self, v):
        # TODO: implement
        None

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
                index = int(dir_l0.replace('card',''))
                dir_l1 = dirpath + dir_l0 + '/device/hwmon/'
                for (dirpath, dirnames, filenames) in os.walk(dir_l1):
                    for dir_l2 in dirnames:
                        if re.match('hwmon\d$', dir_l2): #get into hwmonX
                            dir_l3 = dirpath + dir_l2

                            control_files_dict = {}
                            for filename in os.listdir(dir_l3):
                                if filename.startswith('pwm1') or filename.startswith('temp1'):
                                    control_files_dict[filename] = dir_l3 + '/' + filename #grab the files used to control the pwm

                            if len(control_files_dict) > 0:
                                cards.append(gpu_control(index, control_files_dict))



    return cards



cards = find_gpu_cards()
card0 = cards[0]
card0.set_fan_pwm(70)
print(cards)
