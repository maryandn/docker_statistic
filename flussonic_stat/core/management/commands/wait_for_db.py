from django.core.management import BaseCommand
from django.db import connection, OperationalError
import subprocess
import time
import os

from app.settings import DB_NAME_PRODUCTIONS, MYSQL_USER_PRODUCTIONS, MYSQL_PASSWORD_PRODUCTIONS


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('wait for db....')
        db_con = False
        while not db_con:
            try:
                connection.ensure_connection()
                db_con = True
            except OperationalError:
                self.stdout.write('Database unavailable, wait one sec....')
                time.sleep(1)
        self.stdout.write('Database connected!!!')

        self.restore_database()

    def restore_database(self):
        database_name = DB_NAME_PRODUCTIONS
        backup_file = '/backup/backup.sql'
        mysql_user = MYSQL_USER_PRODUCTIONS
        mysql_password = MYSQL_PASSWORD_PRODUCTIONS

        if not os.path.exists(backup_file):
            self.stdout.write(f'Backup file not found: {backup_file}')
            return

        try:
            # os.system(f'mysql -h db03 -u {mysql_user} -p{mysql_password} {database_name} < {backup_file}')
            command = [
                'mysql', '-h', 'db03', '-u', mysql_user,
                f'--password={mysql_password}'
            ]

            with open(backup_file, 'r') as file:
                subprocess.run(command, stdin=file, check=True)

            self.stdout.write(f'Database restored successfully from {backup_file}')
        except Exception as e:
            self.stdout.write(f'Error occurred during database restore: {str(e)}')
