import requests


class OBSWrapper:

    def __init__(self, email):
        self.req = requests.get("https://raw.githubusercontent.com/Racherin/imss/flask_version/project/obs.json").json()
        self.data = {}
        if self.req[email] is not None:
            self.user = self.req[email]
            self.response = "success"
        else :
            self.response = "error"

    def get_user_name(self):
        return self.user['name']

    def get_user_email(self):
        return self.user['email']

    def get_user_type(self):
        return self.user['type']

    def get_user_department(self):
        return self.user['department']
