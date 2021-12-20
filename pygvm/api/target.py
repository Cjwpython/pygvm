# coding: utf-8

from .base import BaseAPI, APISET


@APISET.register('target')
class TargetAPI(BaseAPI):
    def create(self, name, hosts,
               comment='', allow_simultaneous_ips=True, exclude_hosts=None,
               reverse_lookup_only=False, reverse_lookup_unify=False,
               port_list_id=None, alive_tests=None,
               ssh_credential_id=None, ssh_port=22,
               smb_credential_id=None, esxi_credential_id=None, snmp_credential_id=None):
        '''
        INTERNAL:
        token: ccfbf679-56cd-4a81-89d9-d0492888aeb3
        cmd: create_target
        target_source: manual
        target_exclude_source: manual

        ARGS:
        name: test name
        hosts: 10.0.0.0/24

        OPTS:
        comment: comment test
        allow_simultaneous_ips: 1
        exclude_hosts: 10.0.0.0/28
        reverse_lookup_only: 0
        reverse_lookup_unify: 0
        port_list_id: 33d0cd82-57c6-11e1-8ed1-406186ea4fc5


        alive_tests: Scan Config Default, Consider Alive

        ssh_credential_id: 0
        # ssh port
        port: 22
        smb_credential_id: 0
        esxi_credential_id: ebfc341f-b8a1-4386-a837-1aa247d1e05f
        snmp_credential_id: 0
        '''
        # make default
        alive_tests = 'Scan Config Default' if alive_tests is None else alive_tests
        allow_simultaneous_ips = 1 if allow_simultaneous_ips is True else 0
        if port_list_id is None:
            pld = self.api.portlist.get(name='All IANA assigned TCP and UDP')
            if pld is None:
                raise ValueError("portlist not found")
            else:
                port_list_id = pld['@id']
        ssh_credential_id = '0' if ssh_credential_id is None else ssh_credential_id
        smb_credential_id = '0' if smb_credential_id is None else smb_credential_id
        esxi_credential_id = '0' if esxi_credential_id is None else esxi_credential_id
        snmp_credential_id = '0' if snmp_credential_id is None else snmp_credential_id
        # assemble data
        data = {
            "cmd": "create_target",
            "target_source": "manual",
            "target_exclude_source": "manual",
            "name": name,
            "hosts": hosts,
            "comment": comment,
            "allow_simultaneous_ips": allow_simultaneous_ips,
            "port_list_id": port_list_id,
            "ssh_credential_id": ssh_credential_id,
            "port": ssh_port,
            "alive_tests": alive_tests,
            "smb_credential_id": smb_credential_id,
            "esxi_credential_id": esxi_credential_id,
            "snmp_credential_id": snmp_credential_id,
        }
        data = self.client.post(data=data)
        if "id" not in data['action_result']:
            raise ValueError("Create target failed: {}".format(data['action_result']['message']))
        else:
            uuid = data['action_result']['id']
            return uuid

    def list(self):
        """
        """
        filter_str = "sort=name rows=-1"
        params = {
            "cmd": "get_targets",
            "asset_type": "host",
            "filter": filter_str,
        }
        data = self.client.get(params=params)
        data = data['get_targets']['get_targets_response']
        # temp
        if data['@status'] != '200':
            raise ValueError("status not 200")
        # make result
        targets = self.list_recovery(data.get('target'))
        result = {
            "results": targets,
            "count": len(targets),
        }
        return result

    def get(self, name=None, uuid=None):
        """获取单个target详情
        TODO:
        """

    def remove(self, uuid):
        data = {
            "cmd": "delete_target",
            "target_id": uuid,
        }
        data = self.client.post(data=data)
        msg = data['action_result']['message']
        if msg != 'OK':
            raise ValueError("Delete target failed: {}".format(data['action_result']['message']))
