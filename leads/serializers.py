from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ["id", "user_id", "name", "interested_product", "platform", "date"]
        read_only_fields = ["id", "date"]
