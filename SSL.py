import os
import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable all SSL related warnings
urllib3.disable_warnings()
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# Set environment variables
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Monkey patch requests to disable verification
old_merge_environment_settings = requests.Session.merge_environment_settings

def merge_environment_settings(self, url, proxies, stream, verify, cert):
    settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
    settings['verify'] = False
    return settings

requests.Session.merge_environment_settings = merge_environment_settings

# Now import jiraone
from jiraone import LOGIN, endpoint

# When using LOGIN, try with additional settings
LOGIN(
    user="your_email",
    password="your_token",
    url="your_jira_url"
)
LOGIN.session.verify = False
