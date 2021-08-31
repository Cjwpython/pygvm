# coding: utf-8
class Response():
    @classmethod
    def get_login_info(cls, resp):
        print(resp.text())
