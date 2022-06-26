import json
import sys
import os
# import paho.mqtt.client as mqtt
import time
import ftpModules
import pidModules
import tarfile
import subprocess


# 2.---发送mqtt报文1-版本信息--

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("连接成功")
#         print("Connected with result code " + str(rc))
#     # 02, AI校时订阅
#     client.subscribe("AI/set/time", 0)
#     client.subscribe("AI/response/images", 0)
#
#
# # 一旦订阅到消息，回调此方法
# def on_message(client, userdata, msg):
#     print(msg)
#     print(msg.topic + " " + str(msg.payload))
#     # return msg.payload
#     msg_result = json.loads(msg.payload)
#     if msg.topic == "AI/set/time":
#         # 设置时间戳
#         timestamp = msg_result['timestamp']
#         print('当前时间戳' + timestamp)
#
#         # 设置AI芯片时间
#         try:
#             # 格式转换
#             time_result = timestamp
#             timeArray = time.strptime(time_result, "%Y%m%dT%H%M%S")
#             otherStyleTime = time.strftime("%Y%m%d %H:%M:%S", timeArray)
#             # print(otherStyleTime)
#
#             # 时间分割
#             time_date = otherStyleTime[:8]
#             time_time = otherStyleTime[9:]
#             print(time_date)
#             print(time_time)
#
#             # 设置时间
#             # 设置日期
#             password = 'Mind@123'
#             command_date = 'sudo date -s ' + '\"' + time_date + ' ' + time_time + '\"'
#             os.system('echo %s | sudo -S %s' % (password, command_date))
#             # command_time
#             # # os.system('sudo date -s ' + time_date)
#             # os.system('sudo date -s ' + time_time)
#             # 测试
#             # print('Now: ')
#             # os.system('date')
#         except Exception as e:
#             print(e)
#
#         #  timestamp”:“2021 11 01 T 12 31 0
#         # datetime_str = timestamp
#         # datetime_object = datetime.strptime(datetime_str, '%Y/%m/%dT%H%M%S')
#         #
#         # print(type(datetime_object))
#         # print(datetime_object)
#     elif msg.topic == 'AI/response/images':
#         # 8. ---接受mqtt报文2响应--上传图片对方返回的结果
#         # if msg_result['status']:
#         # print('图片上传结果' + msg_result['status'])
#         print(msg_result)
#
#
# def on_subscribe(client, userdata, mid, granted_qos):
#     print("消息发送成功")
#
#
# client = mqtt.Client(protocol=3)
# client.username_pw_set("admin", "password")
# client.on_connect = on_connect
# client.on_message = on_message
# client.on_subscribe = on_subscribe
# client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
#
#
# client.subscribe("AI/set/time", 0)
# client.subscribe("AI/response/images", 0)
# time.sleep(1)


def ftpfile(img_name, alarm_type):
    print('pubImg start')
    # client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
    try:
        # 7. ---发送mqtt报文2，通知图片处理结果---
        now = int(time.time())  # ->这是时间戳

        # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"

        timeArray = time.localtime(now)

        otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
        img_data = {
            "timestamp": otherStyleTime,
            "filename": img_name,
            "cameralID": "0",
            "type": alarm_type
        }
        sensor_data_img = json.dumps(img_data)

        print('ftpFile start')
        # ftp_status = os.system('ncftpput -C 172.17.0.1 ./out/' + img_name + ' ./images/' + img_name)
        # ftp_status = os.system('ncftpput -C 172.17.0.1 ./out/' + img_name + ' images/' + img_name)
        ftp_status = 0
        time.sleep(1)
        if ftp_status == 0:
            print('ftp 上传 OK!')
            # fire_1efcea23fa4a409e8056bd0b6e96c822.jpg
            # client.publish(topic="AI/notify/images", payload=sensor_data_img, qos=0)
            print(sensor_data_img)
            # mosquitto_pub -h 172.17.0.1 -t AI/notify/images -m "{\"timestamp\": \"20220406T203510\", \"filename\": \"fire_1efcea23fa4a409e8056bd0b6e96c822.jpg\", \"cameraID\": 1}"
            # os.system('')
            return True
    except Exception as e:
        print('ftp 上传 失败！')
        print(e)
        return False


def sendMsg(filename, coordinate, tagName):
    # client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
    now = int(time.time())  # ->这是时间戳
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
    alarm_data = {
        "file_name": filename,
        "photo_time": otherStyleTime,
        "cameraID": 0,
        "if_alarm": 1,
        "result": [
            {
                "coordinate": coordinate,
                "tagName": tagName

            }
        ]
    }
    sensor_data_alarm = json.dumps(alarm_data)
    print('发送告警信息')
    print('sensor_data_alarm')
    
    # client.publish(topic="AI/notify/alarm", payload=sensor_data_alarm, qos=0)
# 6.---ftp上传待处理的图片---

# ncftpput-C172.17.0.1gateway.jpgimages/gateway.jpg


# client.loop_forever()
