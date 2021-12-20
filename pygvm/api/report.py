# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('report')
class ReportAPI(BaseAPI):
    def get_report_id_by_task(self, task_id=None):
        task_data = self.api.task.get(task_id)
        task_status = task_data["status"]
        # 多个状态的任务获取
        if task_status == "Running":
            # 当任务正在运行
            return task_data["current_report"]["report"]["@id"]
        elif task_status == "Done":
            # 当任务运行结束
            return task_data["last_report"]["report"]["@id"]
        else:
            raise ValueError("unkonwn task status: {}".format(task_status))

    def get_report(self, report_id=None, severity=0, min_qod=0):
        """
        Notes
        -----
        Example Filter String
            apply_overrides=0 rows=100 min_qod=69 first=1 sort-reverse=severity severity>5
        """
        filter_str = "min_qod={} first=1 sort-reverse=severity severity>{}".format(
            min_qod, severity)
        params = {
            "cmd": "get_report",
            "lean": "1",
            "ignore_pagination": "1",
            "details": "1",
            "filter": filter_str,
            "report_id": report_id,
        }
        data = self.client.get(params=params)
        data = data['get_report']['get_reports_response']
        return data
