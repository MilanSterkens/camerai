from datetime import datetime, timedelta

import serial
import RPi.GPIO as GPIO
import time
import os

import logging


class AtModem(object):
    powerKey = 4
    logger = None
    backend = ''

    def __init__(self):
        self.logger = logging.getLogger('main')
        self.__install_device()
        self.__open()
        try:
            self.backend = os.getenv('BACKEND')
            print('BACKEND environment variable exists')
        except KeyError:
            print('BACKEND environment variable does not exist')

    def __install_device(self):
        self.logger.info('SIM7080X is starting')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.powerKey, GPIO.OUT)
        time.sleep(0.1)
        GPIO.output(self.powerKey, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.powerKey, GPIO.LOW)
        time.sleep(5)
        self.logger.info('SIM7080X is powered on')

    def uninstall_device(self):
        self.logger.info('SIM7080X is logging off')
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.powerKey, GPIO.OUT)
        GPIO.output(self.powerKey, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(self.powerKey, GPIO.LOW)
        time.sleep(5)
        self.logger.info('SIM7080X is turned off')
        GPIO.cleanup()

    def __open(self):
        self.ser = serial.Serial('/dev/ttyS0', 9600, timeout=100)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%y/%m/%d,%H:%M:%S%z")
        self.send_command('AT')
        self.send_command('AT+CMEE=2')
        self.send_command('AT+CCLK="' + formatted_datetime + '"')

    def ping_google(self):
        self.send_command('AT+SNPING4="www.google.com",3,16,1000')

    def get_gps(self):
        res = self.__get_gps_position()
        return res

    def upload_data(self, data):
        time.sleep(5)
        self.sendAt('AT+CGREG=1', 'OK')
        self.sendAt('AT+CNACT=0,1', 'OK')
        self.sendAt('AT+CSSLCFG="sslversion",1,3', 'OK')
        self.sendAt('AT+SHSSL=1,""', 'OK')
        self.sendAt('AT+SHCONF="URL","' + self.backend + '"', 'OK')
        self.sendAt('AT+SHCONF="BODYLEN",4096', 'OK')
        self.sendAt('AT+SHCONF="HEADERLEN",350', 'OK')
        self.sendAt('AT+SHCONN', 'OK', 20)
        self.sendAt('AT+SHCHEAD', 'OK')
        self.sendAt('AT+SHAHEAD="Content-Type","application/json"', 'OK')
        self.sendAt('AT+SHAHEAD="Cache-control","no-cache"', 'OK')
        self.sendAt('AT+SHAHEAD="Connection","close"', 'OK')
        self.sendAt('AT+SHAHEAD="Accept","*/*"', 'OK')
        self.send_command('AT+SHBOD=' + str(len(data)) + ',10000')
        time.sleep(4)
        self.ser.write(data.encode())
        time.sleep(4)
        self.send_command('AT+SHBOD?')
        time.sleep(4)
        res = self.sendAt('AT+SHREQ="/detection",3', '+SHREQ: "POST",200', 20)
        print(res)
        self.sendAt('AT+SHDISC', 'OK')
        if res == 1:
            return True
        return False

    def close(self):
        self.send_command('AT+CNACT=0,0')
        self.ser.close()

    def send_command(self, command):
        rec_buff = ''
        self.ser.write((command + '\r\n').encode())
        time.sleep(0.1)
        if self.ser.inWaiting():
            time.sleep(1)
            rec_buff = self.ser.read(self.ser.inWaiting())
        if rec_buff != '':
            print(rec_buff.decode())

    def __get_gps_position(self):
        rec_null = True
        answer = ''
        self.logger.info('Start GPS session...')
        time.sleep(5)
        self.sendAt('AT+CGNSPWR=1', 'OK', 0.1)
        while rec_null:
            answer = self.sendAt('AT+CGNSINF', '+CGNSINF: ', 4, True)
            if answer != '':
                answer = answer.replace('AT+CGNSPWR=1', '').replace('OK', '').replace('AT+CGNSINF', '').replace('+CGNSINF:', '').replace('\n', '').replace(' ', '')
                print(answer)
                if '1,,,0.000000,0.000000' in answer or ',,,,9999000.0,6000.0' in answer or '0,,,,,,,,,,,,,,,,,' in answer or ',,,,,,' in answer:
                    self.logger.info('GPS is not ready, response: ' + answer)
                    time.sleep(1)
                else:
                    break
            else:
                self.logger.error('error %d' % answer)
                self.sendAt('AT+CGNSPWR=0', 'OK', 1)
                return False
            time.sleep(1.5)
        self.sendAt('AT+CGNSPWR=0', 'OK')
        latitude, longitude = answer.split(',')[3], answer.split(',')[4]
        return latitude, longitude

    def sendAt(self, command, back=None, timeout=10, returnasstring=False):
        self.ser.write((command + '\r\n').encode())
        res = 0
        start = datetime.now()
        while start + timedelta(seconds=timeout) > datetime.now():
            if self.ser.inWaiting():
                time.sleep(0.3)
                rec_buff = self.ser.read(self.ser.inWaiting())
                if rec_buff != '':
                    if back is not None and back in rec_buff.decode():
                        res = 1
                        if returnasstring:
                            res = rec_buff.decode()
                        break
                    else:
                        res = 0
                else:
                    res = 0
            time.sleep(0.3)
        return res
