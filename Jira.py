import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import math

def get_jira_issues(jira_url, project_key, username, api_token, max_results=100):
    """
    Fetch all issues from a JIRA project and export to CSV
    
    Parameters:
    jira_url (str): Your JIRA instance URL (e.g., 'https://your-domain.atlassian.net')
    project_key (str): The project key (e.g., 'PROJ')
    username (str): Your JIRA email
    api_token (str): Your JIRA API token
    max_results (int): Number of results per page
    """
    
    # Initialize authentication and headers
    auth = HTTPBasicAuth(username, api_token)
    headers = {
        "Accept": "application/json"
    }
    
    # First API call to get total issue count
    jql_query = f'project = {project_key}'
    url = f"{jira_url}/rest/api/3/search"
    
    params = {
        'jql': jql_query,
        'maxResults': 0  # Just to get total count
    }
    
    response = requests.get(url, headers=headers, auth=auth, params=params)
    response.raise_for_status()
    
    total_issues = response.json()['total']
    total_pages = math.ceil(total_issues / max_results)
    
    print(f"Total issues found: {total_issues}")
    print(f"Total pages to process: {total_pages}")
    
    # Initialize list to store all issues
    all_issues = []
    
    # Fetch all pages
    for start_at in range(0, total_issues, max_results):
        params = {
            'jql': jql_query,
            'maxResults': max_results,
            'startAt': start_at,
            'fields': 'summary,status,priority,assignee,created,updated,issuetype'
        }
        
        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
        
        issues = response.json()['issues']
        
        # Process each issue
        for issue in issues:
            issue_data = {
                'Key': issue['key'],
                'Type': issue['fields']['issuetype']['name'],
                'Summary': issue['fields']['summary'],
                'Status': issue['fields']['status']['name'],
                'Priority': issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None',
                'Assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                'Created': issue['fields']['created'],
                'Updated': issue['fields']['updated']
            }
            all_issues.append(issue_data)
        
        print(f"Processed {min(start_at + max_results, total_issues)} of {total_issues} issues")
    
    # Convert to DataFrame and export to CSV
    df = pd.DataFrame(all_issues)
    csv_filename = f"{project_key}_issues.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\nExported {total_issues} issues to {csv_filename}")
    
    return total_issues, total_pages

# Example usage:
if __name__ == "__main__":
    # Replace these with your actual values
    JIRA_URL = "https://your-domain.atlassian.net"
    PROJECT_KEY = "PROJ"
    USERNAME = "your-email@domain.com"
    API_TOKEN = "your-api-token"
    
    try:
        total_issues, total_pages = get_jira_issues(JIRA_URL, PROJECT_KEY, USERNAME, API_TOKEN)
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
