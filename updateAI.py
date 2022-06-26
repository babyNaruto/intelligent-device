import time
time.sleep(60)
# import paho.mqtt.client as mqtt
import ftpModules
import pidModules
import os
import tarfile
import subprocess
import json
from threading import Timer
import sys
import psutil
import signal
import shutil

P_updateAI = psutil.pids()
for pid_u in P_updateAI:
    try:
        p_info = psutil.Process(pid_u).cmdline()
    except:
        continue
    if ('/home/HwHiAiUser/mqtt/updateAI.py' in p_info) and pid_u != os.getpid():
        sys.exit()


sys.path.append("/home/HwHiAiUser/.local/lib/python3.7/site-packages")
import paho.mqtt.client as mqtt
sys.path.append("../MindStudio-WorkSpace/samples-v0.5.0/python/common")
sys.path.append("../")
envpath = '/home/HwHiAiUser/.local/lib/python3.7/site-packages/cv2/qt/plugins/platforms'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath
CAMERA_URL = "rtsp://admin:3204wangbo@192.168.1.64/Streaming/Channels/2"
INPUT_DIR = './data/'
OUTPUT_DIR = './out/'
MODEL_PATH = "./model/peidianfang.om"

# import paho.mqtt.client as mqtt


# from datetime import datetime


# sys.path.append("../MindStudio-WorkSpace/samples-v0.5.0/python/common")
# sys.path.append("../")
#
# import numpy as np
# import cv2 as cv
# # import cv2
# from PIL import Image
# # from check_all import *
# from check_all import Check_all
# import atlas_utils.constants as const
# from atlas_utils.acl_model import Model
# from atlas_utils.acl_resource import AclResource
#
# envpath = '/home/HwHiAiUser/.local/lib/python3.7/site-packages/cv2/qt/plugins/platforms'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath

def update_result(filename):
    # 获得当前时间时间戳

    now = int(time.time())  # ->这是时间戳

    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"

    timeArray = time.localtime(now)

    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
    # now = datetime.datetime.now()
    # otherStyleTime = now.strftime("%Y%m%dT%H:%M:%S")
    # print(otherStyleTime)
    upgrade_data = {
        "timestamp": otherStyleTime,
        "filename": filename,
        "status": "Error"
    }
    return upgrade_data


# 一旦连接成功，回调此方法
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
        print("Connected with result code " + str(rc))
        # 1.等待模型更新报文
        client.subscribe("AI/event/upgrade", 0)
        client.subscribe("AI/set/time", 0)
        client.subscribe("AI/response/images", 0)


