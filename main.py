import json
import subprocess
import sys
import os
#os.system('. /home/HwHiAiUser/Ascend/ascend-toolkit/set_env.sh')
sys.path.append("/home/HwHiAiUser/.local/lib/python3.7/site-packages")
import paho.mqtt.client as mqtt
import time
import ftpModules
from datetime import datetime
import threading
import queue
from threading import Timer

import subprocess
sys.path.append("../MindStudio-WorkSpace/samples-v0.5.0/python/common")
sys.path.append("../")

import numpy as np
import cv2 as cv
import cv2
from PIL import Image
# from check_all import *
from check_all import Check_all
import atlas_utils.constants as const
from atlas_utils.acl_model import Model
from atlas_utils.acl_resource import AclResource
from main3 import ftpfile

envpath = '/home/HwHiAiUser/.local/lib/python3.7/site-packages/cv2/qt/plugins/platforms'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath

CAMERA_URL = "rtsp://admin:3204wangbo@192.168.1.64/Streaming/Channels/2"
INPUT_DIR = './data/'
OUTPUT_DIR = './out/'
MODEL_PATH = "./model/peidianfang.om"
labels = ["person", "fire", "smoke", "tobacco", "hat", "armour", "fence"]
MODEL_WIDTH = 416
MODEL_HEIGHT = 416
class_num = 7
stride_list = [8, 16, 32]
anchors_1 = np.array([[10, 13], [16, 30], [33, 23]]) / stride_list[0]
anchors_2 = np.array([[30, 61], [62, 45], [59, 119]]) / stride_list[1]
anchors_3 = np.array([[116, 90], [156, 198], [373, 326]]) / stride_list[2]
anchor_list = [anchors_1, anchors_2, anchors_3]

conf_threshold = 0.3
iou_threshold = 0.3

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0)]

check = Check_all()


def preprocess(image):

    img_h = image.size[1]
    img_w = image.size[0]
    net_h = MODEL_HEIGHT
    net_w = MODEL_WIDTH

    scale = min(float(net_w) / float(img_w), float(net_h) / float(img_h))
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    shift_x = (net_w - new_w) // 2
    shift_y = (net_h - new_h) // 2
    shift_x_ratio = (net_w - new_w) / 2.0 / net_w
    shift_y_ratio = (net_h - new_h) / 2.0 / net_h

    image_ = image.resize((new_w, new_h))
    new_image = np.zeros((net_h, net_w, 3), np.uint8)
    new_image[shift_y: new_h + shift_y, shift_x: new_w + shift_x, :] = np.array(image_)
    new_image = new_image.astype(np.float32)
    new_image = new_image / 255

    return new_image, image


def overlap(x1, x2, x3, x4):
    left = max(x1, x3)
    right = min(x2, x4)
    return right - left


def cal_iou(box, truth):
    w = overlap(box[0], box[2], truth[0], truth[2])
    h = overlap(box[1], box[3], truth[1], truth[3])
    if w <= 0 or h <= 0:
        return 0
    inter_area = w * h
    union_area = (box[2] - box[0]) * (box[3] - box[1]) + (truth[2] - truth[0]) * (truth[3] - truth[1]) - inter_area
    return inter_area * 1.0 / union_area


def apply_nms(all_boxes, thres):
    res = []

    for cls in range(class_num):
        cls_bboxes = all_boxes[cls]
        sorted_boxes = sorted(cls_bboxes, key=lambda d: d[5])[::-1]

        p = dict()
        for i in range(len(sorted_boxes)):
            if i in p:
                continue

            truth = sorted_boxes[i]
            for j in range(i + 1, len(sorted_boxes)):
                if j in p:
                    continue
                box = sorted_boxes[j]
                iou = cal_iou(box, truth)
                if iou >= thres:
                    p[j] = 1

        for i in range(len(sorted_boxes)):
            if i not in p:
                res.append(sorted_boxes[i])
    return res


