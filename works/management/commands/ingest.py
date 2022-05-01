import glob
import os
from django.core.management.base import BaseCommand
import csv
from bmat.settings import CSV_FOLDER_POSITION, SPLITTER
from works.models import RawWork, WorkFile
from works.utils import calculate_checksum


class Command(BaseCommand):
    help = 'Ingests the csv file provided in the directory. Has to be a correct directory, in the same ' \
           'depth as manage.py.'

    def handle(self, *args, **options):
        path = CSV_FOLDER_POSITION
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        for csv_file in csv_files:
            file = open(csv_file)
            csv_reader = csv.DictReader(file, restval="")

            checksum_str = calculate_checksum(file)
            work_file, created = WorkFile.objects.get_or_create(checksum_str=checksum_str,
                                                                defaults={
                                                                    'name': csv_file.split('/')[-1],
                                                                    'size': os.path.getsize(csv_file),
                                                                })
            if not created:
                """makes sure it isn't recreated"""
                continue

            file.seek(0)  # Resets file seek because the checksum calc has moved it to the end
            for row in csv_reader:
                row['contributors'] = row['contributors'].split(SPLITTER)
                RawWork.objects.create(file=work_file, **row)

            for raw_object in RawWork.objects.filter(processed=False):
                raw_object.process()

            work_file.ingested = True
            work_file.save()
