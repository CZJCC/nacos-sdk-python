from typing import Optional, Callable

from pydantic import BaseModel

from v2.nacos.common.constants import Constants


class RegisterInstanceParam(BaseModel):
    ip: str
    port: int
    weight: float = 1.0
    enabled: bool = True
    healthy: bool = True
    metadata: dict[str, str] = {}
    cluster_name: str = ''
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    ephemeral: bool = True


class BatchRegisterInstanceParam(BaseModel):
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    instances: list[RegisterInstanceParam] = []


class DeregisterInstanceParam(BaseModel):
    ip: str
    port: int
    cluster_name: str = ''
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    ephemeral: bool = True


class ListInstanceParam(BaseModel):
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    clusters: list[str] = []
    subscribe: bool = True
    healthy_only: bool


class SubscribeServiceParam(BaseModel):
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    clusters: list[str] = []
    subscribe_callback: Optional[Callable] = None


class GetServiceParam(BaseModel):
    service_name: str
    group_name: str = Constants.DEFAULT_GROUP
    clusters: list[str] = []


class ListServiceParam(BaseModel):
    namespace_id: str = Constants.DEFAULT_NAMESPACE_ID
    group_name: str = Constants.DEFAULT_GROUP
    page_no: int = 1
    page_size: int = 10