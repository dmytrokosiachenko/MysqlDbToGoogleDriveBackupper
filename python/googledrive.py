import ast
import filecmp
import os
import sys

import googleapiclient
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFileList

CREATED_DATE = 'createdDate'

BACKUPS_TO_KEEP = int(os.getenv('BACKUPS_TO_KEEP'))
BACKUP_FOLDER_NAME = os.getenv('BACKUP_FOLDER_NAME')
YOUR_EMAIL = os.getenv('YOUR_EMAIL')

if not BACKUPS_TO_KEEP:
    sys.exit("No number defined how many backups to keep")

if not BACKUP_FOLDER_NAME:
    sys.exit("No google drive folder name for backups defined")

if not YOUR_EMAIL:
    sys.exit("Google email address is not defined, it is needed to give you read permissions to backup folder.")

if "gmail" not in YOUR_EMAIL:
    sys.exit("Your email must be from gmail! In other case you would not be able to access backup files.")


def authenticate():
    auth = GoogleAuth()
    scope = ["https://www.googleapis.com/auth/drive"]
    auth.credentials = ServiceAccountCredentials.from_json_keyfile_name("client_secrets.json", scope)
    drive = GoogleDrive(auth)
    return drive


def get_sorted_files_from_drive(drive, folder_name):
    """
    Get sorted by date file list form Drive.
    First element is the newest one.
    """
    folder_id = get_folder_id(drive, folder_name=folder_name, parent_folder_id="root")
    file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(folder_id)}).GetList()
    for file1 in file_list:
        metadata = file1.metadata
        date_time = metadata[('%s' % CREATED_DATE)]
        file1[CREATED_DATE] = date_time
    return sorted(file_list, key=lambda file: file[CREATED_DATE], reverse=True)


def get_folder_id(drive, parent_folder_id, folder_name):
    """
    Check if destination folder exists and return it's ID
    :param drive: An instance of GoogleAuth
    :param parent_folder_id: the id of the parent of the folder we are uploading the files to
    :param folder_name: the name of the folder in the drive
    """

    # Auto-iterate through all files in the parent folder.
    file_list = GoogleDriveFileList()

    try:
        file_list = drive.ListFile(
            {'q': "'{0}' in parents and trashed=false".format(parent_folder_id)}
        ).GetList()
    # Exit if the parent folder doesn't exist
    except googleapiclient.errors.HttpError as err:
        # Parse error message
        message = ast.literal_eval(err.content)['error']['message']
        if message == 'File not found: ':
            print(message + folder_name)
            exit(1)
        # Exit with stacktrace in case of other error
        else:
            raise

    # Find the the destination folder in the parent folder's files
    for file in file_list:
        if file['title'] == folder_name:
            print('Found folder -> title: %s, id: %s' % (file['title'], file['id']))
            return file['id']


def create_folder(drive, folder_name, parent_folder_id):
    """
    Create folder on Google Drive
    :param drive: An instance of GoogleAuth
    :param folder_name the id of the folder we are uploading the files to
    :param parent_folder_id: the id of the parent of the folder we are uploading the files to
    """
    folder_metadata = {
        'title': folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
        # ID of the parent folder
        'parents': [{"kind": "drive#fileLink", "id": parent_folder_id}]
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    folder.InsertPermission({
        'type': 'user',
        'value': '{}'.format(YOUR_EMAIL),
        'role': 'owner'})

    # Return folder information
    print('Created folder -> title: %s, id: %s' % (folder['title'], folder['id']))
    return folder['id']


def upload_files_in_folder(drive, folder_name, src_file_name):
    stat_info = os.stat(src_file_name)
    if stat_info.st_size > 0:
        folder_id = get_folder_id(drive, folder_name=folder_name, parent_folder_id="root")
        if not folder_id:
            folder_id = create_folder(drive, folder_name=folder_name, parent_folder_id="root")
        drive_file = drive.CreateFile(
            {"parents": [{"kind": "drive#fileLink", "id": folder_id}], 'title': src_file_name})
        drive_file.SetContentFile(src_file_name)
        drive_file.Upload()
    else:
        print("Failed to upload -> file {0} is empty.", src_file_name)


def delete_obsolete_files(drive, folder_name):
    files_to_sort = get_sorted_files_from_drive(drive, folder_name)
    files_to_delete = files_to_sort[BACKUPS_TO_KEEP:]
    for file in files_to_delete:
        file.Delete()
        print("Deleted obsolete file with date:", file[CREATED_DATE])


def file_exists_in_google_drive(drive, folder_name, filename):
    """
    Check if the last uploaded file with exact same content was already uploaded to google drive
    """
    files_to_sort = get_sorted_files_from_drive(drive, folder_name)

    files_to_sort[0].GetContentFile('file_from_drive.sql')
    file_from_drive = 'file_from_drive.sql'
    file_from_dump = filename
    filecmp.clear_cache()
    compared = filecmp.cmp(file_from_dump, file_from_drive, shallow=False)
    return compared


def upload_file_to_google_drive(filename):
    drive = authenticate()
    upload_files_in_folder(drive, BACKUP_FOLDER_NAME, filename)
    delete_obsolete_files(drive, BACKUP_FOLDER_NAME)
