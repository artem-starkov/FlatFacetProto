import os
from app import app
from abc import abstractmethod
import math
import numpy as np
import time
import serial
from app import enums
from app.utils.prototype_exceptions import *


class PrototypeDataReceiver:
    def __int__(self, run_id):
        self._data_file = os.path.join(app.root_path, 'data', f'data-{run_id}.txt')
        self._threshold_log = os.path.join(app.root_path, 'logs', 'threshold_logs', f'thr_log-{run_id}.txt')

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    def _sleep(self):
        time.sleep(1)

    def _get_threshold_array(self, omm_num):
        arr = [0] * (omm_num * 2)
        shape_length = int(omm_num / 2) - int(omm_num / 10)
        left_arr = np.linspace(math.log(app.config['THRESHOLD_MIN']),
                               math.log(app.config['THRESHOLD_MAX']),
                               shape_length)
        right_arr = np.linspace(math.log(app.config['THRESHOLD_MAX']),
                                math.log(app.config['THRESHOLD_MIN']),
                                shape_length)
        j = 0
        left_coeff = app.config['LEFT_THRESHOLD_COEFF']
        for i in range(int(omm_num/2) - int(omm_num / 10)):
            arr[i] = left_coeff * math.exp(left_arr[j])
            j += 1
        for i in range(int(omm_num/2) - int(omm_num / 10), int(omm_num/2) + int(omm_num / 10)):
            arr[i] = left_coeff * app.config['THRESHOLD_MAX']
        j = 0
        for i in range(int(omm_num/2) + int(omm_num / 10), omm_num):
            arr[i] = left_coeff * math.exp(right_arr[j])
            j += 1

        j = 0
        for i in range(omm_num, omm_num + int(omm_num / 2) - int(omm_num / 10)):
            arr[i] = math.exp(left_arr[j])
            j += 1
        for i in range(omm_num + int(omm_num / 2) - int(omm_num / 10), omm_num + int(omm_num / 2) + int(omm_num / 10)):
            arr[i] = app.config['THRESHOLD_MAX']
        j = 0
        for i in range(omm_num + int(omm_num / 2) + int(omm_num / 10), 2* omm_num):
            arr[i] = math.exp(right_arr[j])
            j += 1
        return arr

    def _make_mask(self, left_arr, right_arr):
        if app.config['EYE_ORDER'] == enums.Order.RightLeft:
            left_arr, right_arr = right_arr, left_arr
        left1, left2, right1, right2 = 318, 338, 338, 318
        orig_length = 82
        diff = int((len(left_arr) - orig_length) / 2)
        precedent = [0] * (left1 - diff) + left_arr + [0] * (left2 - diff) + [0] * (right1 - diff) + right_arr + [0] * (right2 - diff)
        return precedent

    def _current_precedent(self, bytes_, threshold=None):
        if app.config['DATA_SOURCE'] == enums.DataSource.Device:
            str_bytes = [str(x) for x in bytes_]
            with open(self._data_file, 'a') as file:
                file.write(','.join(str_bytes) + '\n')
        try:
            frame_num = bytes_[4]
            omm_num = bytes_[3]
            brights = bytes_[5:-1]
        except:
            raise InputException(bytes_)
        s_arr = []
        j = 0
        threshold_array = self._get_threshold_array(omm_num)
        left, right = [0] * omm_num, [0] * omm_num
        threshold_static = app.config['THRESHOLD_MAX']
        left_coeff = app.config['LEFT_THRESHOLD_COEFF']
        for i in range(omm_num * 2):
            try:
                s = brights[j] * pow(2, 16) + brights[j + 1] * pow(2, 8) + brights[j + 2]
            except:
                raise BrightsException(omm_num, brights)
            j += 3
            s_arr.append(s)
            cur_right_threshold = threshold_static if app.config['THRESHOLD_MODE'] == enums.ThresholdMode.Static \
                else threshold_array[i]
            cur_left_threshold = left_coeff * threshold_static if app.config['THRESHOLD_MODE'] == enums.ThresholdMode.Static \
                else threshold_array[i]
            if threshold:
                cur_left_threshold, cur_right_threshold = threshold, threshold
            if i < omm_num and s > cur_left_threshold:
                left[i] = 1
            if i >= omm_num and s > cur_right_threshold:
                right[i - omm_num] = 1
            # with open(self._threshold_log, 'a') as file:
            #     file.write(f'{cur_left_threshold}\t{cur_right_threshold}\t')

        if bytes_[6 * omm_num + 5] == sum(bytes_[5:6 * omm_num + 5]) % 256:
            precedent = self._make_mask(left, right)
            app.logger.info(f'Frame number: {frame_num}, brights:{brights}, mask: {s_arr}')
        else:
            precedent = [0] * 1476
            app.logger.info(f' something wrong with control sum: {frame_num}, brights:{brights}, mask: {s_arr}')
        print(len(s_arr), 'zeros' if sum(precedent) <= 2 else 'oks')
        print('------ ', s_arr)
        print('sorted ', sorted(s_arr)[::-1])
        return precedent


