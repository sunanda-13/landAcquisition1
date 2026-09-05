from django.contrib import admin
from .models import LandAcquisitionCase

@admin.register(LandAcquisitionCase)
class LandAcquisitionCaseAdmin(admin.ModelAdmin):
    list_display = (
        'case_number', 'project_name', 'sector', 'district',
        'current_stage', 'risk_score', 'risk_level', 'delay_probability',
        'predicted_delay_stage', 'is_delayed', 'updated_at'
    )
    list_filter = ('risk_level', 'sector', 'current_stage', 'is_delayed', 'env_forest_clearance_status')
    search_fields = ('case_number', 'project_name', 'district', 'taluk_village')
    readonly_fields = (
        'case_number', 'delay_probability', 'risk_score', 'risk_level',
        'predicted_delay_stage', 'top_risk_factors', 'recommendations',
        'warning_severity', 'last_assessed_at', 'created_at', 'updated_at'
    )
