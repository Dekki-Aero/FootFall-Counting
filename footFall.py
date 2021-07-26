# import the necessary packages
import cv2
from codes.var import args,ct,encoder,featureQue,net,model
from codes.config import config,optionalVar,INPUT_VIDEO,logger,shop_num,shop_name,initTtlCnt,initGrpCnt,initIndvCnt,updateConfigCounts
import numpy as np
import time
from codes.drawLine import getBoundry
from codes.pushToServer import Server
from datetime import datetime


def getLoc(X,Y,dst=None,direction='top'):
    adj = 30
    if not dst: tmp = (Bx - Ax) * (Y - Ay) - (By - Ay) * (X - Ax)
    else: tmp = (Bx - Ax) * (Y - (Ay-adj)) - ((By-adj) - (Ay-adj)) * (X - Ax)
    if tmp<0:
        if direction=='top': return 'outside'
        else: return 'inside'
    else : 
        if direction=='top': return 'inside'
        else: return 'outside'

def filterBxsByNms(rects,confs,model):
    if model=='frcnn':
        indices = cv2.dnn.NMSBoxes(rects, confs, args['confidence'], args['nmsThreshold'])
    else:
        indices = cv2.dnn.NMSBoxes(rects.tolist(), confs.tolist(), args['confidence'], args['nmsThreshold'])
    rectsf = []
    for i in indices:
        rectsf.append(rects[i[0]])
    return rectsf

def getCnts(v):
    cnt=grp=curGrp = 0
    gc=True
    for i in v:
        if i == curGrp:
            if gc: grp+=1;cnt-=1;gc = False
        else:
            gc = True;cnt+=1;curGrp=i
    return grp,cnt

def getDetections(net,frame,model):
    if model=='frcnn':
        net.setInput(cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False))
        detections = net.forward()
        return detections
    else:
        detections = net.detect(frame, confThreshold = 0.5)
        if len(detections[2]):  detections[2][:,2:]+=detections[2][:,:2]
        # else: boxes = detections[2]
        return detections[0],detections[1],detections[2]

def getRectsConfs(detections):
    if model=='frcnn':
        rects, confs = [], []
        for i in range(0, detections.shape[2]):
            box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
            if detections[0, 0, i, 2] > args["confidence"] \
                    and detections[0, 0, i, 1] == 0:
                rects.append([int(box[0]), int(box[1]), int(box[2]), int(box[3])])
                confs.append(float(detections[0, 0, i, 2]))
        return rects,confs
    else:
        classes, confidences, boxes = detections
        if len(classes):
            classes, confidences = classes.flatten(),confidences.flatten()
            indcs = np.where(classes==1)
            return boxes[indcs],confidences[indcs]
        else:
            return [],[]

if __name__ == "__main__":
    showImg = optionalVar.getboolean('show_video')
    freq = optionalVar.getint('freq')
    vs = cv2.VideoCapture(INPUT_VIDEO,cv2.CAP_FFMPEG)
    time.sleep(2.0)
    frameCnt = 0

    strt,fnl = getBoundry(config,vs,args['width'],logger,INPUT_VIDEO)
    (Ax,Ay),(Bx,By) = strt,fnl

    vdoStatus,frame = vs.read()
    for i in range(190):
        vdoStatus,frame = vs.read()
    # frame = image_resize(frame, width=args['width'])

    lst,cnt = -1,0
    locDict,grpDict = {},{}
    cntng = False
    grp = 1
    today = datetime.today().day
    displayTime = False
    direction = optionalVar.get('direction').lower()
    while True:
        if displayTime: st2 = time.time()
        vdoStatus,frame = vs.read()
        if vdoStatus:
            # frame = image_resize(frame, width=args['width'])
            frame = frame[:,Ax:Bx]
            H, W = frame.shape[:2]
            if frameCnt % freq == 0:
                if displayTime: st = time.time()
                detections = getDetections(net,frame,model)
                if displayTime: dtctTm = time.time()-st
                rects,confs = getRectsConfs(detections)
                if len(rects): rectsf = filterBxsByNms(rects,confs,model)
                else: rectsf=rects
                objects = ct.update(rectsf)
                for (objectID, (centroid,box)) in objects.items():
                    objectID += 1
                    loc = getLoc(centroid[0],centroid[1],direction = direction)
                    if objectID not in locDict: locDict[objectID] = loc
                    elif locDict[objectID] == 'outside' and loc == 'inside':
                        features = encoder(frame, [box])
                        status = featureQue.append(features)
                        if status:
                            cnt += 1
                            while True:
                                if not cntng : #and objectID not in grpDict
                                    grpDict[objectID] = grp
                                    initTime = frameCnt
                                    cntng = True
                                    locDict[objectID] = 'inside'
                                    break
                                else:
                                    if frameCnt - initTime <= 60 :
                                        grpDict[objectID] = grp
                                        locDict[objectID] = 'inside'
                                        break
                                    else:
                                        grp += 1
                                        cntng = False
                    if showImg and vdoStatus:
                        text = "ID {}, {} {}".format(objectID,loc,f"Group {grpDict[objectID]}" if objectID in grpDict else '')
                        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),\
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 0, 0), -1)
                        # cv2.rectangle(frame, box, color=(0, 255, 0))
                        cv2.rectangle(frame, (box[0],box[1]),(box[2],box[3]), color=(0, 255, 0))
        else:
            logger.warning("Unable to get video stream")
            vs = cv2.VideoCapture(INPUT_VIDEO, cv2.CAP_FFMPEG)
            logger.info("Pausing for 20 Sec ...")
            time.sleep(20)
        frameCnt+=1
        if showImg and vdoStatus:
                cv2.line(frame, pt1=(0,Ay),
                        pt2=fnl,
                        color=(0, 255, 255),
                        thickness=2)
                cv2.putText(frame, f'Total Count {cnt+initTtlCnt}', (args['width']//2,20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.imshow(f"Frame ", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
        if frameCnt % 500==0: logger.info("Processed {} frames, time : {}".format(frameCnt,datetime.now()))
        if lst!=cnt:
            grpCnt,indCnt = getCnts(grpDict.values())
            try:
                payload = {
                    "name": shop_name,
                    "count": cnt + initTtlCnt,
                    "group_count": grpCnt + initGrpCnt,
                    "individuals" : indCnt + initIndvCnt
                }
                server = Server()
                server.publish(shopNm=shop_num, payload=payload)
                logger.info("Counts updated in server")
            except Exception as e:
                logger.info("Couldn't push counts to server ",e)
            lst = cnt
            updateConfigCounts(groups = grpCnt+initGrpCnt,individuals = indCnt+initIndvCnt,count = cnt+initTtlCnt,day = today)
        if displayTime: logger.info('Time for detection {}, Remaining {}'.format(dtctTm,time.time()-st2))
        # print('Time for detection {}, Remaining {}'.format(dtctTm,time.time()-st2))
    if showImg:cv2.destroyAllWindows()

    #rtsp://admin:sang%%40123@49.206.18.107:554/Streaming/channels/101