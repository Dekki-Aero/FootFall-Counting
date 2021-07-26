from codes.featureMatch import DeQue
from codes.config import logger,application_path,optionalVar
import cv2,os
from codes.libs.tracker.centroidtracker import CentroidTracker
from codes.libs.tools import generate_detections as gdet

featureQue = DeQue(maxLen=1000,simTresh=0.75)

model_filename = os.path.join(application_path,'codes/libs/model_data/mars-small128.pb')
encoder = gdet.create_box_encoder(model_filename, batch_size=1)

args = {
    "confidence": optionalVar.getfloat('confidence')/100,
    "nmsThreshold" : 0.7,
    "width" : 800
}

logger.info("[INFO] loading model...")

model = 'ssd' #optionalVar.get('model')
if model=='frcnn':
    net = cv2.dnn.readNetFromTensorflow(
        os.path.join(application_path,'codes/libs/model_data/frcnnGraph.pb'),
        os.path.join(application_path,'codes/libs/model_data/fastRcnn.pbtxt'))
else:
    net = cv2.dnn_DetectionModel(
        os.path.join(application_path,'codes/libs/model_data/ssd_mobilenet_v3_large_coco_2020_01_14/frozen_inference_graph.pb'),
        os.path.join(application_path,'codes/libs/model_data/ssd_mobilenet_v3_large_coco_2020_01_14/graph.pdtxt')
        )
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

logger.info("[INFO] loaded model...")

ct = CentroidTracker(maxDisappeared=2)

__all__ = ['featureQue','model_filename','encoder','args','net','ct']