# 一旦订阅到消息，回调此方法
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == 'AI/event/upgrade':

        # 2.接收模型更新报文
        upgrade_result = json.loads(msg.payload)
        filename = upgrade_result['filename']
        # filedir = './' + filename

        # 3.下载模型更新文件
        # ncftpget -C 172.17.0.1 update/A200_sw.tar.gz new.tar.gz

        try:
            # ftp = ftpModules.myFtp('172.17.0.1')
            # ftp.Login('FTP', 'FTP')  # 登录，如果匿名登录则用空串代替即可
            # ftp_status = ftp.DownLoadFile(filedir, '/data/share/update/' + filename)
            print('模型更新文件下载....')
            # os.system('ncftpget -C 172.17.0.1 ./' + filename + ' ./model' + filename)
            
            os.system('ncftpget -C 172.17.0.1  update/' + filename + ' ./update/' + filename)

            # print('模型更新文件下载')
            # 4.替换模型文件
            # 备份
            # os.system('cp model/peidianfang.om model/peidianfang.om.bak')
            # print('模型备份成功')
            
            
            
            
            # ----解包到路径-----
            # tar = tarfile.open('./' + filename)
            # tar = tarfile.open('./model/' + filename)
            # names = tar.getnames()
            # for name in names:
                # tar.extract(name, path='./')
                # tar.extract(name, path='./model/')
            # print('解包成功')
            # tar.close()
            
            # =======模块备份和替换=========
            update_file = ['updateAI.py', 'main.py', 'main_back.py', 'check_all.py', 'peidianfang.om', 'main3.py', 'config.json']
            
            update_path = {
                'updateAI.py': './',
                'main.py': './',
                'main_back.py': './',
                'check_all.py': './',
                'peidianfang.om': './model/',
                'main3.py': './',
                'config.json': './'
            
            }


            tar = tarfile.open('./update/' + filename)
            names = tar.getnames()
        
            for name in names:
                if name in update_file:
                    shutil.copyfile(update_path[name] + name, './backup/' + name + '.back')
                    print('模型%s已备份' % name)
                    tar.extract(name, path=update_path[name])
                    print('模型文件%s已替换' % name)
                    
            tar.close()
            
            
            
            
            



            # 5.杀死智能分析进程
            # 5.1 读取pid
            f1 = open(file='ai_pid.txt', mode='r')
            pid = f1.read()
            f1.close()
            # pidModules.kill(pid)
            # window系统测试
            if os.name == 'posix':
                # Windows系统
                # cmd = 'taskkill /pid ' + str(pid) + ' /f'
                # Linux系统
                cmd = 'kill ' + str(pid)

                os.system(cmd)
                print(pid, 'killed')

                # 6.启动智能分析
                # try:
                print('重新启动算法')
                # proc =  os.system('python main.py')
                os.system('sh start1.sh')
                # os.system('nohup /usr/local/python3.7.5/bin/python3 /home/HwHiAiUser/mqtt/main.py > /home/HwHiAiUser/mqtt/main.log 2>&1 &')
                # proc = subprocess.Popen('. ~/Ascend/ascend-toolkit/set_env.sh && python3 main.py', shell=True)

                # 等待算法启动
                time.sleep(60)
                # 再次读取pid
                f1 = open(file='ai_pid.txt', mode='r')
                pid2 = f1.read()
                f1.close()
                # 无报错说明进程存在
                main_pid = psutil.pids()
                
                if int(pid2)  in main_pid:
                
                # os.kill(int(pid2), 0)
                    print('算法已成功运行')
    
                    # 7.更新结果--成功！
                    # now = datetime.datetime.now()
                    # otherStyleTime = now.strftime("%Y%m%dT%H%M%S")
                    now = int(time.time())  # ->这是时间戳
                    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
                    timeArray = time.localtime(now)
                    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
                    print('算法更新完成时间：' + otherStyleTime)
                    upgrade_data = {
                        "timestamp": otherStyleTime,
                        "filename": filename,
                        "status": "OK"
                    }
                    sensor_data_upgrade = json.dumps(upgrade_data)
                    client.publish(topic="AI/response/upgrade", payload=sensor_data_upgrade, qos=0)
                    # proc = subprocess.Popen('. ~/Ascend/ascend-toolkit/set_env.sh && python3 updateAI.py', shell=True)
        # 更新失败
        except Exception as e:
            print(e)
            sensor_data_upgrade = json.dumps(update_result(filename))
            client.publish(topic="AI/response/upgrade", payload=sensor_data_upgrade, qos=0)



    elif msg.topic == "AI/set/time":

        msg_result = json.loads(msg.payload)
        # 设置时间戳
        timestamp = msg_result['timestamp']
        print('当前时间戳' + timestamp)
        # 设置AI芯片时间
        try:
            # 格式转换
            time_result = timestamp
            timeArray = time.strptime(time_result, "%Y%m%dT%H%M%S")
            otherStyleTime = time.strftime("%Y%m%d %H:%M:%S", timeArray)
            # print(otherStyleTime)

            # 时间分割
            time_date = otherStyleTime[:8]
            time_time = otherStyleTime[9:]
            print(time_date)
            print(time_time)

            # 设置时间
            # 设置日期
            password = 'Mind@123'
            command_date = 'sudo date -s ' + '"' + time_date + ' ' + time_time + '"'
            # os.system('echo %s | sudo -S %s' % (password, command_date))
            os.system(command_date)
            # command_time
            # # os.system('sudo date -s ' + time_date)
            # os.system('sudo date -s ' + time_time)
            # 测试
            # print('Now: ')
            # os.system('date')
        except Exception as e:
            print(e)


    elif msg.topic == 'AI/response/images':
        msg_result = json.loads(msg.payload)
        # 8. ---接受mqtt报文2响应--上传图片对方返回的结果
        # if msg_result['status']:
        # print('图片上传结果' + msg_result['status'])
        print(msg_result)

def checkprocess():
    pl = psutil.pids()
    try:
        
        f1 = open(file='ai_pid.txt', mode='r')
        pid3 = f1.read()
        f1.close()
        if int(pid3) not in pl:
            # print('main存在')
            os.system('sh start1.sh')
    
        for pid in pl:
            if ('/home/HwHiAiUser/mqtt/main.py' in psutil.Process(pid).cmdline() or '/home/HwHiAiUser/mqtt/main_back.py' in psutil.Process(pid).cmdline()) and pid != int(pid3):
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(e)
        
    t = Timer(120, checkprocess)
    t.start()



client = mqtt.Client(protocol=3)
client.username_pw_set("admin", "password")
client.on_connect = on_connect
client.on_message = on_message
client.connect(host="172.17.0.1", port=1883, keepalive=60)  # 订阅频道
# os.system('sh start.sh')
time.sleep(1)


# 2 mqtt报文1, UPDATE-AI模块应用信息发布
# 更新程序心跳
# 主程序心跳
def time_update_info():
    client.connect(host="172.17.0.1", port=1883, keepalive=60)
    now = int(time.time())  # ->这是时间戳
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%dT%H%M%S", timeArray)
    pub_data = {
        "name": "UPDATE-APP",
        "version": "v1.0",
        "timestamp": otherStyleTime
    }
    sensor_data_pub = json.dumps(pub_data)

    client.publish(topic="app/notify/info", payload=sensor_data_pub, qos=0)
    t = Timer(120, time_update_info)
    t.start()


time_update_info()
checkprocess()
# pub_data = {
#     "name": "UPDATE-APP",
#     "version": "v1.0"
# }
# sensor_data_pub = json.dumps(pub_data)
# client.publish(topic="app/notify/info", payload=sensor_data_pub, qos=0)

# os.system('sh start.sh')

client.loop_forever()
