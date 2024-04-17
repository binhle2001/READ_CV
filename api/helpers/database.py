import logging

import pymysql
import requests

from api.helpers.common import get_env_var
from api.schema import ListDBConfig


def get_db_config_all_tenants():
    try:
        url = get_env_var("url", "IAM_API_URL") + "/all-tenants"
        headers = {
                "client-id": get_env_var("auth", "CHATBOT_CLIENT_ID"),
                "client-secret": get_env_var("auth", "CHATBOT_CLIENT_SECRET")
            }
        response = requests.get(url, headers = headers)
        data = response.json()
        if data['code'] == 200:
            data = data["data"]["organizationConfigs"]
            for item in data:
                ListDBConfig.LISTDBCONFIG[item["tenant"]] = item["dbConfig"]
            return True
        logging.error("get db config status: ", response)
        return False
    except Exception as e:
        logging.error(e)
        return False

def get_db(tenant_id):
    try:
        if tenant_id not in ListDBConfig.LISTDBCONFIG:
            get_db_config_all_tenants()

        if tenant_id not in ListDBConfig.LISTDBCONFIG:
            return None
        conn = pymysql.connect(
            host = ListDBConfig.LISTDBCONFIG[tenant_id]["host"],
            port = ListDBConfig.LISTDBCONFIG[tenant_id]["port"],
            user = ListDBConfig.LISTDBCONFIG[tenant_id]["username"], 
            password = ListDBConfig.LISTDBCONFIG[tenant_id]["password"], 
            db = ListDBConfig.LISTDBCONFIG[tenant_id]["databaseName"],
            cursorclass =  pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        logging.error(e)
        return None
    
