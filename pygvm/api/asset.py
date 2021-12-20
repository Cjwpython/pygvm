# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('asset_host')
class AssetHostAPI(BaseAPI):
    def list(self):
        '''cmd: get_assets
        asset_type: host
        filter: sort=name first=1 rows=1000'''
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_assets",
            "asset_type": "host",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_assets']['get_assets_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        assets = self.list_recovery(data.get('asset'))
        result = {
            "results": assets,
            "count": len(assets),
        }
        return result
