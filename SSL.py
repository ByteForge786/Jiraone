import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Patch the original Session class
original_session = requests.Session
class PatchedSession(original_session):
    def __init__(self):
        super().__init__()
        self.verify = False
        
requests.Session = PatchedSession

# Now import and use jiraone
from jiraone import LOGIN, endpoint
