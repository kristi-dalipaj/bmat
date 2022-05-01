from rest_framework import serializers

from works.models import Work


class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ['title', 'contributors', 'iswc']


class WorkEnrichSerializer(serializers.Serializer):
    iswc = serializers.CharField(required=True)
    contributors = serializers.ListField(child=serializers.CharField())
