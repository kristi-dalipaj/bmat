from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from works.models import Work
from works.serializers import WorkSerializer, WorkEnrichSerializer
from rest_framework import viewsets


class WorkViewSet(viewsets.ModelViewSet):
    """
    Using viewset because we might want to create works from api
    and also allows gets/lists/deletes/updates
    """
    serializer_class = WorkSerializer
    queryset = Work.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], name='Enrich ISWC')
    def enrich(self, request, *args, **kwargs):
        def missing_codes(codes, works_qs):
            """Finds missing elements"""
            set_codes = set(codes)
            set_iswc = set(works_qs.values_list('iswc', flat=True))
            return str(sorted(list(set_codes - set_iswc)))

        def clean(data):
            return [el for el in data if el]

        iswcs = request.data.get("iswc", [])
        iswcs = clean(iswcs)
        works = Work.objects.filter(iswc__in=iswcs)
        message = "Enrichment complete" if len(works) == len(iswcs) else \
            "Enrichment complete. Some ISWC where not found in database. " \
            "Missing ISWCS : " + missing_codes(iswcs, works)

        return Response({
            "data": WorkEnrichSerializer(works, many=True).data,
            "message": message
        })