def decode_bbox(conv_output, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio):
    def _sigmoid(x):
        s = 1 / (1 + np.exp(-x))
        return s

    h, w, _ = conv_output.shape

    pred = conv_output.reshape((h * w, 3, 5 + class_num))

    pred[..., 4:] = _sigmoid(pred[..., 4:])
    pred[..., 0] = (_sigmoid(pred[..., 0]) + np.tile(range(w), (3, h)).transpose((1, 0))) / w
    pred[..., 1] = (_sigmoid(pred[..., 1]) + np.tile(np.repeat(range(h), w), (3, 1)).transpose((1, 0))) / h
    pred[..., 2] = np.exp(pred[..., 2]) * anchors[:, 0:1].transpose((1, 0)) / w
    pred[..., 3] = np.exp(pred[..., 3]) * anchors[:, 1:2].transpose((1, 0)) / h

    bbox = np.zeros((h * w, 3, 4))
    bbox[..., 0] = np.maximum((pred[..., 0] - pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, 0)  # x_min
    bbox[..., 1] = np.maximum((pred[..., 1] - pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, 0)  # y_min
    bbox[..., 2] = np.minimum((pred[..., 0] + pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, img_w)  # x_max
    bbox[..., 3] = np.minimum((pred[..., 1] + pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, img_h)  # y_max

    pred[..., :4] = bbox
    pred = pred.reshape((-1, 5 + class_num))
    pred[:, 4] = pred[:, 4] * pred[:, 5:].max(1)
    pred = pred[pred[:, 4] >= conf_threshold]
    pred[:, 5] = np.argmax(pred[:, 5:], axis=-1)

    all_boxes = [[] for ix in range(class_num)]
    for ix in range(pred.shape[0]):
        box = [int(pred[ix, iy]) for iy in range(4)]
        box.append(int(pred[ix, 5]))
        box.append(pred[ix, 4])
        all_boxes[box[4] - 1].append(box)

    return all_boxes


def convert_labels(label_list):
    if isinstance(label_list, np.ndarray):
        label_list = label_list.tolist()
        label_names = [labels[int(index)] for index in label_list]
    return label_names


def post_process(infer_output, origin_img):
    # print("post process")
    result_return = dict()
    img_h = origin_img.size[1]
    img_w = origin_img.size[0]

    scale = min(float(MODEL_WIDTH) / float(img_w), float(MODEL_HEIGHT) / float(img_h))
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    shift_x_ratio = (MODEL_WIDTH - new_w) / 2.0 / MODEL_WIDTH
    shift_y_ratio = (MODEL_HEIGHT - new_h) / 2.0 / MODEL_HEIGHT
    class_number = len(labels)
    num_channel = 3 * (class_number + 5)
    x_scale = MODEL_WIDTH / float(new_w)
    y_scale = MODEL_HEIGHT / float(new_h)
    all_boxes = [[] for ix in range(class_number)]
    for ix in range(3):
        pred = infer_output[2 - ix].reshape((MODEL_HEIGHT // stride_list[ix], \
                                             MODEL_WIDTH // stride_list[ix], num_channel))
        anchors = anchor_list[ix]
        boxes = decode_bbox(pred, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio)
        all_boxes = [all_boxes[iy] + boxes[iy] for iy in range(class_number)]

    res = apply_nms(all_boxes, iou_threshold)
    if not res:
        result_return['detection_classes'] = []
        result_return['detection_boxes'] = []
        result_return['detection_scores'] = []
        return result_return
    else:
        new_res = np.array(res)
        picked_boxes = new_res[:, 0:4]
        picked_boxes = picked_boxes[:, [1, 0, 3, 2]]
        picked_classes = convert_labels(new_res[:, 4])
        picked_score = new_res[:, 5]
        result_return['detection_classes'] = picked_classes
        result_return['detection_boxes'] = picked_boxes.tolist()
        result_return['detection_scores'] = picked_score.tolist()
        return result_return


# 2.---??????mqtt??????1-????????????--

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("????????????")
        print("Connected with result code " + str(rc))
    # 02, AI????????????
    client.subscribe("AI/set/time", 0)
    client.subscribe("AI/response/images", 0)


# ???????????????????????????????????????
def on_message(client, userdata, msg):
    print(msg)
    print(msg.topic + " " + str(msg.payload))
    # return msg.payload
    msg_result = json.loads(msg.payload)
    if msg.topic == "AI/set/time":
        # ???????????????
        timestamp = msg_result['timestamp']
        print('???????????????' + timestamp)
        
        # ??????AI????????????
        try:
            # ????????????
            time_result = timestamp
            timeArray = time.strptime(time_result, "%Y%m%dT%H%M%S")
            otherStyleTime = time.strftime("%Y%m%d %H:%M:%S", timeArray)
            # print(otherStyleTime)

            # ????????????
            time_date = otherStyleTime[:8]
            time_time = otherStyleTime[9:]
            print(time_date)
            print(time_time)

            # ????????????
            # ????????????
            password = 'Mind@123'
            command_date = 'sudo date -s ' + '"' + time_date + ' ' + time_time + '"'
            # os.system('echo %s | sudo -S %s' % (password, command_date))
            os.system(command_date)
            # command_time
            # # os.system('sudo date -s ' + time_date)
            # os.system('sudo date -s ' + time_time)
            # ??????
            # print('Now: ')
            # os.system('date')
        except Exception as e:
            print(e)
            
        #  timestamp???:???2021 11 01 T 12 31 0
        # datetime_str = timestamp
        # datetime_object = datetime.strptime(datetime_str, '%Y/%m/%dT%H%M%S')
        #
        # print(type(datetime_object))
        # print(datetime_object)
    elif msg.topic == 'AI/response/images':
        # 8. ---??????mqtt??????2??????--?????????????????????????????????
        # if msg_result['status']:
        # print('??????????????????' + msg_result['status'])
        print(msg_result)


def on_subscribe(client, userdata, mid, granted_qos):
    print("??????????????????")


def sendTimeMsg(filename):
    client.connect(host="172.17.0.1", port=1883, keepalive=60)  # ????????????
    now = int(time.time())  # ->???????????????
    # ???????????????????????????,???:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
    alarm_data = {
        "file_name": filename,
        "photo_time": otherStyleTime,
        "cameraID": 0,
        "if_alarm": 0,
        "result": [
            {
                "coordinate": '',
                "tagName": '??????'

            }
        ]
    }
    sensor_data_alarm = json.dumps(alarm_data)
    print('??????????????????')
    # client.connect(host="172.17.0.1", port=1883, keepalive=60)
    client.publish(topic="AI/notify/alarm", payload=sensor_data_alarm, qos=0)
    


def time_ftp():
    
    url = CAMERA_URL
    # capture=cv2.VideoCapture("1.mp4")
    capture = cv2.VideoCapture(url)
    # capture = cv2.VideoCapture(0)
    # ???????????????
    ref, frame = capture.read()
    if not ref:
        print('fail')
    # ???????????????BGRtoRGB
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # ?????????Image
    # temp_image = Image.fromarray(np.uint8(frame))
    # ????????????
    
    time_img_name = 'Timing_transmission_' + str(round(time.time())) + '.jpg'
    cv2.imwrite('./out/' + time_img_name, frame)
    sendTimeMsg(time_img_name)
    flag = ftpfile(time_img_name, 'Timing_transmission')
    if flag:
        os.remove('./out/' + time_img_name)
    # cv2.destroyAllWindows()
    capture.release()
    t = Timer(3600, time_ftp)
    t.start()

# ???????????????
def time_main_info():
    client.connect(host="172.17.0.1", port=1883, keepalive=60)
    now = int(time.time())  # ->???????????????
    # ???????????????????????????,???:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
    pub_data = {
        "name": "AI-APP",
        "version": "v1.0",
        "timestamp": otherStyleTime
    }
    sensor_data_pub = json.dumps(pub_data)

    client.publish(topic="app/notify/info", payload=sensor_data_pub, qos=0)
    t = Timer(120, time_main_info)
    t.start()

def get_frame(img_queue,cap):
    t = 0
    while(True):
        ret, frame = cap.read()
        
        if img_queue.empty() and ret and time.time() -t > 0.5:
            img_queue.put(frame)
            t = time.time()
        else:
            # print('111111111')
            time.sleep(0.01)

# ??????????????????
# 1.---??????????????????---

print('??????????????????...')
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
# ACL resource initialization
acl_resource = AclResource()
acl_resource.init()
# load model
model = Model(MODEL_PATH)

client = mqtt.Client(protocol=3)
client.username_pw_set("admin", "password")
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host="172.17.0.1", port=1883, keepalive=60)  # ????????????


# os.system('nohup /usr/local/python3.7.5/bin/python3 /home/HwHiAiUser/mqtt/updateAI.py > /home/HwHiAiUser/mqtt/updateAI.log 2>&1 &')
# proc = subprocess.Popen('nohup /usr/local/python3.7.5/bin/python3 /home/HwHiAiUser/mqtt/updateAI.py > /home/HwHiAiUser/mqtt/updateAI.log 2>&1 &', shell=True)
os.system('sh start2.sh')
time.sleep(10)

client.subscribe("AI/set/time", 0)
client.subscribe("AI/response/images", 0)

# 2.1 mqtt??????1, AI????????????????????????

time_main_info()

# 3. ---??????????????????PID??????????????????---

# 3.1 ??????????????????PID
pid = os.getpid()
print('pid: ', pid)

# 3.2 ???pid??????????????????
f1 = open(file='ai_pid.txt', mode='w')
f1.write(pid.__str__())
f1.close()

# 4. ---?????????????????????---
# images_list = [os.path.join(INPUT_DIR, img)
               # for img in os.listdir(INPUT_DIR)
               # if os.path.splitext(img)[1] in const.IMG_EXT]
# Read images from the data directory one by one for reasoning


# for pic in images_list:
    # read image
# ????????????
os.system('sh start2.sh')
time.sleep(15)

time_ftp()
    
    
url = CAMERA_URL
# capture=cv2.VideoCapture("1.mp4")
capture = cv2.VideoCapture(url)
# capture = cv2.VideoCapture(0)
ref,frame=capture.read()


img_queue = queue.Queue(maxsize=1)
img_thread = threading.Thread(target=get_frame,args=(img_queue,capture ))
img_thread.setDaemon(True)
img_thread.start()




while(True):
    t1 = time.time()
    # ???????????????
    # ref,frame=capture.read()
    if not img_queue.empty():
        frame = img_queue.get()
    else:
        time.sleep(0.01)
        continue
    # ???????????????BGRtoRGB
    bgr_img = frame
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    # ?????????Image
    temp_image = Image.fromarray(np.uint8(frame))
    # ????????????
    # frame = cv2.imwrite("./test111.jpg", frame)
    
    # ?????????????????????????????????
    
    # preprocess
    data, orig = preprocess(temp_image)
    # Send into model inference
    result_list = model.execute([data, ])
    # Process inference results
    result_return = post_process(result_list, orig)

    # print("result = ", result_return)

    labels_temp = []
    confidents = []
    bboxs = []

    for i in range(len(result_return['detection_classes'])):
        box = result_return['detection_boxes'][i]
        class_name = result_return['detection_classes'][i]
        confidence = result_return['detection_scores'][i]
        # cv.rectangle(bgr_img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), colors[i % 6])
        labels_temp.append(class_name)
        confidents.append(confidence)
        temp_box = [max(0, int(b)) for b in box]
        bboxs.append(temp_box)

    # 5. ---????????????---
    check.check(bgr_img, bboxs, labels_temp, confidents)
    # time.sleep(0.25)
    # cv2.imshow('test', bgr_img)
    # if cv2.waitKey() == ord('q'):
    #     break
    # output_file = os.path.join(OUTPUT_DIR, "out_" + os.path.basename(pic))
    # print("output:%s" % output_file)
    # cv.imwrite(output_file, bgr_img)


# print("Execute end")

# time.sleep(5)
client.loop_forever()


