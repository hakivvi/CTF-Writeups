from rest_framework import serializers
from .models import Experience, WebFramework

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'owner', 'web_framework', 'text', 'hot', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at', 'hot']

    def create(self, validated_data):
        if len(validated_data["text"]) < 50:
            raise serializers.ValidationError({"error": "text too short, 50 chars minimum."})
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class WebFrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebFramework
        fields = ['id', 'name', 'icon']