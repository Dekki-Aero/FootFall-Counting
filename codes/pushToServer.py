import paho.mqtt.client as mqtt
from codes.config import dashboard_url,dashboard_port
import json

class Server:
      def __init__(self):
            self.client = mqtt.Client()
            self.client.connect(dashboard_url, dashboard_port, 60)
      def publish(self,shopNm,payload):
            self.client.publish(topic=f"shop/{shopNm}/data", payload=json.dumps(payload))