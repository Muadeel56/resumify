from rest_framework import serializers


class AIUpdateResumeSerializer(serializers.Serializer):
    resume_text = serializers.CharField(min_length=1, max_length=50000)
    instructions = serializers.CharField(min_length=1, max_length=5000)


class AIUpdateResumeResponseSerializer(serializers.Serializer):
    updated_resume = serializers.DictField()
    changes_made = serializers.ListField(child=serializers.CharField())
