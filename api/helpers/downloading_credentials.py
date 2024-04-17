import pandas as pd
from api.schema import ListDBConfig, CronjobTimeConfig
from .database import get_db
import os
import requests
from fastapi import status
os.makedirs("ai_core/token", exist_ok=True)
def get_token_credentials_all_tenant():
    for tenant in ListDBConfig.LISTDBCONFIG:
        conn = get_db(tenant)
        cursor = conn.cursor()
        sql_query = "SELECT token_link FROM cv_reciever_config"
        cursor.execute(sql_query)

        # Fetch all the rows from the query result
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Get the column names from the cursor description
        if len(rows) != 0:
            for row in rows:
                response = requests.get(row["token_link"])
                if response.status_code == status.HTTP_200_OK and not os.path.exists(f"ai_core/token/{tenant}.json"):
                    with open(f"ai_core/token/{tenant}.json", "wb") as file:
                        file.write(response.content)

def get_cronjob_time_all_tenant():
    
    for tenant in ListDBConfig.LISTDBCONFIG:
        
        conn = get_db(tenant)
        cursor = conn.cursor()
        sql_query = "SELECT cronjob_hour, cronjob_minute FROM cv_reciever_config"
        cursor.execute(sql_query)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(rows) != 0:
            for cronjob_time in rows:
                CronjobTimeConfig.cronjob_time_config[tenant] = cronjob_time
    