class PrototypeFileReceiver(PrototypeDataReceiver):
    def __init__(self, run_id):
        super().__init__()
        self._data_file = os.path.join(app.root_path, 'data', f'data-{run_id}.txt')
        self._lines = []
        self._threshold_log = os.path.join(app.root_path, 'logs', 'threshold_logs', f'thr_log-{run_id}.txt')
        # with open(self._threshold_log, 'w') as file:
        #     file.write('Threshold_left\tThreshold_right\tr\tfi\n')

    def initialize(self):
        filename = os.path.join(app.root_path, 'data', app.config['DATA_FILE'])
        with open(filename) as file:
            self._lines = file.readlines()

    def get_data(self, threshold=None):
        app.logger.info(f'Started stream from file {app.config["DATA_FILE"]}.')
        for i,line in enumerate(self._lines):
            bytes_ = list(map(int, line.split(',')))
            yield self._current_precedent(bytes_, threshold)
            if threshold:
                yield self._current_precedent(bytes_, threshold), threshold
                threshold += 1000
            else:
                yield self._current_precedent(bytes_, threshold)
            self._sleep()


class PrototypeDeviceReceiver(PrototypeDataReceiver):
    def __init__(self, run_id):
        super().__init__()
        self._data_file = os.path.join(app.root_path, 'data', f'data-{run_id}.txt')
        self._threshold_log = os.path.join(app.root_path, 'logs', 'threshold_logs', f'thr_log-{run_id}.txt')
        # with open(self._threshold_log, 'w') as file:
        #     file.write('Threshold_left\tThreshold_right\tr\tfi\n')
        self._ser = None

    def initialize(self):
        self._ser = serial.Serial(app.config["DATA_PORT"], app.config["BAUD_RATE"])
        self._ser.flushInput()
        self._ser.flushOutput()

    def get_data(self, threshold=None):
        app.logger.info(f'Started stream from port {app.config["DATA_PORT"]}. Threshold: threshold')
        while True:
            if app.config['PROTOCOL_MODE'] == enums.ProtocolType.Old:
                data = (5).to_bytes(1, byteorder='little')
                self._ser.write(data)
            else:
                data = bytes([243, 211, 195, 3, 0, 0, 0, 0])
                self._ser.write(data)
                #time.sleep(0.001)

                data = bytes([243, 211, 195, 4, 0, 2, 87, 89])
                self._ser.write(data)
                #time.sleep(0.001)

                data = bytes([243, 211, 195, 8, 0, 0, 1, 1])
                self._ser.write(data)
                #time.sleep(0.001)
            received_data = self._ser.read()
            time.sleep(0.001)
            data_left = self._ser.inWaiting()
            received_data += self._ser.read(data_left)
            self._ser.flushInput()
            self._ser.flushOutput()
            bytes_ = list(bytearray(received_data))
            if threshold:
                yield self._current_precedent(bytes_, threshold), threshold
                threshold += 1000
            else:
                yield self._current_precedent(bytes_, threshold)
            self._sleep()
