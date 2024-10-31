import asyncio
import unittest

from v2.nacos.common.client_config import GRPCConfig
from v2.nacos.common.client_config_builder import ClientConfigBuilder
from v2.nacos.naming.model.naming_param import RegisterInstanceParam
from v2.nacos.naming.nacos_naming_service import NacosNamingService

client_config = (ClientConfigBuilder()
                 .access_key('xxxxxxx')
                 .secret_key('xxxxxxxxxxxxxx')
                 .server_address('localhost:8848')
                 .log_level('INFO')
                 .grpc_config(GRPCConfig(grpc_timeout=5000))
                 .log_dir('/home/admin/logs/nacos').build())


class TestClientV2(unittest.IsolatedAsyncioTestCase):
    async def test_naming_register(self):
        client = await NacosNamingService.create_naming_service(client_config)
        try:
            await asyncio.sleep(5)
            response = await client.register_instance(
                request=RegisterInstanceParam(service_name='nacos.test.1', group_name='DEFAULT_GROUP', ip='1.1.1.1',
                                              port=7001, weight=1.0, cluster_name='c1', metadata={'a': 'b'},
                                              enable=True,
                                              healthy=True, ephemeral=True))
            self.assertEqual(response, True)
            if response:
                print("success to register")
            await asyncio.sleep(1000)
        except Exception as e:
            print(str(e))
