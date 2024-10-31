import asyncio

from v2.nacos.common.nacos_exception import NacosException
from v2.nacos.naming.model.instance import Instance
from v2.nacos.naming.model.service_info import ServiceInfo
from v2.nacos.naming.util.naming_client_util import get_group_name, get_service_cache_key
from v2.nacos.transport.connection_event_listener import ConnectionEventListener


class NamingGrpcConnectionEventListener(ConnectionEventListener):
    def __init__(self, client_proxy):
        self.logger = client_proxy.logger
        self.client_proxy = client_proxy
        self.registered_instance_cached = {}
        self.subscribes = {}
        self.lock = asyncio.Lock()

    async def on_connected(self) -> None:
        await self.__redo_subscribe()
        await self.__redo_register_each_service()

    async def on_disconnect(self) -> None:
        self.logger.info("Grpc connection disconnected")

    async def __redo_subscribe(self) -> None:
        for each in self.subscribes:
            info = ServiceInfo.from_key(each)
            try:
                service_info = await self.client_proxy.subscribe(info.name, info.groupName, info.clusters)
            except Exception as e:
                self.logger.warning("redo subscribe service %s failed: %s", info.name, e)
                continue
            self.client_proxy.service_info_cache.process_service_info(service_info)

    async def __redo_register_each_service(self) -> None:
        self.logger.info("Grpc reconnect, redo register services")
        for key, instanceVal in self.registered_instance_cached.items():
            info = ServiceInfo.from_key(key)
            try:
                if isinstance(instanceVal, Instance):
                    await self.client_proxy.register_instance(info.name, info.groupName, instanceVal)
                elif isinstance(instanceVal, list) and all(isinstance(x, Instance) for x in instanceVal):
                    await self.client_proxy.batch_register_instance(info.name, info.groupName, info)
            except Exception as e:
                self.logger.info("redo register service %s@@%s failed: %s"
                                 % (info.groupName, info.name, e))

    async def cache_instance_for_redo(self, service_name: str, group_name: str, instance: Instance) -> None:
        key = get_group_name(service_name, group_name)
        with self.lock:
            self.registered_instance_cached[key] = instance

    async def cache_instances_for_redo(self, service_name: str, group_name: str, instances: list[Instance]) -> None:
        key = get_group_name(service_name, group_name)
        with self.lock:
            self.registered_instance_cached[key] = instances

    async def remove_instance_for_redo(self, service_name: str, group_name: str) -> None:
        key = get_group_name(service_name, group_name)
        with self.lock:
            self.registered_instance_cached.pop(key)

    async def cache_subscribe_for_redo(self, full_service_name: str, cluster: str) -> None:
        cache_key = get_service_cache_key(full_service_name, cluster)
        with self.lock:
            if cache_key not in self.subscribes:
                self.subscribes[cache_key] = None

    async def remove_subscriber_for_redo(self, full_service_name: str, cluster: str) -> None:
        cache_key = get_service_cache_key(full_service_name, cluster)
        with self.lock:
            self.subscribes.pop(cache_key)