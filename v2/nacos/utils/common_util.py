import json
import time

from v2.nacos.common.constants import Constants


def get_current_time_millis():
    t = time.time()
    return int(round(t * 1000))


def to_json_string(obj):
    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        print(f"Error serializing object to JSON: {e}")
        return None


def to_json_obj(body):
    try:
        return json.loads(body)
    except (TypeError, ValueError) as e:
        print(f"Error serializing object to OBJ: {e}")
        return None


def to_json(obj):
    d = {}
    d.update(obj.__dict__)
    return d


def vars_obj(obj):
    try:
        return vars(obj)
    except (TypeError, ValueError) as e:
        print(f"Error serializing obj to dict: {e}")
        return None


def get_service_cache_key(serviceName, clusters):
    if not clusters:
        return serviceName
    return serviceName + Constants.SERVICE_INFO_SPLITER + clusters


def get_config_cache_key(data_id: str, group: str, tenant: str):
    return data_id + Constants.CONFIG_INFO_SPLITER + group + Constants.CONFIG_INFO_SPLITER + tenant
