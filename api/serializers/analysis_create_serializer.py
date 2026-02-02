from analysis.models import AnalysisModel
from rest_framework.serializers import ModelSerializer

class AnalysisCreateSerializer(ModelSerializer):
    class Meta:
        model = AnalysisModel
        exclude = [
            'workshop1_data',
            'workshop2_data',
            'workshop3_data',
            'workshop4_data',
            'workshop5_data',
            'slug',
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
