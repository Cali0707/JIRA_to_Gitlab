def json_extract(obj, key, return_type):
    """Recursively fetch values from nested JSON.
    If return_type == 'string' then it returns string, elif return_type == 'list', it returns values as a list.
    """
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v, in obj.items():
                if k == key:
                    if v is not None:
                        arr.append(v)
                elif k == 'projectCategory':
                    pass
                elif isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif v == 'paragraph' and return_type == 'string':
                    arr.append('<br/>')
                # elif k == key:
                # if v is not None:
                #   arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    if return_type == 'string':
        separator = ' '
        return separator.join(extract(obj, arr, key))
    elif return_type == 'list':
        return extract(obj, arr, key)
    else:
        raise ValueError("return_type must be either 'list' or 'string'")


def extract_jira_project(obj):
    """returns a list containing lists of the form [project key, project name]
    """
    arr = []

    def extract_jira(obj, arr):
        if isinstance(obj, dict):
            proj = []
            for k, v in obj.items():
                if k == 'key' or k == 'name':
                    proj.append(v)
                elif k == 'projectCategory':
                    pass
                if len(proj) == 2:
                    arr.append(proj)
                    proj = []
                if isinstance(v, (dict, list)):
                    extract_jira(v, arr)
        elif isinstance(obj, list):
            for item in obj:
                extract_jira(item, arr)
        return arr
    return extract_jira(obj, arr)


def extract_gitlab_project(obj):
    """returns a list containing lists of the form
    [project_id, project_name, name_with_namespace, group_id, group_name]"""
    arr = []

    def extract_gitlab(obj, arr):
        if isinstance(obj, dict):
            #print('isisnstance(obj, dict)')
            proj = []
            for k, v in obj.items():
                #print('k=', k)
                if k == 'id' or k == 'name' or k == 'path_with_namespace':
                    proj.append(v)
                    #print('proj=', proj)
                elif k == 'namespace':
                    proj.append(v['id'])
                    proj.append(v['name'])
                if len(proj) == 5:
                    arr.append(proj)
                    proj = []
                    #print('appending arr')
        elif isinstance(obj, list):
            for item in obj:
                extract_gitlab(item, arr)
        return arr
    return extract_gitlab(obj, arr)
