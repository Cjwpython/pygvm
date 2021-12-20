# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('scan_config')
class ScanConfigAPI(BaseAPI):
    def init(self):
        self._scan_configs_uuid = {}
        self._scan_configs_name = {}

    def prepare(self):
        scan_configs = self.list()
        for sc in scan_configs['results']:
            self._scan_configs_uuid[sc['@id']] = sc
            self._scan_configs_name[sc['name']] = sc

    def create(self):
        """创建scan_config
        TODO:
        """

    def list(self):
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_configs",
            "usage_type": "scan",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_configs']['get_configs_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        configs = self.list_recovery(data.get('config'))
        result = {
            "results": configs,
            "count": len(configs),
        }
        return result

    def get(self, name=None, uuid=None):
        """获取单个scan_configs详情"""
        if name is not None:
            pl = self._scan_configs_name.get(name)
            return pl
        if uuid is not None:
            pl = self._scan_configs_uuid.get(uuid)
            return pl
