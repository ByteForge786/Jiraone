from jiraone import LOGIN, issue_export
import json

config = json.load(open("config.json"))
LOGIN(**config)

jql = "project = xys ORDER BY created DESC"
page_size = 1000
start_at = 0
all_issues = []

while True:
    issues = issue_export(jql=jql, page=(start_at, start_at + page_size))
    if not issues:
        break
    all_issues.extend(issues)
    start_at += page_size

# Save all_issues to CSV or handle as needed
