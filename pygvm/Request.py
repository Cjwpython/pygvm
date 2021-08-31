# coding: utf-8
import requests
from requests_toolbelt import MultipartEncoder
from pygvm.utils import lxml_to_dict, str_to_lxml
from http.cookies import SimpleCookie

requests.packages.urllib3.disable_warnings()
from pprint import pprint


class Request():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }

    @classmethod
    def get(cls, url, cookies={}, params={}):
        # 获取单个数据
        resp = requests.get(url, params=params, cookies=cookies, verify=False)
        tree = str_to_lxml(str(resp.content, encoding="utf-8"))
        data = lxml_to_dict(tree)["envelope"]
        if data.get("gsad_response"):
            raise Exception(data["gsad_response"]["message"])
        return lxml_to_dict(tree)["envelope"]["get_task"]["get_tasks_response"]["task"]

    @classmethod
    def get_report(cls, url, cookies={}, params={}):
        # 获取任务报告详情
        # result 并不能直接获取所有的数据，所以使用report
        resp = requests.get(url, params=params, cookies=cookies, verify=False)
        tree = str_to_lxml(str(resp.content, encoding="utf-8"))
        data = lxml_to_dict(tree)["envelope"]
        if data.get("gsad_response"):
            raise Exception(data["gsad_response"]["message"])
        return lxml_to_dict(tree)["envelope"]["get_report"]["get_reports_response"]["report"]
    @classmethod
    def list(cls, url, cookies={}, params={}):
        # 获取列表数据
        resp = requests.get(url, params=params, cookies=cookies, verify=False)
        tree = str_to_lxml(str(resp.content, encoding="utf-8"))
        return lxml_to_dict(tree)["envelope"]["get_tasks"]["get_tasks_response"]["task"]

    @classmethod
    def count(cls, url, cookies={}, params={}):
        # 获取数量
        resp = requests.get(url, params=params, cookies=cookies, verify=False)
        tree = str_to_lxml(str(resp.content, encoding="utf-8"))
        return lxml_to_dict(tree)["envelope"]["get_tasks"]["get_tasks_response"]["task_count"]["#text"]

    @classmethod
    def post(cls, url, token=None, cookie={}, cmd=None, id=None):
        # 发送单个数据
        resp = requests.post
        pass

    @classmethod
    def auth(cls, url, username=None, password=None):
        # 鉴权模块
        data = MultipartEncoder(
            fields={
                "cmd": "login",
                "login": username,
                "password": password
            }
        )
        cls.headers["Content-Type"] = data.content_type
        resp = requests.post(url, data=data, headers=cls.headers, verify=False)
        cookie = SimpleCookie(resp.headers.get("Set-Cookie"))
        cookies = {i.key: i.value for i in cookie.values()}
        tree = str_to_lxml(str(resp.content, encoding="utf-8"))
        return cookies, lxml_to_dict(tree)["envelope"]
