
from configparser import ConfigParser
from api.schema import ProcessStatus
import os


def get_env_var(group, var_name): 
    config = ConfigParser()
    file_path = ".env"
    if os.path.exists(file_path):
        config.read(file_path)
        return config[group][var_name]
    return os.environ.get(var_name)

def check_tenant_status(tenant_id):
    for process in ProcessStatus.list_tenant():
        if tenant_id == process["tenant_id"]:
            return True
    return False

def get_cv_file_s3_path(tenant_id):
    return f"cv_reader/{tenant_id}/CV/"