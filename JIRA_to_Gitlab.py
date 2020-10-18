import json

import requests
from requests.auth import HTTPBasicAuth
import re
from json_exract import json_extract
from image_post import image_post


##############################################################################
## General
"""
Lines 23, 25, 27, 29, 31, 33, 35, 41, 43, 45, 47, 49, 51, 66, 67 & 315 need to be changed 
to details from your JIRA & Gitlab instances
"""

# *False* if Jira / GitLab is using self-signed certificates, otherwise *True*
VERIFY_SSL_CERTIFICATE = True

##############################################################################
## Jira specifics

# Jira URL
JIRA_URL = 'https://yourdomain.atlassian.net/rest/api/3'
# Jira user credentials (incl. API token)
JIRA_ACCOUNT = ('email-from-JIRA-account', 'your-api-token')
# Jira project ID (short)
JIRA_PROJECT = 'KEY'
# Jira Query (JQL)
JQL = 'project=%s+AND+issueType=Epic+AND+resolution=Unresolved+ORDER+BY+createdDate+ASC&maxResults=100' % JIRA_PROJECT
# Jira Epic custom field
JIRA_EPIC_FIELD = 'customfield_10005'
# Jira Sprints custom field
JIRA_SPRINT_FIELD = 'customfield_10010'
# Jira story points custom field
JIRA_STORY_POINTS_FIELD = 'customfield_10014'

##############################################################################
## GitLab specifics

# GitLab URL
GITLAB_URL = 'https://lab.your-instance.com/api/v4'
# GitLab token will be used whenever the API is invoked
GITLAB_TOKEN = 'your-gitlab-token'
# GitLab group
GITLAB_GROUP = 'group-name'
# GitLab group id
GITLAB_GROUP_ID = 'group-id-number'
# Gitlab project with group/namespace
GITLAB_PROJECT = 'group-name/project-name'
# GitLab project id
GITLAB_PROJECT_ID = 'project-id-number'

##############################################################################
## Import configuration

# Add a comment with the link to the Jira issue
ADD_A_LINK = False

# Jira username as key, GitLab as value
# Note: If you want dates and times to be correct, make sure every user is (temporarily) owner
USERNAMES_MAP = {
    # 'your-jira-user-1': 'your-gitlab-user1',
    # 'your-jira-user-2': 'your-gitlab-user2',
   
}

# Convert Jira issue types to Gitlab labels
# Note: If a Jira issue type isn't in the map, the issue will be skipped
# use whole list
ISSUE_TYPES_MAP = {
    'Bug': 'Bug',
    'Epic': 'Epic',
    'Improvement': 'Improvement',
    'New Feature': 'New Feature',
    'Spec approval': 'Spec approval',
    'Story': 'Story',
    'Task': 'Task',
    'Sub-Task': 'Sub-Task',
    'Technical task': 'Technical task'
}

# Convert Jira story points to Gitlab issue weight
STORY_POINTS_MAP = {
    1.0: 1,
    2.0: 2,
    3.0: 3,
    5.0: 5,
    8.0: 8,
    13.0: 13,
    21.0: 21,
}


##############################################################################


# GET request
def gl_get_request(endpoint):
    response = requests.get(
        GITLAB_URL + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE
    )

    if response.status_code != 200:
        raise Exception("Unable to read data from %s!" % GITLAB_PROJECT_ID)

    return response.json()


# POST request
def gl_post_request(endpoint, data):
    response = requests.post(
        GITLAB_URL + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE,
        data=data
    )

    print('response is =', response.json())
    if response.status_code != 201:
        raise Exception("Unable to write data from %s!" % GITLAB_PROJECT_ID)
    return response.json()


# PUT request
def gl_put_request(endpoint, gl_project, data):
    response = requests.put(
        GITLAB_URL + '/' + gl_project + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE,
        data=data
    )

    return response.json()


