from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from works.models import Work
from works.serializers import WorkSerializer, WorkEnrichSerializer
from rest_framework import viewsets


class WorkViewSet(viewsets.ModelViewSet):
    """using a view set here because its scalable and we can have get or post methods in the future."""

    serializer_class = WorkSerializer
    queryset = Work.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], name='Enrich ISWC')
    def enrich(self, request, *args, **kwargs):
        def missing_info(codes, object_with_codes):
            """one of the costliest operations. Decided to add it for clarity for the user."""
            return str(list(set(codes) - set(object_with_codes.values_list('iswc', flat=True))))

        def clean(data):
            return [el for el in data if el]

        iswcs = request.data.get("iswc", [])
        iswcs = clean(iswcs)
        works = Work.objects.filter(iswc__in=iswcs)
        message = "Enrichment complete" if len(works) == len(iswcs) else \
            "Enrichment complete, but some ISWC where not found in database or were cleaned " \
            "before hand. Missing ISWCS : " + missing_info(iswcs, works)

        return Response({
            "data": WorkEnrichSerializer(works, many=True).data,
            "message": message
        })
