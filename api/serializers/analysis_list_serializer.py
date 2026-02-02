from rest_framework import serializers
from analysis.models import AnalysisModel


class AnalysisListSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(
        source='get_status_analysis_display',
        read_only=True
    )
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisModel
        fields = [
            'id',
            'title',
            'organization',
            'status_analysis',
            'status_label',
            'progress_percentage',
            'slug',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_progress_percentage(self, obj):
        completed = sum([
            bool(obj.workshop1_data),
            bool(obj.workshop2_data),
            bool(obj.workshop3_data),
            bool(obj.workshop4_data),
            bool(obj.workshop5_data),
        ])
        return int((completed / 5) * 100)
