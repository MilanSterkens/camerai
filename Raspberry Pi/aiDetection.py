import device_patches       # Device specific patches for Jetson Nano (needs to be before importing cv2)

import cv2
import os
import sys, getopt
import signal
import time
from datetime import datetime
import schedule
from datetime import timedelta
from edge_impulse_linux.image import ImageImpulseRunner
from tracker import *

from databaseHelper import DatabaseHelper


class AiDetection:
    runner = None
    tracker = EuclideanDistTracker()

    ih = 480
    iw = 640
    center = int(iw / 4)
    line_p = int(ih / 4)
    line_position_1 = center - line_p
    line_position_2 = center
    line_position_3 = center + line_p
    line_d = 20
    line_1_r = line_position_1 + line_d
    line_1_l = line_position_1 - line_d
    line_2_r = line_position_2 + line_d
    line_2_l = line_position_2 - line_d
    line_3_r = line_position_3 + line_d
    line_3_l = line_position_3 - line_d

    # if you don't want to see a camera preview, set this to False
    show_camera = True

    def __init__(self, dbhelper: DatabaseHelper):
        if sys.platform == 'linux' and not os.environ.get('DISPLAY'):
            self.show_camera = False
        self.dbHelper = dbhelper
        self.main(sys.argv[1:])

    if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
        show_camera = False

    def now(self):
        return round(time.time() * 1000)

    def get_webcams(self):
        port_ids = []
        for port in range(5):
            print("Looking for a camera in port %s:" % port)
            camera = cv2.VideoCapture(port)
            if camera.isOpened():
                ret = camera.read()[0]
                if ret:
                    backendName = camera.getBackendName()
                    w = camera.get(3)
                    h = camera.get(4)
                    print("Camera %s (%s x %s) found in port %s " % (backendName, h, w, port))
                    port_ids.append(port)
                camera.release()
        return port_ids

    def sigint_handler(self, sig, frame):
        print('Interrupted')
        if self.runner:
            self.runner.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    def help(self):
        print(
            'python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

    def find_center(self, x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)
        cx = x + x1
        cy = y + y1
        return cx, cy

    # Function for vehicle speed
    stamp1_list = {}
    stamp2_list = {}
    stamp3_list = {}
    average_speed = []
    count_list = []

    # Distance in Meters
    frame_w = iw / 2
    distance_frame = 10
    distance_px = distance_frame / frame_w
    distance_1 = line_position_1 * distance_px
    distance_2 = line_position_2 * distance_px
    distance_3 = line_position_3 * distance_px
    print(distance_px, distance_1, distance_2, distance_3)

    def get_vehicle_type(self, type: str):
        if type == 'car':
            return 1
        elif type == 'truck':
            return 2
        elif type == 'bike':
            return 3
        else:
            return 4

    def vehicle_speed(self, box_id, img):
        x, y, w, h, id, index = box_id
        n = "timestamp" + str(id)
        # Find the center of the rectangle for detection
        center = self.find_center(x, y, w, h)

        ix, iy = center

        # Get time stamps
        # Stamp 1
        if (ix > self.line_1_l) and (ix < self.line_1_r):
            if n not in self.stamp1_list:
                now = datetime.now()
                time1 = [id, now, index, 1]
                self.stamp1_list[n] = time1
                print('Stamp 1')
                print(self.stamp1_list)
                if id not in self.count_list:
                    self.count_list.append(id)

        # Stamp 2
        if (ix > self.line_2_l) and (ix < self.line_2_r):
            if n not in self.stamp2_list:
                now = datetime.now()
                time2 = [id, now, index, 2]
                self.stamp2_list[n] = time2
                print('Stamp 2')
                print(self.stamp2_list)
                if id not in self.count_list:
                    self.count_list.append(id)

        # Stamp 3
        if (ix > self.line_3_l) and (ix < self.line_3_r):
            if n not in self.stamp3_list:
                now = datetime.now()
                time3 = [id, now, index, 3]
                self.stamp3_list[n] = time3
                print('Stamp 3')
                print(self.stamp3_list)
                if id not in self.count_list:
                    self.count_list.append(id)

        # Speed calculation
        if n in self.stamp1_list and n in self.stamp2_list:
            t1 = self.stamp1_list[n][1]
            t2 = self.stamp2_list[n][1]
            if t2 < t1:
                t1, t2 = t2, t1
            s = self.distance_2 - self.distance_1
            t = t2 - t1
            t = timedelta.total_seconds(t)
            v = (s / t) * 3.6
            print('speed: ' + str(v) + ' distance: ' + str(s) + ' time:' + str(t))
            if id not in self.average_speed:
                self.average_speed.append([id, index, v])
                self.dbHelper.insert_detection(self.get_vehicle_type(index), v)
        elif n in self.stamp2_list and n in self.stamp3_list:
            t1 = self.stamp2_list[n][1]
            t2 = self.stamp3_list[n][1]
            if t2 < t1:
                t1, t2 = t2, t1
            s = self.distance_3 - self.distance_2
            t = t2 - t1
            t = timedelta.total_seconds(t)
            v = (s / t) * 3.6
            print('speed: ' + str(v) + ' distance: ' + str(s) + ' time:' + str(t))
            if id not in self.average_speed:
                self.average_speed.append([id, index, v])
                self.dbHelper.insert_detection(self.get_vehicle_type(index), v)
        elif n in self.stamp3_list and n in self.stamp1_list:
            t1 = self.stamp1_list[n][1]
            t2 = self.stamp3_list[n][1]
            if t2 < t1:
                t1, t2 = t2, t1
            s = self.distance_3 - self.distance_1
            t = t2 - t1
            t = timedelta.total_seconds(t)
            v = (s / t) * 3.6
            print('speed: ' + str(v) + ' distance: ' + str(s) + ' time:' + str(t))
            if id not in self.average_speed:
                self.average_speed.append([id, index, v])
                print('detected: ' + index + ', speed: '+ str(v))
                self.dbHelper.insert_detection(self.get_vehicle_type(index), v)
        else:
            print('detected: ' + index + ', no speed')
            self.dbHelper.insert_detection(self.get_vehicle_type(index), 0)
        # Draw circle in the middle of the rectangle
        cv2.circle(img, center, 2, (0, 0, 255), -1)  # end here

    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv, "h", ["--help"])
        except getopt.GetoptError:
            help()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                help()
                sys.exit()

        if len(args) == 0:
            help()
            sys.exit(2)

        model = args[0]

        dir_path = os.path.dirname(os.path.realpath(__file__))
        modelfile = os.path.join(dir_path, model)

        print('MODEL: ' + modelfile)

        with ImageImpulseRunner(modelfile) as runner:
            try:
                model_info = runner.init()
                print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project'][
                    'name'] + '"')
                labels = model_info['model_parameters']['labels']
                if len(args) >= 2:
                    videoCaptureDeviceId = int(args[1])
                else:
                    port_ids = self.get_webcams()
                    if len(port_ids) == 0:
                        raise Exception('Cannot find any webcams')
                    if len(args) <= 1 < len(port_ids):
                        raise Exception(
                            "Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                    videoCaptureDeviceId = int(port_ids[0])

                camera = cv2.VideoCapture(videoCaptureDeviceId)
                ret = camera.read()[0]
                if ret:
                    backendName = camera.getBackendName()
                    w = camera.get(3)
                    h = camera.get(4)
                    print("Camera %s (%s x %s) in port %s selected." % (backendName, h, w, videoCaptureDeviceId))
                    camera.release()
                else:
                    raise Exception("Couldn't initialize selected camera.")

                next_frame = 0  # limit to ~10 fps here

                for res, img in runner.classifier(videoCaptureDeviceId):
                    if next_frame > self.now():
                        time.sleep((next_frame - self.now()) / 1000)

                    schedule.run_pending()

                    detection = []

                    # print('classification runner response', res)

                    if "classification" in res["result"].keys():
                        print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                        for label in labels:
                            score = res['result']['classification'][label]
                            print('%s: %.2f\t' % (label, score), end='')
                        print('', flush=True)

                    elif "bounding_boxes" in res["result"].keys():
                        print('Found %d bounding boxes (%d ms.)' % (
                        len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                        for bb in res["result"]["bounding_boxes"]:
                            detection.append([bb['x'], bb['y'], bb['width'], bb['height'], bb['label']])
                            boxes_ids = self.tracker.update(detection)
                            for box_id in boxes_ids:
                                x, y, w, h, id, index = box_id
                                self.vehicle_speed(box_id, img)
                                cv2.putText(img, f'{id} {self.tracker.id_count}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                            (255, 0, 0), 1)
                                print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], x, y, w, h))
                                print(f'{id}')
                                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)

                    # Draw the crossing lines
                    # line 1
                    cv2.line(img, (self.line_position_1, 0), (self.line_position_1, self.ih), (255, 0, 255), 1)
                    cv2.line(img, (self.line_1_l, 0), (self.line_1_l, self.ih), (0, 0, 255), 1)
                    cv2.line(img, (self.line_1_r, 0), (self.line_1_r, self.ih), (0, 0, 255), 1)

                    # line 2
                    cv2.line(img, (self.line_position_2, 0), (self.line_position_2, self.ih), (255, 0, 255), 1)
                    cv2.line(img, (self.line_2_l, 0), (self.line_2_l, self.ih), (0, 0, 255), 1)
                    cv2.line(img, (self.line_2_r, 0), (self.line_2_r, self.ih), (0, 0, 255), 1)

                    # line 3
                    cv2.line(img, (self.line_position_3, 0), (self.line_position_3, self.ih), (255, 0, 255), 1)
                    cv2.line(img, (self.line_3_l, 0), (self.line_3_l, self.ih), (0, 0, 255), 1)
                    cv2.line(img, (self.line_3_r, 0), (self.line_3_r, self.ih), (0, 0, 255), 1)

                    if (self.show_camera):
                        cv2.imshow('edgeimpulse', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                        if cv2.waitKey(1) == ord('q'):
                            break

                    next_frame = self.now() + 100
            finally:
                if self.runner:
                    self.runner.stop()