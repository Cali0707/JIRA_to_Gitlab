# JIRA_to_Gitlab
A script to migrate from JIRA to Gitlab

# Usage
To use this script, one should replace the details in JIRA_to_Gitlab.py with their personal credentials,
as explained in the file, then run JIRA_to_Gitlab.py as the main file. Make sure that the credentials you use for both
JIRA and Gitlab give you access to all projects and issues, as the project will otherwise be skipped and not migrated.

# Known issues
This script posts all comments from JIRA under the same Gitlab user, with the first line of the comment indicating
which JIRA user posted the comment. To change this, one would need a gitlab token for each user in the JIRA instance,
and to post each comment using that user's Gitlab credentials.
The other issue is that image_download.py does not delete images after posting them - this needs to be done manually.

# Contributing
Contributions are welcome on this repo in the form of pull requests and by opening issues.
