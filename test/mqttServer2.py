import json

import paho.mqtt.client as mqtt
import time
import sys


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("消息发送成功")


client = mqtt.Client(protocol=3)
client.username_pw_set("admin", "password")
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
time.sleep(1)

pub_data = {"timestamp": "20211101T123109", "timezone": "Asia/Shanghai"}

img_data = {"timestamp":"20211101T123515","filename":"gateway.jpg", "status":"OK"}

upgrade_data = {"timestamp": "20211102T103000", "filename": "main.tar.gz", "version": "1.0.0.1"}

# 发布MQTT信息
sensor_data_pub = json.dumps(pub_data)
sensor_data_img = json.dumps(img_data)
sensor_data_upgrade = json.dumps(upgrade_data)


# 01, AI模块应用信息发布
def sendMsg(data):
    client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
    client.publish(topic="app/notify/info", payload=data, qos=0)
    # client.loop_forever()


# client.publish(topic="AI/set/time", payload=sensor_data_pub, qos=0)
# 03, AI上传图片

# 上传图片

# client.publish(topic="AI/response/image", payload=sensor_data_img, qos=0)

# 06, AI模块升级结果发布

# 升级
client.publish(topic="AI/event/upgrade", payload=sensor_data_upgrade, qos=0)

time.sleep(5)

client.loop_forever()
