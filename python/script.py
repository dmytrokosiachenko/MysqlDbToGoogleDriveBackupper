import os
import sys

from googledrive import upload_file_to_google_drive

# Get environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

BACKUP_NAME = os.getenv('BACKUP_NAME')

if not DB_USER:
    sys.exit("No db user defined")

if not DB_PASSWORD:
    sys.exit("No db password defined")

if not DB_HOST:
    sys.exit("No db host defined")

print(f"Starting backup creation for {DB_HOST} to {BACKUP_NAME} ...")

os.system(f"mysqldump --user={DB_USER} --password={DB_PASSWORD} --host={DB_HOST} --all-databases > {BACKUP_NAME}")

print("Backup of db tables was created.")
print("Starting uploading to Google Drive.")

upload_file_to_google_drive(filename=BACKUP_NAME)

print("Upload to Google Drive is done.")
print("Backup is done.")
