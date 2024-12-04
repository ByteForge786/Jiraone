from jira import JIRA
import pandas as pd
from datetime import datetime

def export_jira_issues_to_csv(username, password, jira_url, project_name, jql_query=None):
    """
    Export all issues from a specified Jira project to a CSV file using JQL.
    
    Args:
        username (str): Jira username
        password (str): Jira password/API token
        jira_url (str): Jira instance URL
        project_name (str): Project key/name in Jira
        jql_query (str, optional): Custom JQL query. If None, defaults to all issues in project
    
    Returns:
        str: Path to the exported CSV file
    """
    try:
        # Initialize Jira client
        jira = JIRA(
            basic_auth=(username, password),
            server=jira_url,
            options={'verify': True}
        )
        
        # Initialize empty list to store all issues
        all_issues = []
        
        # Set up pagination parameters
        start_at = 0
        max_results = 1000  # Jira's maximum limit
        
        # Construct JQL query
        if jql_query is None:
            jql_query = f'project = "{project_name}" ORDER BY created DESC'
        elif 'project' not in jql_query.lower():
            # Ensure project is included in custom JQL
            jql_query = f'project = "{project_name}" AND ({jql_query})'
            
        print(f"Using JQL query: {jql_query}")
        
        while True:
            # Search issues using JQL
            issues = jira.search_issues(
                jql_query,
                startAt=start_at,
                maxResults=max_results,
                expand='changelog'
            )
            
            # Break if no more issues
            if len(issues) == 0:
                break
                
            # Process each issue
            for issue in issues:
                issue_dict = {
                    'Key': issue.key,
                    'Summary': issue.fields.summary,
                    'Status': issue.fields.status.name,
                    'Issue Type': issue.fields.issuetype.name,
                    'Priority': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'None',
                    'Reporter': issue.fields.reporter.displayName,
                    'Assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'Created': issue.fields.created,
                    'Updated': issue.fields.updated,
                    'Description': issue.fields.description if issue.fields.description else '',
                    'Labels': ','.join(issue.fields.labels) if issue.fields.labels else '',
                    'Resolution': issue.fields.resolution.name if issue.fields.resolution else 'Unresolved',
                    'Components': ','.join([c.name for c in issue.fields.components]) if issue.fields.components else '',
                    'Sprint': getattr(issue.fields, 'customfield_10020', 'No Sprint') if hasattr(issue.fields, 'customfield_10020') else 'No Sprint'
                }
                
                # Add custom fields if they exist
                for field_name in issue.raw['fields']:
                    if field_name.startswith('customfield_'):
                        field_value = issue.raw['fields'][field_name]
                        if field_value is not None:
                            if isinstance(field_value, dict):
                                field_value = field_value.get('value', '') or field_value.get('name', '')
                            issue_dict[field_name] = str(field_value)
                
                all_issues.append(issue_dict)
            
            # Update start_at for next iteration
            start_at += max_results
            
            # Print progress
            print(f"Retrieved {len(all_issues)} issues so far...")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_issues)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"jira_issues_{project_name}_{timestamp}.csv"
        
        # Export to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"Successfully exported {len(all_issues)} issues to {filename}")
        return filename
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
