# coding: utf-8
from pygvm.Request import Request
from pygvm.constants import base_url


class Client():
    """gvm web client"""

    def __init__(self, host, username=None, password=None, port=9390):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.token = None
        self.cookies = {}
        self.base_url = base_url.format(self.host, self.port)

    def login(self):
        # 登录获取token和cookie
        cookies, resp_data, = Request.auth(self.base_url, username=self.username, password=self.password)
        self.cookies = cookies
        token = resp_data.get("token")
        self.token = token

    def task_conut(self, filter_str="sort=name rows=1"):
        # 获取当前任务的全部数量
        params = {
            "token": self.token,
            "cmd": "get_tasks",
            "usage_type": "scan",
            "filter": filter_str
        }
        task_count = Request.count(self.base_url, cookies=self.cookies, params=params)
        return int(task_count)

    def list_tasks(self):
        # 获取所有任务
        filter_str = "sort=name rows=-1"
        params = {
            "token": self.token,
            "cmd": "get_tasks",
            "usage_type": "scan",
            "filter": filter_str
        }
        return Request.list(self.base_url, cookies=self.cookies, params=params)

    def get_task(self, task_id=None):
        # 获取任务的结果，不包含任务报告
        params = {
            "token": self.token,
            "cmd": "get_task",
            "task_id": task_id
        }
        return Request.get(self.base_url, cookies=self.cookies, params=params)

    def get_task_report_id(self, task_id=None):
        # 获取任务的报告id
        params = {
            "token": self.token,
            "cmd": "get_task",
            "task_id": task_id
        }
        task_data = Request.get(self.base_url, cookies=self.cookies, params=params)
        # TODO 多个状态的任务获取
        if task_data["status"] == "Running":
            # 当任务正在运行
            return task_data["current_report"]["report"]["@id"]
        elif task_data["status"] == "Done":
            # 当任务运行结束
            return task_data["last_report"]["report"]["@id"]

    def get_task_vul_result(self, task_id=None, severity=0.0):
        result = []
        report_id = self.get_task_report_id(task_id=task_id)
        filter_str = "min_qod=70 rows=-1 sort=name"
        params = {
            "token": self.token,
            "cmd": "get_report",
            "lean": "1",
            "ignore_pagination": "1",
            "details": "1",
            "filter_str": filter_str,
            "report_id": report_id
        }
        task_data = Request.get_report(self.base_url, cookies=self.cookies, params=params)
        for i in task_data["report"]["results"]["result"]:
            if float(i["severity"]) == float(severity):
                continue
            result.append(i)
        return result

    def get_task_status(self, task_id=None):
        # 获取任务的状态
        params = {
            "token": self.token,
            "cmd": "get_task",
            "task_id": task_id
        }
        task_data = Request.get(self.base_url, cookies=self.cookies, params=params)
        return task_data["status"]

    def get_task_process(self, task_id=None):
        # 获取任务的进度
        params = {
            "token": self.token,
            "cmd": "get_task",
            "task_id": task_id
        }
        task_data = Request.get(self.base_url, cookies=self.cookies, params=params)
        if task_data["status"] == "Running":
            return task_data["progress"]

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        self.login()
        return self
