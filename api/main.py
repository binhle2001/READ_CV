from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# from ai_core.source.reading_cv import push_data_to_DB
from .schema import CronjobTimeConfig
from .helpers.downloading_credentials import get_cronjob_time_all_tenant, get_token_credentials_all_tenant
from .helpers.database import get_db_config_all_tenants
from fastapi import FastAPI
import pytz
from .controller import router

#khi nào chạy theo cronjob thì dùng
'''
get_db_config_all_tenants()
get_token_credentials_all_tenant()
get_cronjob_time_all_tenant()

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Bangkok'))
scheduler.start()
for tenant_id in CronjobTimeConfig.cronjob_time_config:
    scheduler.add_job(
        push_data_to_DB,
        CronTrigger(
            hour=CronjobTimeConfig.cronjob_time_config[tenant_id]["cronjob_hour"], 
            minute=CronjobTimeConfig.cronjob_time_config[tenant_id]["cronjob_hour"]), 
        args=[tenant_id])
'''

# init application
app = FastAPI(
    title = 'EMPLOYEE AUTO CHECKING',
    description = "This API was built with FastAPI. Plugin/module in TIMS that supported about cheking of employees.",
    version = "1.0.0",
)
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(router)
