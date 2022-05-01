from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction


def union(contributors_1, contributors_2):
    contributors = set(contributors_1)
    contributors.update(contributors_2)
    return list(contributors)


class WorkFile(models.Model):
    """Will be used to automate ingestion. If a files"""
    name = models.CharField(max_length=1024, null=False, blank=False)
    checksum_str = models.CharField(max_length=2056, null=False, blank=False, unique=True)
    size = models.IntegerField(default=0)
    ingested = models.BooleanField(default=False)


class RawWork(models.Model):
    """
    Helper Class - will store the direct data given from the sources
    f.e in case some checks need to be made
    """
    title = models.CharField(max_length=1024, null=False, blank=False)
    contributors = ArrayField(base_field=models.CharField(max_length=1024))
    iswc = models.CharField(max_length=11, null=True, blank=True)
    issues = models.BooleanField(default=False)
    errors = models.CharField(max_length=2056, null=True, blank=True)
    file = models.ForeignKey(to=WorkFile, null=True, on_delete=models.SET_NULL)
    processed = models.BooleanField(default=False)

    @transaction.atomic
    def process(self):
        """Atomic process, if some error reset back"""
        """Its places inside the raw data because it made sense that the logic is in this instance instead of the arg
        for better testing f.e"""
        """Logic
        1) checks if there is an existing work with the raw iswc 
        a) if there is - update contributors as union
        b) if not :
                    b1) Check if there is a work with title match, contributors intersection exists 
                    (either a in b or b in a) and iswc empty . 
                    Update iswc for that Work and union contributors.
                    b2) If not above , create a new Work from the RawData
        2) if no raw iswc : Check if there is a Work with equal title and contributor intersection exits.
            a) if this work exists, update contributors to union of existing work
            b) if this work doesnt exist create new Work from RawData
        """

        iswc = self.iswc
        if Work.objects.filter(iswc=iswc) and iswc:
            """ 
            Didn't know how to process titles. Not defined in requirement.
            If titles equal - no problem
            if different i am just adding a titles different to error. Not a hard error because i allow the procedure.
            Just basically logs a small issue in the RawData.
            """
            existing_work = Work.objects.filter(iswc=iswc)[0]
            existing_work.contributors = union(self.contributors, existing_work.contributors)
            existing_work.save()
            if existing_work.title != self.title:
                self.errors = "Titles are different for same iswc."
                self.save()
        elif iswc:
            possible_works = Work.objects.filter(title=self.title, iswc="", contributors__overlap=self.contributors)
            if possible_works.count() > 1:
                self.errors = "More then 1 work already exists with the same title and overlapping contributors." \
                              "System doesn't know how to process."
                """here if we knew more about the structure, role etc we could add logic.
                F.e we could check that the contributors singer (if we would have role f.e) is exact then thats the 
                source of truth."""
            elif possible_works.count() == 1:
                existing_work = possible_works[0]
                existing_work.contributors = union(self.contributors, existing_work.contributors)
                existing_work.iswc = self.iswc
                existing_work.save()
            else:
                self.create_work()
        else:
            possible_works = Work.objects.filter(title=self.title, contributors__overlap=self.contributors)
            if possible_works.count() > 1:
                self.errors = "More then 1 work already exists with the same title and overlapping contributors." \
                              "System doesn't know how to process."
            elif possible_works.count() == 1:
                existing_work = possible_works[0]
                existing_work.contributors = union(self.contributors, existing_work.contributors)
                existing_work.save()
            else:
                self.create_work()
        self.processed = True
        self.save()

    def create_work(self):
        try:
            return Work.objects.create(title=self.title, contributors=self.contributors, iswc=self.iswc, raw_data=self)
        except Exception as e:
            self.errors = e


class Work(models.Model):
    """
    Assumption : Title is Mandatory
    Contributors - Since its Postgres i am going to use ArrayField
    """
    title = models.CharField(max_length=1024, null=False, blank=False)
    contributors = ArrayField(base_field=models.CharField(max_length=1024))
    iswc = models.CharField(max_length=11, null=True, blank=True, unique=True, db_index=True)
    raw_data = models.ForeignKey(to=RawWork, on_delete=models.SET_NULL, null=True, related_name="work")
