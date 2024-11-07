import time
import urllib.parse
from typing import Optional

from pydantic import BaseModel

from v2.nacos.common.constants import Constants
from v2.nacos.common.nacos_exception import NacosException
from v2.nacos.naming.model.instance import Instance

EMPTY = ""

ALL_IPS = "000--00-ALL_IPS--00--000"

SPLITER = "@@"

DEFAULT_CHARSET = "UTF-8"


class Service(BaseModel):
    name: Optional[str]
    groupName: Optional[str]
    clusters: Optional[str]
    cacheMillis: int = 1000
    hosts: list[Instance] = []
    lastRefTime: int = 0
    checksum: str = ""
    allIps: bool = False
    reachProtectionThreshold: bool = False
    jsonFromServer: str = ""

    def init_from_key(self, key=None):
        if key:
            max_index = 2
            cluster_index = 2
            service_name_index = 1
            group_index = 0
            keys = key.split(Constants.SERVICE_INFO_SPLITER)
            if len(keys) >= max_index + 1:
                self.groupName = keys[group_index]
                self.name = keys[service_name_index]
                self.clusters = keys[cluster_index]
            elif len(keys) == max_index:
                self.groupName = keys[group_index]
                self.name = keys[service_name_index]
            else:
                raise NacosException("Can't parse out 'group_name', but it must not None!")

    def get_ip_count(self):
        return len(self.hosts)

    def is_expired(self):
        return int(round(time.time() * 1000)) - self.lastRefTime > self.cacheMillis

    def add_host(self, host):
        self.hosts.append(host)

    def add_all_hosts(self, hosts):
        self.hosts.extend(hosts)

    def is_valid(self):
        return self.hosts != []

    def validate(self):
        if self.allIps:
            return True

        if not self.hosts:
            return False

        valid_hosts = []
        for host in self.hosts:
            if not host.is_healthy():
                continue

            for i in range(host.get_weight()):
                valid_hosts.append(i)

        return len(valid_hosts) > 0

    def get_key_default(self):
        service_name = self.get_grouped_service_name()
        return self.get_key(service_name, self.clusters)

    def get_key_encoded(self):
        service_name = self.get_grouped_service_name().encode("utf-8")
        service_name = urllib.parse.quote(service_name)
        return self.get_key(service_name, self.clusters)

    def get_grouped_service_name(self):
        service_name = self.name
        if self.groupName and Constants.SERVICE_INFO_SPLITER not in service_name:
            service_name = self.groupName + Constants.SERVICE_INFO_SPLITER + service_name
        return service_name

    @staticmethod
    def from_key(key: str):
        service = Service()
        max_seg_count = 3
        segs = key.split(Constants.SERVICE_INFO_SPLITER)
        if len(segs) == max_seg_count - 1:
            service.groupName = segs[0]
            service.name = segs[1]
        elif len(segs) == max_seg_count:
            service.groupName = segs[0]
            service.name = segs[1]
            service.clusters = segs[2]
        return service

    def __str__(self):
        return self.get_key()

    def get_hosts_str(self):
        hosts_str = ""
        for host in self.hosts:
            hosts_str += host.json() + ";"
        return hosts_str

    class Config:
        arbitrary_types_allowed = True


class ServiceList(BaseModel):
    count: int
    services: list[str]
