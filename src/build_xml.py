from datetime import datetime
import json
import logging
import os

import boto3
from dict2xml import dict2xml
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    return json.dumps(
        {
            "status_code": 200,
            "response": BuildXML(
                group_name="Testing group name",
                email=os.getenv('EMAIL_NOTIFICATION')
            ).handler()
        }
    )


class BuildXML:
    def __init__(self, email: str, group_name: str):
        self.email: str = email
        self.group_name: str = group_name
        self.s3_client = boto3.client(
            service_name="s3",
            region_name=os.getenv("REGION"),
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY")
        )
        self.now = datetime.now()

    def get_data(self):
        data = {
            "Email": self.email,
            "Confirm": "False",
            "Detail": "False",
            "Subject": "OFF",
            "Return": "true",
            "Group": self.group_name,
            "Action": "OFF",
            "Campaign": "OFF",
            "HtmlMessage": "False",
            "DisableMessageOptions": "OFF",
        }
        return data

    def handler(self):
        self.write_file(data=self.get_data())
        self.send_file()
        return {
            "sending": "ok"
        }

    def write_file(self, data):
        xml_data = dict2xml(data, wrap="ArchivoXML", indent="    ")
        with open(f"IN_{self.now.strftime('%Y%m%d%H%M')}.xml", "w") as f:
            f.write(xml_data)

    def send_file(self):
        self.s3_client.upload_file(
            f"IN_{self.now.strftime('%Y%m%d%H%M')}.xml",
            os.getenv("BUCKET"),
            f"IN_{self.now.strftime('%Y%m%d%H%M')}.xml"
        )