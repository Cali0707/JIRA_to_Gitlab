import os
import requests
from requests.auth import HTTPBasicAuth
import shutil


def image_post(image_url, file_name, jira_auth, gl_url, gl_token):
    image = requests.get(
        image_url,
        auth=HTTPBasicAuth(*jira_auth),
        stream=True)

    local_file = open(file_name, 'wb')
    image.raw.decode_content = True
    shutil.copyfileobj(image.raw, local_file)
    local_file.close()
    s = requests.Session()
    file = {'file': (file_name, open(file_name, 'rb'),'multipart/form-data')}
    value = s.post(
        gl_url,
        headers={'PRIVATE-TOKEN': gl_token},
        verify=True,
        files=file
    )
    print(value)
    os.remove(local_file)
    return value.json()
