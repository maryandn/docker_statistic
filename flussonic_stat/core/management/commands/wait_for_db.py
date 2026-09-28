from django.core.management import BaseCommand
from django.db import connection, OperationalError
import subprocess
import time
import os

from app import settings
from app.settings import DB_NAME_PRODUCTIONS, MYSQL_USER_PRODUCTIONS, MYSQL_PASSWORD_PRODUCTIONS, \
    MYSQL_ROOT_PASSWORD_PRODUCTIONS


BACKUP_FILE = '/backup/backup.sql'


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('wait for db....')
        while True:
            try:
                connection.ensure_connection()
                break
            except OperationalError:
                self.stdout.write('Database unavailable, wait one sec....')
                time.sleep(1)
        self.stdout.write('Database connected!!!')

        if os.getenv('DB_RESTORE_ON_START') != '1':
            self.stdout.write('Restore on start disabled')
            return

        if connection.introspection.table_names():
            self.stdout.write('Database is not empty, restore skipped')
            return

        self.restore_database()

    def restore_database(self):
        if not os.path.exists(BACKUP_FILE):
            self.stdout.write(f'Backup file not found: {BACKUP_FILE}')
            return

        host = settings.DATABASES['default']['HOST']
        env = {**os.environ, 'MYSQL_PWD': MYSQL_ROOT_PASSWORD_PRODUCTIONS}

        with open(BACKUP_FILE, 'rb') as file:
            result = subprocess.run(['mysql', '-h', host, '-u', 'root'], stdin=file, env=env)

        if result.returncode == 0:
            self.stdout.write(f'Database restored successfully from {BACKUP_FILE}')
        else:
            self.stdout.write(f'Database restore failed, exit code {result.returncode}')
