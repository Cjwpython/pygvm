# coding: utf-8

import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .api import APISET
from .utils import xml_loads, xml_to_dict

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GSAHttpClient(object):
    """GSAClient
    GVM client based on GSA http api.

    use Requests as http client, manage session and token
    """
    BASE_URL = "https://{}:{}/gmp"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    }

    def __init__(self, host, port=9393, username=None, password=None):
        self.api = APISET
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = self.BASE_URL.format(self.host, self.port)
        self.api.set_base_url(self.base_url)
        self.token = None
        self.session = None

    def get(self, params, timeout=None):
        params['token'] = self.token
        resp = self.session.get(self.base_url, params=params, timeout=timeout)
        result = self.parse_response(resp)
        return result

    def post(self, data, params=None, files=None, timeout=None):
        params = {} if params is None else params
        data = {} if data is None else data
        data['token'] = self.token
        resp = self.session.post(
            self.base_url,
            params=params, data=data, files=files,
            timeout=timeout,
        )
        result = self.parse_response(resp)
        return result

    def parse_response(self, resp):
        data = xml_to_dict(xml_loads(resp.content))
        if "envelope" not in data:
            raise ValueError("envelope not found, maybe bad request")
        if data['envelope'].get('gsad_response'):
            raise ValueError(data['envelope']['gsad_response'])

        # 部分异常处理
        error = data["envelope"].get("action_result")
        if error and not error["message"].startswith("OK"):
            raise ValueError(data["envelope"]["action_result"]["message"])
        return data['envelope']

    def login(self):
        """登陆接口
        设cookies，拿token
        """
        # 登录获取token和cookie
        # cookies, resp_data = GSAHttp.auth(self.base_url, username=self.username, password=self.password)
        self.session = requests.Session()
        # login
        multipart_data = (
            ("cmd", "login"),
            ("login", self.username),
            ("password", self.password),
        )
        resp = self.session.post(self.base_url, data=multipart_data, headers=self.HEADERS, verify=False)
        data = self.parse_response(resp)
        self.token = data.get("token")

    def renew(self):
        """默认接口需要15分钟刷新一次token防止超时登出"""
        data = {
            "cmd": "renew_session",
        }
        data = self.post(data=data)
        print("next renew timestamp: {}".format(data['session']))

    def logout(self):
        self.session.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def __enter__(self):
        self.login()
        self.api.set_client(self)
        self.api.prepare()
        return self
