from rest_framework import serializers

# Generic response Serializer
class GenericResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    data = serializers.JSONField(required=False)
    success = serializers.BooleanField(required=True)
    latest_version = serializers.IntegerField(required=False)
    acceptable_version = serializers.IntegerField(required=False)
