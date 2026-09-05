import uuid
from django.db import models
from django.urls import reverse

SECTORS = [
    ('Highways', 'Highways & Expressways'),
    ('Railways', 'Railways & Dedicated Freight Corridors'),
    ('Urban Infrastructure', 'Urban Infrastructure & Metro'),
    ('Irrigation', 'Irrigation & Water Resources'),
    ('Energy', 'Energy, Power & Transmission'),
    ('Industrial', 'Industrial Corridors & SEZ'),
]

LAND_TYPES = [
    ('Agricultural', 'Agricultural Land'),
    ('Forest', 'Forest & Protected Land'),
    ('Residential', 'Residential / Homestead'),
    ('Commercial', 'Commercial / Semi-Urban'),
    ('Government/Barren', 'Government / Barren Land'),
]

STAGES = [
    ('Survey & Demarcation', '1. Survey & Demarcation'),
    ('Preliminary Notification (Sec 11)', '2. Preliminary Notification (Sec 11)'),
    ('Hearing of Objections (Sec 15)', '3. Hearing of Objections (Sec 15)'),
    ('Declaration of Acquisition (Sec 19)', '4. Declaration of Acquisition (Sec 19)'),
    ('Award & Compensation (Sec 23)', '5. Award & Compensation (Sec 23)'),
    ('R&R Implementation', '6. R&R Implementation'),
    ('Physical Possession', '7. Physical Possession'),
]

CLEARANCE_STATUS = [
    ('Approved', 'Approved / Secured'),
    ('Pending', 'Pending Review / Submission'),
    ('Rejected', 'Rejected / Queries Raised'),
    ('Not Applicable', 'Not Applicable'),
]

RISK_LEVELS = [
    ('Low', 'Low Risk'),
    ('Medium', 'Medium Risk'),
    ('High', 'High Risk'),
]

WARNING_SEVERITIES = [
    ('LOW', 'Low Severity (Normal)'),
    ('MODERATE', 'Moderate Severity (Attention Required)'),
    ('HIGH', 'High Severity (Action Required)'),
    ('CRITICAL', 'Critical Severity (Urgent Escalation)'),
]

class LandAcquisitionCase(models.Model):
    # Identification
    case_number = models.CharField(max_length=50, unique=True, blank=True)
    project_name = models.CharField(max_length=255, verbose_name="Project / Stretch Name")
    sector = models.CharField(max_length=50, choices=SECTORS, default='Highways')
    
    # Location
    state = models.CharField(max_length=100, default='Maharashtra')
    district = models.CharField(max_length=100)
    taluk_village = models.CharField(max_length=150, verbose_name="Taluk / Village / Tehsil")

    # Scope & Land Characteristics
    total_area_hectares = models.FloatField(verbose_name="Total Land Area (Hectares)", default=10.0)
    land_type = models.CharField(max_length=50, choices=LAND_TYPES, default='Agricultural')
    affected_landowners_count = models.PositiveIntegerField(verbose_name="Affected Landowners", default=25)
    plots_count = models.PositiveIntegerField(verbose_name="Number of Survey Plots / Survey Nos.", default=30)

    # Process Progression
    current_stage = models.CharField(max_length=100, choices=STAGES, default='Survey & Demarcation')
    days_in_current_stage = models.PositiveIntegerField(verbose_name="Days in Current Stage", default=15)

    # Key Risk & Friction Indicators
    env_forest_clearance_status = models.CharField(
        max_length=50, choices=CLEARANCE_STATUS, default='Approved', verbose_name="Env / Forest Clearance"
    )
    litigation_cases_count = models.PositiveIntegerField(
        default=0, verbose_name="Active Court Stays / Litigations"
    )
    public_objections_count = models.PositiveIntegerField(
        default=0, verbose_name="Public / Gram Sabha Objections"
    )
    compensation_disparity_ratio = models.FloatField(
        default=1.0,
        verbose_name="Compensation Ratio (Offered vs Market Rate)",
        help_text="1.00 = Market parity. Values below 0.85 indicate severe landowner dissatisfaction."
    )
    sia_completed = models.BooleanField(
        default=True, verbose_name="Social Impact Assessment (SIA) Completed"
    )
    rr_plan_approved = models.BooleanField(
        default=True, verbose_name="R&R Scheme Approved under Sec 16"
    )

    # ML Output & Persisted Risk Intelligence
    is_delayed = models.BooleanField(default=False, verbose_name="Currently Delayed")
    delay_probability = models.FloatField(default=0.0, verbose_name="Delay Probability (%)")
    risk_score = models.PositiveIntegerField(default=0, verbose_name="Risk Score (0-100)")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='Low')
    predicted_delay_stage = models.CharField(max_length=100, blank=True, default='None')
    top_risk_factors = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    warning_severity = models.CharField(max_length=20, choices=WARNING_SEVERITIES, default='LOW')
    last_assessed_at = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_score', '-updated_at']
        verbose_name = "Land Acquisition Case"
        verbose_name_plural = "Land Acquisition Cases"

    def __str__(self):
        return f"[{self.case_number or 'DRAFT'}] {self.project_name} ({self.risk_level} Risk)"

    def get_absolute_url(self):
        return reverse('case_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.case_number:
            self.case_number = f"LA-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def to_ml_dict(self):
        """Prepares raw case data for ML inference."""
        return {
            'sector': self.sector,
            'land_type': self.land_type,
            'current_stage': self.current_stage,
            'env_forest_clearance_status': self.env_forest_clearance_status,
            'total_area_hectares': self.total_area_hectares,
            'affected_landowners_count': self.affected_landowners_count,
            'plots_count': self.plots_count,
            'days_in_current_stage': self.days_in_current_stage,
            'litigation_cases_count': self.litigation_cases_count,
            'public_objections_count': self.public_objections_count,
            'compensation_disparity_ratio': self.compensation_disparity_ratio,
            'sia_completed': 1 if self.sia_completed else 0,
            'rr_plan_approved': 1 if self.rr_plan_approved else 0,
        }

    def run_risk_assessment(self):
        """Runs the ML assessment engine and stores intelligence fields."""
        from ml_engine.predict import assess_case_risk
        
        result = assess_case_risk(self.to_ml_dict())
        self.delay_probability = result['delay_probability']
        self.risk_score = result['risk_score']
        self.risk_level = result['risk_level']
        self.predicted_delay_stage = result['predicted_delay_stage']
        self.top_risk_factors = result['top_risk_factors']
        self.recommendations = result['recommendations']
        self.warning_severity = result['warning_severity']
        self.is_delayed = bool(self.risk_score >= 50 or self.days_in_current_stage > 120)
        self.save(update_fields=[
            'delay_probability', 'risk_score', 'risk_level',
            'predicted_delay_stage', 'top_risk_factors',
            'recommendations', 'warning_severity', 'is_delayed',
            'last_assessed_at'
        ])
        return result
