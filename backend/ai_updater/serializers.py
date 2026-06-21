from rest_framework import serializers


class AIUpdateResumeResponseSerializer(serializers.Serializer):
    updated_resume = serializers.DictField()
    changes_made = serializers.ListField(child=serializers.CharField())
