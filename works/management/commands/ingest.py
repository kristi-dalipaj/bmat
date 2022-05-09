import glob
import os
from django.core.management.base import BaseCommand
import csv
from bmat.settings import CSV_FOLDER_POSITION, SPLITTER
from works.models import RawWork, WorkFile
from works.utils import calculate_checksum


class Command(BaseCommand):
    help = 'Ingests the csv file provided in the directory. ' \
           'Directory is set in settings.py.'

    def handle(self, *args, **options):
        """ Custom Command to handle ingest. Retrieves all file from a settings defined path and processes them
        by creating and ingesting works."""
        path = CSV_FOLDER_POSITION
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        for csv_file in csv_files:
            try:
                WorkFile.objects.create_from_file_name(csv_file)
            except OSError as e:
                self.stdout.write(self.style.SUCCESS('File not found '
                                                     '"%s"' % csv_file))
                self.stdout.write(e)
