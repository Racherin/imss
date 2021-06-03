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

    def get_user_nationality(self):
        return self.user['nationality']

    def get_user_courses(self):
        if self.get_user_type() == "Student" :
            return self.user['courses']['semester1']
        else :
            return ""

    def get_user_gpa(self):
        if self.get_user_type() == "Student" :
            return self.user['gpa']
        else :
            return ""

    def get_user_department_advisor(self):
        if self.get_user_type() == "Student" :
            return self.user['department_advisor']
        else :
            return ""

    def get_user_department_advisor_mail(self):
        if self.get_user_type() == "Student" :
            return self.user['department_advisor_mail']
        else :
            return ""

    def get_user_prerequisites(self):
        if self.get_user_type() == "Student" :
            return self.user['prerequisite']
        else :
            return ""

    def get_semester(self):
        return self.user['semester']

    def get_photo(self):
        return self.user['photo']