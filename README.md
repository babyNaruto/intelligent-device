> ### 1.相机配置  

- **可发送程序更新包更新配置**。修改config.json中的userName和password，对应海康摄像头的用户名和密码。
- 海康摄像头默认IP：192.168.1.64


> 更新举例：  

修改config.json文件配置>打包压缩xxx.tar.gz>发送更新报文

- config.json内容参考：

``` python
{"userName": "admin","password": "xxxx","ip": "192.168.1.64"}
```
- **可现场手动更改配置**。更新内容同理  

---

> ### 2.程序启动  

 - **项目目录：**  /home/HwHiAiUser/mqtt/  

- main_back.py：主要完成读取摄像头信息，推理分析处理，将告警信息和图片等上传。
- updateAI.py： 守护进程，完成程序校时、模型更新、算法更新、配置更新等。
 
 - **开机程序自启动：**
  - 支持断电以及远程复位AI模块自启动。
  
 
 