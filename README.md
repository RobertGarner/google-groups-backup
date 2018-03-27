# google-groups-backup

A script enabling a user to download the message history ( into a .json file) and attachements of a google groups archive.

This utility uses selenium, due to the javascript generated nature of google groups. The following software packages are required:

- Selenium WebDriver for python 
- Chrome/Firefox driver for selenium 

Information on both of these, and setting up selenium is available from the [project website](https://www.seleniumhq.org/). 

## Usage
An example is included in the main section of archivegg.py.

The following top level variables and functions are required:
- Define a download path for any files (currently set a Download folder in the project path)
- Setup the driver, if this is the first time this script is run, please provide a username and password (for a private group) - otherwise the script automatically saves cookies to the google group
- If this is the first time the script has been run, use "find_conversation_urls" and provide the link to the google group
- Call download_archive, specifying the json filename for the archive to be outputted to, and if you wish to download attachments

