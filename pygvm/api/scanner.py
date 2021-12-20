# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('scanner')
class ScannerAPI(BaseAPI):
    def init(self):
        self._scanners_uuid = {}
        self._scanners_name = {}

    def prepare(self):
        scanners = self.list()
        for sc in scanners['results']:
            self._scanners_uuid[sc['@id']] = sc
            self._scanners_name[sc['name']] = sc

    def list(self):
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_scanners",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_scanners']['get_scanners_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        scanners = self.list_recovery(data.get('scanner'))
        result = {
            "results": scanners,
            "count": len(scanners),
        }
        return result

    def get(self, name=None, uuid=None):
        """获取单个scanner详情"""
        if name is not None:
            sc = self._scanners_name.get(name)
            return sc
        if uuid is not None:
            sc = self._scanners_uuid.get(uuid)
            return sc
