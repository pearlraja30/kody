# -*- coding: utf-8 -*-
"""
Database Backup Management Command for Kodys Application.

Usage:
    python manage.py db_backup
    python manage.py db_backup --output /path/to/backup/
"""
from __future__ import unicode_literals
import os
import shutil
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a backup of the SQLite database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='',
            help='Output directory for the backup file (default: same directory as DB)'
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']

        if not os.path.exists(db_path):
            self.stderr.write(self.style.ERROR('Database not found at: %s' % db_path))
            return

        # Determine output directory
        output_dir = options.get('output', '') or os.path.dirname(db_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create timestamped backup filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = 'db_backup_%s.sqlite3' % timestamp
        backup_path = os.path.join(output_dir, backup_filename)

        try:
            shutil.copy2(db_path, backup_path)
            file_size = os.path.getsize(backup_path)
            self.stdout.write(self.style.SUCCESS(
                'Backup created successfully!\n'
                '  Path: %s\n'
                '  Size: %s bytes\n'
                '  Time: %s' % (backup_path, file_size, timestamp)
            ))

            # Log to TX_DATABASEBACKUPLOGS if possible
            try:
                from kodys.models import TX_DATABASEBACKUPLOGS
                from django.contrib.auth.models import User
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    TX_DATABASEBACKUPLOGS.objects.create(
                        TYPE='MANUAL',
                        BACKUP_PATH=backup_path,
                        CREATED_BY=admin_user,
                        UPDATED_BY=admin_user
                    )
                    self.stdout.write('  Logged to TX_DATABASEBACKUPLOGS')
            except Exception as e:
                self.stdout.write('  Warning: Could not log backup: %s' % str(e))

        except Exception as e:
            self.stderr.write(self.style.ERROR('Backup failed: %s' % str(e)))
