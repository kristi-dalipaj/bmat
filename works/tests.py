import csv
import json
import os

from rest_framework import status
from rest_framework.test import APITestCase

from bmat.settings import CSV_FOLDER_POSITION
from works.models import Work, WorkFile
from works.utils import create_on_mass


class EventTestCase(APITestCase):

    def test_ingest(self):
        filename = CSV_FOLDER_POSITION + "/test_file_ingest.csv"
        header = ["title", "contributors", "iswc"]
        works_data = [
            ["Shape of You", "Edward Christopher Sheeran", "T9204649558"],
            ["Adventure of a Lifetime",
             "O Brien Edward John|Yorke Thomas Edward|Greenwood Colin Charles",
             "T0101974597"],
            ["Adventure of a Lifetime",
             "O Brien Edward John|Selway Philip James",
             "T0101974597"],
            ["Me EnamorÃ©",
             "Rayo Gibo Antonio|Ripoll Shakira Isabel Mebarak",
             "T9214745718"],
            ["Je ne sais pas",
             "Obispo Pascal Michel|Florence Lionel Jacques",
             ""],
            ["Je ne sais pas",
             "Obispo Pascal Michel|Florence Lionel Jacques",
             "T0046951705"],
        ]
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, delimiter=',', fieldnames=header)
            writer.writeheader()
            for row in works_data:
                writer.writerow({
                    header[0]: row[0],
                    header[1]: row[1],
                    header[2]: row[2]
                })
        results = {
            "T9204649558": ["Shape of You", ["Edward Christopher Sheeran"]],
            "T0101974597": ["Adventure of a Lifetime",
                            ["O Brien Edward John",
                             "Yorke Thomas Edward",
                             "Greenwood Colin Charles",
                             "Selway Philip James"]],
            "T9214745718": ["Me EnamorÃ©",
                            ["Rayo Gibo Antonio",
                             "Ripoll Shakira Isabel Mebarak"
                             ]],
            "T0046951705": ["Je ne sais pas",
                            ["Obispo Pascal Michel",
                             "Florence Lionel Jacques"
                             ]],

        }
        work_file = WorkFile.objects.create_from_file_name(filename)
        self.assertEqual(work_file.name, "test_file_ingest.csv")
        self.assertEqual(work_file.ingested, True)

        raw_works = work_file.rawwork_set.all()
        self.assertEqual(raw_works.count(), 6)  # 6 raw lines
        self.assertEqual(Work.objects.all().count(), 4)
        for work in Work.objects.all():
            self.assertIn(work.iswc, results)
            self.assertEqual(work.title, results.get(work.iswc)[0])
            self.assertCountEqual(work.contributors, results.get(work.iswc)[1])

        os.remove(filename)

    def test_enrich(self):
        """uses create_on_mass from utils"""
        """
        creates 100 Works
        gets the iscw of the first 10
        tests enrich with just those 10 iscw
        test enrich with those 10 iscw + not_found_ids
        test enrich with not_found_ids
        """
        create_on_mass(100, 10)
        iswc_ids = set(Work.objects.all()[0:10].values_list('iswc', flat=True))

        response = self.client.post(path="http://0.0.0.0:8000/work/enrich/",
                                    data=json.dumps({
                                        'iswc': list(iswc_ids)
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'Enrichment complete')
        for enriched in response.data.get('data'):
            iswc = enriched.get('iswc')
            contributors = enriched.get('contributors')
            self.assertListEqual(Work.objects.get(iswc=iswc).contributors,
                                 contributors)

        not_found_ids = {"111", "222", "333"}
        response = self.client.post(
            path="http://0.0.0.0:8000/work/enrich/",
            data=json.dumps({
                'iswc': list(iswc_ids.union(not_found_ids))
            }),
            content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        error_message = "Enrichment complete. Some ISWC where not found " \
                        "in database. " \
                        "Missing ISWCS : ['111', '222', '333']"
        self.assertEqual(response.data.get('message'), error_message)
        for enriched in response.data.get('data'):
            iswc = enriched.get('iswc')
            contributors = enriched.get('contributors')
            self.assertListEqual(Work.objects.get(iswc=iswc).contributors,
                                 contributors)

        response = self.client.post(path="http://0.0.0.0:8000/work/enrich/",
                                    data=json.dumps({
                                        'iswc': list(not_found_ids)
                                    }),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), error_message)
        self.assertEqual(response.data.get('data'), [])
