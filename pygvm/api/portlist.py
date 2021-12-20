# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('portlist')
class PortlistAPI(BaseAPI):
    def init(self):
        self._portlist_uuid = {}
        self._portlist_name = {}

    def prepare(self):
        portlist = self.list()
        for pl in portlist['results']:
            self._portlist_uuid[pl['@id']] = pl
            self._portlist_name[pl['name']] = pl

    def create(self):
        """创建create_portlist
        TODO:
        """

    def list(self):
        """获取全部portlist列表"""
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_port_lists",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_port_lists']['get_port_lists_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        portlist = self.list_recovery(data.get('port_list'))
        result = {
            "results": portlist,
            "count": len(portlist),
        }
        return result

    def get(self, name=None, uuid=None):
        """获取单个portlist详情"""
        if name is not None:
            pl = self._portlist_name.get(name)
            return pl
        if uuid is not None:
            pl = self._portlist_uuid.get(uuid)
            return pl
