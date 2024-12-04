import os
import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable all warnings related to unsecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a custom adapter with SSL verification disabled
class SSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = urllib3.util.ssl_.create_urllib3_context()
        kwargs['assert_hostname'] = False
        kwargs['cert_reqs'] = 'CERT_NONE'
        return super().init_poolmanager(*args, **kwargs)

# Create custom session
session = requests.Session()
adapter = SSLAdapter()
session.mount('https://', adapter)
session.verify = False

# Import jiraone after setting up the session
from jiraone import LOGIN

# Use the custom session when initializing LOGIN
LOGIN(
    user="your_email",
    password="your_token", 
    url="your_jira_url",
    session=session
)
