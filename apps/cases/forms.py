from django import forms
from .models import LandAcquisitionCase

class LandAcquisitionCaseForm(forms.ModelForm):
    class Meta:
        model = LandAcquisitionCase
        fields = [
            'project_name', 'sector', 'state', 'district', 'taluk_village',
            'total_area_hectares', 'land_type', 'affected_landowners_count', 'plots_count',
            'current_stage', 'days_in_current_stage', 'env_forest_clearance_status',
            'litigation_cases_count', 'public_objections_count',
            'compensation_disparity_ratio', 'sia_completed', 'rr_plan_approved',
            'is_delayed'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nagpur-Mumbai Expressway Package 4'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}),
            'taluk_village': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Taluk / Tehsil / Villages'}),
            'total_area_hectares': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.1'}),
            'land_type': forms.Select(attrs={'class': 'form-select'}),
            'affected_landowners_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'plots_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'current_stage': forms.Select(attrs={'class': 'form-select'}),
            'days_in_current_stage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'env_forest_clearance_status': forms.Select(attrs={'class': 'form-select'}),
            'litigation_cases_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'public_objections_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'compensation_disparity_ratio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.1', 'max': '3.0'}),
            'sia_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rr_plan_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_delayed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
