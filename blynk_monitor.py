# from blynkapi import Blynk
import time
from urllib.request import urlopen

class blynk():
    def __init__(self):
        self.my_auth_token = ""
        # my_server = 'joaofl.ddns.net'
        self.my_server = '192.168.1.2' #only works inside the VPN
        self.my_port = '8080' # not sure
    def set_value(self, pin, value):
        url = 'http://{}:{}/{}/update/{}?value={}'.format(self.my_server, self.my_port, self.my_auth_token, pin, value)

        try:
            urlopen(url)
        except:
            print('Failed to open {}'.format(url))


# while(True):
#
#     b = blynk()
#     b.set_value('V0', 25)
#     time.sleep(2)