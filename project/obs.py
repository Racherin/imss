import requests


class OBSWrapper:

    def __init__(self, email):
        req = requests.get("https://raw.githubusercontent.com/Racherin/imss/flask_version/project/obs.json").json()

        return
