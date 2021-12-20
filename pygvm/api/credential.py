# coding: utf-8

import uuid
from .base import BaseAPI, APISET


@APISET.register('credential')
class CredentialAPI(BaseAPI):
    def create(self, type, **kwargs):
        """创建认证
        :param type: 认证类型  当type 不传的时候，返回为空 其他根据上层业务进行传递
        :param kwargs: 可以参考下面的demo
        :return:

        如果没有name 在资质列表中name为uuid

        账号密码登录
        kwargs = {
        "credential_login": 123123,
        "lsc_password": 123123,
        }
        账号秘钥登录
        kwargs = {
        "credential_type": "usk",  登录方式
        "credential_login": "user", 登录用户名
        "passphrase": "12312312312", 证书的密码
        "private_key": key  证书的str内容，如果证书内容错误，会直接报错 ValueError: Erroneous Private Key.
        }
        """
        if not type:
            return

        form_data = {
            "token": self.token,
            "cmd": "create_credential",
            "name": str(uuid.uuid4()),
            "comment": "",
            "credential_type": "up",
            "allow_insecure": "1",
            "autogenerate": "0",
            "community": "",
            "credential_login": "",
            "lsc_password": "",
            "passphrase": "",
            "privacy_password": "",
            "auth_algorithm": "sha1",
            "privacy_algorithm": "aes"
        }
        form_data.update(kwargs)

        files = None
        if form_data.get("private_key"):
            private_key = form_data.pop("private_key")
            files = [
                ('private_key', ('id_rsa.bak', bytes(private_key, encoding="utf8"), 'application/octet-stream'))
            ]
        if form_data["credential_type"] == "usk":
            form_data["lsc_password"] = "tophant"
        result = self.client.post(data=form_data, files=files)
        return result["action_result"]["id"]

    def remove(self, credential_id):
        # 删除认证信息
        form_data = {
            "token": self.token,
            "cmd": "delete_credential",
            "credential_id": credential_id
        }
        self.client.post(data=form_data)

    def get(self, credential_id):
        # 获取认证信息
        params = {
            "token": self.token,
            "cmd": "get_credential",
            "credential_id": credential_id
        }
        result = self.client.get(params=params)
        return result["get_credential"]["get_credentials_response"]["credential"]

    def list(self, filter="sort=name rows=-1"):
        # 获取认证信息
        params = {
            "token": self.token,
            "cmd": "get_credentials",
            "filter": filter
        }
        result = self.client.get(params=params)
        credential = self.list_recovery(result["get_credentials"]["get_credentials_response"].get("credential"))
        return credential
