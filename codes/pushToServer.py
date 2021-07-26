import paho.mqtt.client as mqtt
import json

class Server:
      def __init__(self):
            self.client = mqtt.Client()
            self.client.connect("128.199.76.117", 1883, 60)
      def publish(self,shopNm,payload):
            self.client.publish(topic=f"shop/{shopNm}/data", payload=json.dumps(payload))