"""
this file will hold the cron jobs
This functions will be called from a rabbit mq at a frequency defined by the user.

delete f.e can be weekly while ingest hourly
"""
import glob
import os
from django.core.management import call_command

from bmat.settings import CSV_FOLDER_POSITION
from works.models import WorkFile, Work, RawWork
import hashlib


def calculate_checksum(file):
    return hashlib.md5(file.read().encode()).hexdigest()


def ingest():
    """Using ingest command to reuse logic."""
    call_command("ingest")


def delete_ingested():
    """
    On the folder deletes all files who's names and hash matches with existing rows.
    Using hash and name and ingested as check to make absolutely sure no important file is deleted.
    """
    path = CSV_FOLDER_POSITION
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    for csv_file in csv_files:
        file = open(csv_file)
        checksum_str = calculate_checksum(file)
        file_name = csv_file.split("/")[-1]
        if WorkFile.objects.filter(name=file_name, ingested=True, checksum_str=checksum_str):
            os.remove(csv_file)


def print_data():
    print("FILES")
    print("Name\tChecksum\tSize\tIngested")
    for row in WorkFile.objects.all():
        print(row.name, row.checksum_str, row.size, row.ingested)

    print("RAW WORKS")
    print("Title\tContributors\tISWC\tIssues\tErrors\tFile Name\t Processed")
    for row in RawWork.objects.all():
        print(row.title, row.contributors, row.iswc, row.issues, row.errors, row.file.name, row.processed)

    print("WORKS")
    print("Title\tContributors\tISWC\tRaw")
    for row in Work.objects.all():
        print(row.title, row.contributors, row.iswc, row.raw_data.title)


def clean():
    print(Work.objects.all().delete())
    print(WorkFile.objects.all().delete())
    print(RawWork.objects.all().delete())


def create_on_mass(reps=15000000):
    from random import randrange
    partitions = 500
    for i in range(0, partitions):
        print("REP", i)
        bulk_works = []
        for j in range(0, reps//partitions):
            bulk_works.append(Work(
                title="Title" + str(i),
                contributors=[i, i - 1, i + 1],
                iswc="T" + str(randrange(100, 1000)) + str(randrange(100, 1000)) + str(randrange(100, 1000)),
            ))

        Work.objects.bulk_create(bulk_works, ignore_conflicts=True)
