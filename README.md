# MySqltoGoogleDriveBackupper

Helm chart for making periodical backups for all tables on MariaDB or MySQL host running in Kubernetes into your Google Drive.

It is useful if you are running bare-metal k8s cluster but still want to backup your DB data in the cloud.

## Usage

To be able to access the Google Drive API you have to have a credentials file called client_secrets.json.

How to get it is described in this [tutorial](https://medium.com/analytics-vidhya/pydrive-to-download-from-google-drive-to-a-remote-machine-14c2d086e84e).
After downloading the client_secrets.json, place it into the root folder of this project.

That's it, just deploy the chart with adopted values.yaml via:

**helm install mysqltogoogledrivebackupper -f values.yaml .**

## values.yaml

| Parameter                | Description                                                                    |      Default       |
| ------------------------ | :----------------------------------------------------------------------------- | :----------------: |
| google_drive.folder_name | Name of the folder in Google Drive where backups will be stored.               |   mariadb_backup   |
| google_drive.backup_name | Name of the backup file that will be stored in Google Drive.                   | mariadb-backup.sql |
| google_drive.your_email  | Must be Gmail E-Mail, to give you the possibility to access the backup folder. |   user@gmail.com   |
| mysql.db_user            | User name to access your MySQL or MariaDb instance.                            |        user        |
| mysql.db_password        | Password to access your MySQL or MariaDb instance.                             |      password      |
| mysql.db_port            | Port to access your MySQL or MariaDb instance.                                 |        3306        |
| backup.croninterval      | Interval how oft should backup be triggered.                                   |  every two hours   |
| backup.backups_to_keep   | how many backup files should be kept by Google Drive.                          |         5          |