# GET request
def jira_get_request(endpoint):
    response = requests.get(
        JIRA_URL + endpoint,
        auth=HTTPBasicAuth(*JIRA_ACCOUNT),
        verify=VERIFY_SSL_CERTIFICATE,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise Exception("Unable to read data from %s!" % JIRA_PROJECT)

    return response.json()




##############################################################################

def migrate_project(jira_project, gitlab_group_id, gitlab_project, gitlab_project_id):
  

    # Get all GitLab members
    gl_members = gl_get_request('/groups/%s/members' % gitlab_group_id)

    jira_issues_number = jira_get_request('/search?jql=project=%s ORDER BY created ASC&startAt=0&maxResults=0'
                                          % jira_project)['total']
    print(jira_issues_number)

    for startIndex in range(0, jira_issues_number, 100):

        jira_issues = jira_get_request('/search?jql=project=%s ORDER BY created ASC&startAt=%s&maxResults=-1'
                                       % (jira_project, startIndex))

        for issue in jira_issues['issues']:
            with open('json_file.json', 'w') as json_file:
                json.dump(issue, json_file, indent=4, separators=(':', ','))
                print(json_file)

            jira_key = issue['key']
            jira_issue_type = issue['fields']['issuetype']['name']

            gl_issue_type = ''
            if jira_issue_type not in ISSUE_TYPES_MAP:
                print("Unknown issue type detected. Jira issue %s skipped" % jira_key)
                continue
            else:
                gl_issue_type = ISSUE_TYPES_MAP[jira_issue_type]

            ##################

            print("Start import of Jira issue %s" % jira_key)
            jira_reporter = issue['fields']['reporter']['displayName']
            try:
                jira_title = issue['fields']['summary']
            except TypeError:
                jira_title = 'No title found on JIRA'
            try:
                jira_description = jira_reporter + ':', issue['fields']['reporter']['displayName'] \
                                   + json_extract(issue['fields']['description']['content'], 'text')
            except TypeError:
                jira_description = 'No description found on JIRA'
            
            try:
                jira_issue_status = issue['fields']['status']['statusCategory']['name']
            except TypeError:
                jira_issue_status = 'In Progress'
            jira_date = issue['fields']['created']

            # Get Jira assignee
            jira_assignee = ''
            if issue['fields']['assignee'] is not None and issue['fields']['assignee']['displayName'] is not None:
                jira_assignee = issue['fields']['assignee']['displayName']

            # Get GitLab assignee
            gl_assignee_id = 0
            for member in gl_members:
                if member['name'] == jira_assignee:
                    gl_assignee_id = member['id']
                    break

            # Add GitLab issue type as label
            gl_labels = []
            gl_labels.append(gl_issue_type)

            # Add "In Progress" to labels
            if jira_issue_status == "In Progress":
                gl_labels.append(jira_issue_type)

            # Add Jira ticket to labels
            gl_labels.append('jira-import::' + jira_key)

            # Get Jira attachments and comments - might want to do separately
            jira_info = jira_get_request('/issue/%s/?fields=attachment,comment' % issue['id'])
            jira_info_formatted = json.dumps(jira_info, indent=3)
            print(jira_info_formatted)

            # Issue weight
            gl_weight = 0
            if JIRA_STORY_POINTS_FIELD in issue['fields'] and issue['fields'][JIRA_STORY_POINTS_FIELD]:
                gl_weight = STORY_POINTS_MAP[issue['fields'][JIRA_STORY_POINTS_FIELD]]

            # Create GitLab issue
            print("posting to gitlab")
            gl_issue = gl_post_request('/projects/%s/issues' % gitlab_project_id, {
                'assignee_ids': [gl_assignee_id],
                'title': jira_title,
                'description': jira_description,
                'labels': ", ".join(gl_labels),
                'weight': gl_weight,
                'created_at': jira_date
            })

            gl_iid = gl_issue['iid']


            jira_attachments = []
            for attachment in jira_info['fields']['attachment']:
                i = image_post(
                    attachment['content'],
                    attachment['filename'],
                    JIRA_ACCOUNT,
                    'https://lab.your-instance.com/api/v4/projects/%s/uploads' % gitlab_project_id,
                    GITLAB_TOKEN)
                jira_attachments.append(i['markdown'])
            if jira_attachments:
                gl_attachment_comment = gl_post_request('/projects/%s/issues/%s/notes' % (gitlab_project_id, gl_issue['iid']), {
                    'body': jira_attachments
                })

            for comment in jira_info['fields']['comment']['comments']:
                author = comment['author']['displayName']
                if 'content' not in comment['body']:
                    content = comment['body']
                else:
                    content = json_extract(comment['body']['content'], 'text')
                comment_date = comment['created']
                gl_comment = gl_post_request('/projects/%s/issues/%s/notes' % (gitlab_project_id, gl_issue['iid']), {
                    # trying to take the body from the comment - JIRA returns a lot of information
                    # need to figure out how to have the author for the comment
                    'body': "%(k)s: %(u)s" % {'k': author, 'u': content},
                    'created_at': comment_date
                })

            # Add a comment with the link to the Jira issue
            if ADD_A_LINK:
                gl_post_request('/projects/%s/issues/%s/notes' % (gitlab_project_id, gl_issue['iid']), {
                    'body': "Imported from Jira issue [%(k)s](%(u)sbrowse/%(k)s)" % {'k': jira_key, 'u': JIRA_URL}
                })

            # Change GitLab issue status
            if jira_issue_status == "Done":
                gl_put_request('/projects/%s/issues/%s' % (gitlab_project_id, gl_iid), gitlab_project, {
                    'state_event': 'close'
                })


if __name__ == '__main__':
    from match_jira_gitlab_projects import match_jira_gitlab_projects
    jira_projects, project_match = match_jira_gitlab_projects()
    # Create new gitlab projects for any JIRA projects that do not already have an equivalent gitlab project
    for project in jira_projects:
        proj = [project]
        response = extract_gitlab_project(gl_post_request('/projects?name=%s' % project[1]))
        proj.append(response)
        project_match.append(proj)
    problem_projects = []
    # Migrate all projects (This might take a while!)
    for project in project_match:
        print('Begin import of project', project[0][1])
        try:
            migrate_project(project[0][0], project[1][3], project[1][2], project[1][0])
        except:
            problem_projects.append(project)
    print('The projects that were not migrated are:', problem_projects)        
    

