from concurrent.futures import ThreadPoolExecutor

from draw_bbox import *
import time
import uuid
import os
from main3 import ftpfile,sendMsg


class Check_all:
    def __init__(self):
        self.cate_regtime = {'hat': 0, 'armour': 0, "person": 0, 'fire': 0, 'smoke': 0, 'tobacco': 0, 'fence': 0}
        self.err_count = {'hat': 0, 'armour': 0, "person": 0, 'fire': 0, 'smoke': 0, 'tobacco': 0, 'fence': 0}
        
        
        self.f_status = {'hat': 0, 'armour': 0, "person": 0, 'fire': 0, 'smoke': 0, 'tobacco': 0, 'fence': 0}
        self.threadPool = ThreadPoolExecutor(max_workers=5)

    def sendRequest(self, image, bboxs, cate, curtime, f_status, gap=5):
        #curtime = self.cate_regtime[cate]
        #print(cate,f_status)
        #if f_status == 1:
        #    gap = 300
        if time.time() - curtime >= gap:
            print('========',cate,f_status)
            #self.cate_regtime[cate] = time.time()
            # 发送文字信息
            # msg = {
            #
            # }
            #

            # tempPath = './out/'
            # pictureName = f'{cate}_{uuid.uuid4().hex}.jpg'
            # if not os.path.exists(tempPath):
            #     os.makedirs(tempPath)
            # picPath = os.path.join(tempPath, pictureName)
            # cv2.imwrite(picPath, image)
            # self.lock.acquire()
            # self.cate_regtime[cate] = time.time()
            # self.lock.release()
            # print('picture:' + pictureName)
            # return pictureName
            # # output_file = os.path.join(OUTPUT_DIR, "out_" + os.path.basename(pic))
            # # print("output:%s" % output_file)
            tempPath = './out/'
            pictureName = f'{cate}_{uuid.uuid4().hex}.jpg'
            if not os.path.exists(tempPath):
                os.makedirs(tempPath)
            picPath = os.path.join(tempPath, pictureName)
            cv2.imwrite(picPath, image)
            # 发送告警
            sendMsg(pictureName,bboxs,cate)
            # 发送文件
            flag = ftpfile(pictureName,cate)
            if flag:
                # os.remove(picPath)
                # 这里写传送文件和信息的代码,image是处理好的图片(h,w,3)np格式,cate是异常类型
                self.lock.acquire()
                #self.cate_regtime[cate] = time.time()
                self.lock.release()


    ''' 
    image:cv2 image
    bboxs:list of bbox
    labels:list of label
    confidents:list of confident
    '''

    def check(self, image, bboxs, labels, confidents):
        draw_boxes(zip(labels, confidents, bboxs), image,
                   {'person': (0, 255, 0), 'armour': (0, 255, 0), 'hat': (0, 255, 0), 'fire': (0, 255, 0),
                    'smoke': (0, 255, 0), 'tobacco': (0, 255, 0), 'fence': (0, 255, 0)})
        # fire/smoke/tobacco
        if 'fire' in labels:
            if self.err_count['fire'] >= 3 and time.time() - self.cate_regtime['fire'] > 30+self.f_status['fire']*300:
                cv2.putText(image, 'fire!', (100, 100), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
                self.threadPool.submit(self.sendRequest, image, bboxs, 'fire', self.cate_regtime['fire'], self.f_status['fire'])
                self.err_count['fire'] = 0
                self.cate_regtime['fire'] = time.time()
                self.f_status['fire'] = 1
            else:
                self.err_count['fire'] += 1
        else:
            #self.cate_regtime['fire'] = time.time()-10
            self.f_status['fire'] = 0
        if 'smoke' in labels:
            if self.err_count['smoke'] >= 3 and time.time() - self.cate_regtime['smoke']> 30+self.f_status['smoke']*300:
                cv2.putText(image, 'smoke!', (100, 200), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
                self.threadPool.submit(self.sendRequest, image, bboxs, 'smoke', self.cate_regtime['smoke'], self.f_status['smoke'])
                self.err_count['smoke'] = 0
                self.cate_regtime['smoke'] = time.time()
                self.f_status['smoke'] = 1
            else:
                self.err_count['smoke'] += 1
        else:
            #self.cate_regtime['smoke'] = time.time()-10
            self.f_status['smoke'] = 0
        if 'tobacco' in labels:
            if self.err_count['tobacco'] >= 3 and time.time() - self.cate_regtime['tobacco']> 30+self.f_status['tobacco']*300:
                cv2.putText(image, 'tobacco!', (100, 300), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
                self.threadPool.submit(self.sendRequest, image, bboxs,'tobacco', self.cate_regtime['tobacco'], self.f_status['tobacco'])
                self.err_count['tobacco'] = 0
                self.cate_regtime['tobacco'] = time.time()
                self.f_status['tobacco'] = 1
            else:
                self.err_count['tobacco'] += 1
        else:
            #self.cate_regtime['tobacco'] = time.time()-10
            self.f_status['tobacco'] = 0

        # hat/armour/fence
        hat_bboxs = []
        person_bboxs = []
        armour_bboxs = []

        no_hat = False
        no_armour = False
        red = (0, 0, 255)
        for label, confidence, bbox in zip(labels, confidents, bboxs):
            top, left, bot, right = bbox
            if label == 'hat':
                hat_bboxs.append((left, top, right, bot))
            if label == 'armour':
                armour_bboxs.append((left, top, right, bot))
            if label == 'person':
                person_bboxs.append((left, top, right, bot))

        if person_bboxs:
            for person_bbox in person_bboxs:
                person_left, person_top, person_right, person_bottom = person_bbox
                if not hat_bboxs:
                    no_hat = True
                    if self.err_count['hat'] == 3:
                        cv2.rectangle(image, (person_left, person_top), (person_right, person_bottom), red, 1)
                        cv2.putText(image, 'no hat',
                                    (person_left, person_top + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
                else:
                    this_person_hat = False
                    for hat_bbox in hat_bboxs:
                        hat_left, hat_top, hat_right, hat_bottom = hat_bbox
                        hat_lfmid = (hat_left + hat_right) // 2
                        if person_left <= hat_lfmid <= person_right:
                            this_person_hat = True
                    if not this_person_hat:
                        no_hat = True
                        if self.err_count['hat'] == 3:
                            cv2.rectangle(image, (person_left, person_top), (person_right, person_bottom), red, 1)
                            cv2.putText(image, 'no hat',
                                        (person_left, person_top + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
                if not armour_bboxs:
                    no_armour = True
                    if self.err_count['armour'] == 3:
                        cv2.rectangle(image, (person_left, person_top), (person_right, person_bottom), red, 1)
                        cv2.putText(image, 'no armour',
                                    (person_left, person_top + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
                else:
                    this_person_armour = False
                    for armour_bbox in armour_bboxs:
                        arm_left, arm_top, arm_right, arm_bottom = armour_bbox
                        arm_lfmid = (arm_left + arm_right) // 2
                        if person_left <= arm_lfmid <= person_right:
                            this_person_armour = True
                    if not this_person_armour:
                        no_armour = True
                        if self.err_count['armour'] == 3:
                            cv2.rectangle(image, (person_left, person_top), (person_right, person_bottom), red, 1)
                            cv2.putText(image, 'no armour',
                                        (person_left, person_top + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)

        if no_hat:
            self.err_count['hat'] += 1
            if self.err_count['hat'] > 3 and time.time() - self.cate_regtime['hat']> 30+self.f_status['hat']*300:
                self.threadPool.submit(self.sendRequest, image, bboxs, 'hat', self.cate_regtime['hat'], self.f_status['hat'])
                self.err_count['hat'] = 0
                self.cate_regtime['hat'] = time.time()
                self.f_status['hat'] = 1
        else:
            #self.cate_regtime['hat'] = time.time()-10
            self.f_status['hat'] = 0
        if no_armour:
            self.err_count['armour'] += 1
            if self.err_count['armour'] > 3 and time.time() - self.cate_regtime['armour']> 30+self.f_status['armour']*300:
                self.threadPool.submit(self.sendRequest, image, bboxs, 'armour', self.cate_regtime['armour'], self.f_status['armour'])
                self.err_count['armour'] = 0
                self.cate_regtime['armour'] = time.time()
                self.f_status['armour'] = 1
        else:
            #self.cate_regtime['armour'] = time.time()-10
            self.f_status['armour'] = 0

        # fence

if __name__ == "__main__":
    # from main import ftpfile
    print('---main---')
