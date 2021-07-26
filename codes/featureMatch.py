from collections import deque
from codes.config import *
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DeQue():
    def __init__(self,maxLen=1000,simTresh = 0.95):
        self.que = deque(maxlen=maxLen)
        self.simTresh = simTresh

    def append(self,features):
        featuresAll = np.array(self.que)
        if len(featuresAll):
            similarities = cosine_similarity(features,featuresAll)
            # print(similarities)
            if not np.any(similarities > self.simTresh) :
                self.que.append(features[0])
                return 1
            else:
                logger.info("Not counting as similar one counted already")
                return 0
        else:
            self.que.append(features[0])
            return 1
