from jira import JIRA
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_issue_batch(jira, issues):
    """Helper function to process a batch of issues"""
    batch_data = []
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
            'Resolution': issue.fields.resolution.name if issue.fields.resolution else 'Unresolved',
            'Components': ','.join([c.name for c in issue.fields.components]) if issue.fields.components else '',
            'Labels': ','.join(issue.fields.labels) if issue.fields.labels else ''
        }
        
        # Optimized custom fields processing
        for field_name, field_value in issue.raw['fields'].items():
            if field_name.startswith('customfield_') and field_value is not None:
                if isinstance(field_value, dict):
                    field_value = field_value.get('value', '') or field_value.get('name', '')
                issue_dict[field_name] = str(field_value)
        
        batch_data.append(issue_dict)
    return batch_data

def export_jira_issues_to_csv(username, password, jira_url, project_name, jql_query=None, batch_size=1000, max_workers=4):
    """
    Export all issues from a specified Jira project to a CSV file using JQL with optimized performance.
    
    Args:
        username (str): Jira username
        password (str): Jira password/API token
        jira_url (str): Jira instance URL
        project_name (str): Project key/name in Jira
        jql_query (str, optional): Custom JQL query
        batch_size (int): Number of issues per batch (max 1000)
        max_workers (int): Number of parallel workers for processing
    
    Returns:
        str: Path to the exported CSV file
    """
    try:
        start_time = time.time()
        
        # Initialize Jira client with connection pooling
        options = {
            'verify': True,
            'pool_size': max_workers,
            'pool_maxsize': max_workers
        }
        
        jira = JIRA(
            basic_auth=(username, password),
            server=jira_url,
            options=options
        )
        
        # Construct JQL query
        if jql_query is None:
            jql_query = f'project = "{project_name}" ORDER BY created DESC'
        elif 'project' not in jql_query.lower():
            jql_query = f'project = "{project_name}" AND ({jql_query})'
            
        print(f"Using JQL query: {jql_query}")
        
        # Get total issue count first
        total_issues = jira.search_issues(jql_query, maxResults=1).total
        print(f"Total issues to process: {total_issues}")
        
        all_issues = []
        futures = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for start_at in range(0, total_issues, batch_size):
                # Fetch batch of issues
                issues = jira.search_issues(
                    jql_query,
                    startAt=start_at,
                    maxResults=batch_size,
                    fields='summary,status,issuetype,priority,reporter,assignee,created,updated,resolution,components,labels,*all'
                )
                
                # Submit batch processing to thread pool
                future = executor.submit(fetch_issue_batch, jira, issues)
                futures.append(future)
                
                # Print progress
                print(f"Queued batch starting at {start_at}")
            
            # Collect results as they complete
            for future in as_completed(futures):
                batch_results = future.result()
                all_issues.extend(batch_results)
                print(f"Processed batch - Total issues so far: {len(all_issues)}")
        
        # Convert to DataFrame efficiently
        df = pd.DataFrame(all_issues)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"jira_issues_{project_name}_{timestamp}.csv"
        
        # Export to CSV with optimized settings
        df.to_csv(filename, index=False, encoding='utf-8', chunksize=10000)
        
        end_time = time.time()
        print(f"Successfully exported {len(all_issues)} issues to {filename}")
        print(f"Total execution time: {end_time - start_time:.2f} seconds")
        return filename
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
