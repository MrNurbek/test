from apps.testupload.models import NewTestUpload
from rest_framework import serializers

class NewTestUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewTestUpload
        fields = ['category', 'topic_name', 'json_data']