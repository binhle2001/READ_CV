from pydantic import BaseModel,  Field
from typing import Union
import pandas as pd

class CVSender:
    list_email_address_sender = {
    "teamhub": {
    "email_address": ["binhltl@tokyotechlab.com"],
    "label": ["INBOX"],
    "status": ["unread"],
        }
    }


class UpdateCVSender(BaseModel):
    email_address: str = Field(example = "refresh_devices")
    label: str = Field(example = "")
    status: str = "unread"
    class Config:
        json_schema_extra = {
            "example":{
                "email_address": "refresh_devices",
                "label": "", 
                "status": ""
            }
        }

class ProcessStatus:
    list_tenant = {}


class ListDBConfig:
    LISTDBCONFIG = {
        "teamhub": {
            "host": "127.0.0.1",
            "port": 3306,
            "username": "root",
            "password": "",
            "databaseName": "read_cv",
        }
    }
    
class Hook(BaseModel):
    tenant_id: str
    class Config:
        json_schema_extra = {
            "tenant_id": "str",
        }

class CronjobTimeConfig:
    cronjob_time_config = {}