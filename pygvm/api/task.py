# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('task')
class TaskAPI(BaseAPI):
    def create(self, name, target_id, scanner_id,
               comment=None, min_qod=None,
               # OpenVAS 参数
               scan_config_id=None, hosts_ordering=None,
               max_hosts=None, max_checks=None, source_iface=None,
               ):
        """创建任务
        按目前业务情况，下发到这个接口的都是单个IP地址或者域名

        Parameters
        ----------
        name : str
            name
        target_id : str
            uuid of target
        scanner_id : str
            uuid of scanner

        comment : str
            comment of task
        min_qod : int
            Quality of Detection, default 0

        scan_config_id : str
            OpenVAS specific config, uuid of scan config
        hosts_ordering : str
            OpenVAS specific config, default sequential
        max_hosts : str
            OpenVAS specific config, default 20
        max_checks : str
            OpenVAS specific config, default 4
        source_iface : str
            OpenVAS specific config, source NIC

        Returns
        -------
        str
            uuid of task.

        API Reference
        -------------
        token           : 614dac0e-0642-436d-9fa8-9dc08106bf6c
        cmd             : create_task
            必填，固定参数
        name            : task test CVE
            必填，任务名称
        comment         : ''
            必填，备注
        target_id       : 99a793c0-9ec5-4556-82ff-f944554cd712
            必填，目标uuid
        usage_type      : scan
            必填，固定参数
        apply_overrides : 1
            必填，是否覆盖，1为覆盖
        min_qod         : 70
            必填，Quality of Detection
        auto_delete     : no
            必填，是否自动删除生成的报告 no为不删除
        auto_delete_data: 5
            必填，保留的报告数量，auto_delete为no时不生效
        in_assets       : 1
            必填，是否自动添加入assets中，1为是

        scanner_id      : 6acd0832-df90-11e4-b9d5-28d24461215b
            必填，scanner的uuid
        scanner_type    : 3
            必填，扫描器类型 CVE为3 OpenVAS为2
        config_id       : daba56c8-73ec-11df-a475-002264764cea
            扫描器类型为OpenVAS时，对应的config_id
        source_iface    : ''
            扫描器类型为OpenVAS时，源接口
        max_checks      : 4
            扫描器类型为OpenVAS时，
        max_hosts       : 20
            扫描器类型为OpenVAS时，
        hosts_ordering  : sequential
            扫描器类型为OpenVAS时，

        alterable       : 0
            必填，固定参数，用途不明
        schedule_id     : 0
            必填，计划的ID

        schedule_periods: 1
            选填，计划周期，1表示只跑一次
        add_tag         : 0
            选填，用途不明

        Examples
        --------
        """
        # make default
        comment = '' if comment is None else comment
        min_qod = 0 if min_qod is None else min_qod
        if scanner_id not in self.api.scanner._scanners_uuid:
            raise ValueError("Could not find specific scanner: {}".format(scanner_id))
        scanner_type = self.api.scanner._scanners_uuid[scanner_id]['type']
        # import ipdb;ipdb.set_trace()
        # assemble data
        data = {
            # must
            "cmd": "create_task",
            "name": name,
            "comment": comment,
            "scanner_type": scanner_type,
            "scanner_id": scanner_id,
            "min_qod": min_qod,
            "usage_type": "scan",
            "target_id": target_id,
            "schedule_id": 0,
            "in_assets": 1,
            "apply_overrides": 1,
            "auto_delete": "no",
            "auto_delete_data": 5,
            "alterable": 0,
            # opt
            "schedule_periods": 1,
        }
        # scanner_type is OpenVAS
        if scanner_type == '2':
            hosts_ordering = 'sequential' if hosts_ordering is None else hosts_ordering
            max_checks = 4 if max_checks is None else max_checks
            max_hosts = 20 if max_hosts is None else max_hosts
            source_iface = '' if source_iface is None else source_iface
            if scan_config_id is None:
                scan_config_id = self.api.scan_config.get(name='Full and fast')['@id']
            data['config_id'] = scan_config_id
            data['hosts_ordering'] = hosts_ordering
            data['max_checks'] = max_checks
            data['max_hosts'] = max_hosts
            data['source_iface'] = source_iface
        # do post
        data = self.client.post(data=data)
        if "id" not in data['action_result']:
            raise ValueError("Create task failed: {}".format(data['action_result']['message']))
        else:
            uuid = data['action_result']['id']
            return uuid

    def list(self):
        """获取任务列表"""
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_tasks",
            "usage_type": "scan",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_tasks']['get_tasks_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        task_list = self.list_recovery(data.get('task'))
        result = {
            "results": task_list,
            "count": len(task_list),
        }
        return result

    def get(self, task_id):
        """获取单个任务"""
        params = {
            "cmd": "get_task",
            "task_id": task_id
        }
        data = self.client.get(params=params)
        return data['get_task']['get_tasks_response']['task']

    def get_status(self, task_id):
        detail = self.get(task_id)
        return detail['status']

    def get_progress(self, task_id):
        detail = self.get(task_id)
        pg = int(detail['progress'])
        status = detail['status']
        if pg < 0:
            return 0
        if status == 'Done':
            return 100
        return pg

    def start(self, task_id):
        """
        Notes
        -----
        状态转移
        - 新建task至task执行完成
            New -> Requested -> Queued -> Running -> Done
        - 停止正在执行的task至恢复(resume_task)task
            Running -> Stop Requested -> Stopped -> Requested -> Queued -> Running
        - 停止正在执行的task至开始(start_task)task
            Running -> Stop Requested -> Stopped -> Requested -> Queued -> Running
        """
        task = self.get(task_id)
        # status check
        if task['status'] not in {'New'}:
            raise ValueError("Task's status not match: {}".format(task['status']))
        data = {
            'cmd': 'start_task',
            'task_id': task_id,
        }
        data = self.client.post(data=data)

    def stop(self, task_id):
        """
        Notes
        -----
        在Requested和Queued状态下停止该task大概率导致这个task无法恢复(resume_task)
        """
        data = {
            'cmd': 'stop_task',
            'task_id': task_id,
        }
        data = self.client.post(data=data, timeout=5)

    def resume(self, task_id):
        task = self.get(task_id)
        # status check
        if task['status'] not in {'Stopped'}:
            raise ValueError("Task's status not match: {}".format(task['status']))
        data = {
            'cmd': 'resume_task',
            'task_id': task_id,
        }
        data = self.client.post(data=data)

    def remove(self, task_id):
        """
        token: 1ffcc72e-91f2-404a-a69e-40536a2ac2ed
        cmd: delete_task
        task_id: a9478c01-1c02-41f2-96f5-ad32cc92c379
        """
        data = {
            'cmd': 'delete_task',
            'task_id': task_id,
        }
        data = self.client.post(data=data)
