from analysis.models import AnalysisModel
from rest_framework import serializers

class AnalysisDetailSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    status_label = serializers.CharField(
        source='get_status_analysis_display',
        read_only=True
    )
    class Meta:
        model = AnalysisModel
        fields = '__all__'
        read_only_fields = ['__all__']

    def get_progress_percentage(self, obj):
        completed = sum([
            bool(obj.workshop1_data),
            bool(obj.workshop2_data),
            bool(obj.workshop3_data),
            bool(obj.workshop4_data),
            bool(obj.workshop5_data),
        ])
        return int((completed / 5) * 100)

