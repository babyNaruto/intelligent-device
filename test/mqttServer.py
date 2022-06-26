import time
import json
import paho.mqtt.client as mqtt


# 一旦连接成功，回调此方法
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
        print("Connected with result code " + str(rc))
    # 02, AI校时订阅

    client.subscribe("app/notify/info", 0)

    # 订阅频道

    # data = json.loads(test_time)
    # print(data)

    # 04,图片响应结果订阅
    client.subscribe("AI/notify/images", 0)

    # 05,应用和模型升级订阅
    client.subscribe("AI/response/upgrade", 0)
    # 告警信息订阅
    client.subscribe("AI/notify/alarm", 0)


# 一旦订阅到消息，回调此方法
def on_message(client, userdata, msg):
    print('收到')
    # print(msg)
    print(msg.topic + " " + str(msg.payload))
    # print(msg.payload)
    # return msg.payload


client = mqtt.Client(protocol=3)
client.username_pw_set("admin", "password")
client.on_connect = on_connect
client.on_message = on_message
client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
time.sleep(1)

# client.subscribe("AI/set/time", 0)

client.loop_forever()
