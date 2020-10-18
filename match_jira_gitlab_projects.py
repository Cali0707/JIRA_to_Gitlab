import JIRA_to_Gitlab as main
from json_extract import json_extract, extract_jira_project, extract_gitlab_project
import json


def match_jira_gitlab_projects():
    gl_projects = main.gl_get_request('/projects?sort=asc&order_by=id&per_page=100')
    for project in gl_projects:
        with open('gitlab_projects.json', 'a') as json_file:
            json.dump(project, json_file, indent=4)
    json_file.close()
    gl_projects_sorted = extract_gitlab_project(gl_projects)
    jira_projects = main.jira_get_request('/project')
    for project in jira_projects:
        with open('jira_projects.json', 'a') as jira_file:
            json.dump(project, jira_file, indent=4)
            
    jira_projects_sorted = extract_jira_project(jira_projects)
    
    matching_projects = []
    for project in gl_projects_sorted:
        proj = []
        for item in jira_projects_sorted:
            if project[1] == item[1]:
                proj.append(item)
                proj.append(project)
                matching_projects.append(proj)
                jira_projects_sorted.remove(item)
    # Clear the json files
    json_file = open(json_file.name, 'w')
    json_file.write('')
    jira_file = open(jira_file.name, 'w')
    jira_file.write('')
    
    #print(matching_projects)
    return jira_projects_sorted, matching_projects


if __name__ == '__main__':
    jira_projects_sorted, matching_projects = match_jira_gitlab_projects()
    print(jira_projects_sorted)
    print(matching_projects)
