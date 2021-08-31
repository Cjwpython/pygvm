# coding: utf-8
from pygvm.client import Client

host = "10.0.83.41"
port = 9392
username = "tophant"
password = "tophant"
cli = Client(host=host, port=port, username=username, password=password)
with cli:
    tasks = cli.get_task_vul_result(task_id="6d597699-5b05-491a-aade-2775a1efe3f7")
    print(tasks)
