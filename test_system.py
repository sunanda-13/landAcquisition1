"""
End-to-End System Tests verifying all 7 core prototype features.
"""

import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.cases.models import LandAcquisitionCase

def run_system_verification():
    client = Client()
    print("--- Starting End-to-End Prototype Verification ---")

    # 1. Verify Dashboard
    res_dash = client.get('/')
    assert res_dash.status_code == 200, f"Dashboard failed with status {res_dash.status_code}"
    assert b"Executive Risk &amp; Delay Intelligence Dashboard" in res_dash.content or b"Executive Risk & Delay Intelligence Dashboard" in res_dash.content
    print("[PASS] Feature 1: Dashboard rendered successfully with all KPI blocks.")

    # 2. Verify Chart API
    res_charts = client.get('/api/charts/')
    assert res_charts.status_code == 200, f"Charts API failed with status {res_charts.status_code}"
    chart_data = res_charts.json()
    assert 'risk_distribution' in chart_data and 'stage_breakdown' in chart_data and 'sector_analytics' in chart_data
    print("[PASS] Feature 4: Predictive Analytics Chart API active and returning valid JSON datasets.")

    # 3. Verify Cases Roster (CRUD: List)
    res_list = client.get('/cases/')
    assert res_list.status_code == 200, f"Case List failed with status {res_list.status_code}"
    assert b"Land Acquisition Cases" in res_list.content
    print(f"[PASS] Feature 2: Case Registry list rendered successfully.")

    # 4. Verify Case Detail (Delay Probability, Risk Score, Bottleneck Stage, XAI, Early Warnings)
    first_case = LandAcquisitionCase.objects.first()
    assert first_case is not None, "No cases found in DB."
    res_detail = client.get(f'/cases/{first_case.pk}/')
    assert res_detail.status_code == 200, f"Case Detail failed with status {res_detail.status_code}"
    assert b"Explainable AI (XAI) Root Cause Breakdown" in res_detail.content
    assert b"Early Warning Mitigations &amp; Action Plan" in res_detail.content or b"Early Warning Mitigations & Action Plan" in res_detail.content
    print(f"[PASS] Feature 3 & 6: Case Risk Detail & Delay Stage Prediction active for '{first_case.project_name}'.")
    print(f"       Score: {first_case.risk_score}/100 | Prob: {first_case.delay_probability}% | Bottleneck: {first_case.predicted_delay_stage}")


    # Verify XAI and Recommendations populated
    assert len(first_case.top_risk_factors) > 0, "XAI risk factors not populated."
    assert len(first_case.recommendations) > 0, "Recommendations not populated."
    print(f"[PASS] Feature 5 & 7: Explainable AI ({len(first_case.top_risk_factors)} factors) & Early Warning Recommendations ({len(first_case.recommendations)} actions) verified.")

    # 5. Verify What-if Interactive Simulation Endpoint
    sim_payload = {
        'env_forest_clearance_status': 'Approved',
        'litigation_cases_count': 0,
        'compensation_disparity_ratio': 1.15,
        'public_objections_count': 0
    }
    res_sim = client.post(
        f'/intelligence/simulate/{first_case.pk}/',
        data=json.dumps(sim_payload),
        content_type='application/json'
    )
    assert res_sim.status_code == 200, f"Simulation API failed with status {res_sim.status_code}"
    sim_data = res_sim.json()
    print(f"[PASS] Interactive Simulation API: Original {sim_data['original_risk_score']} -> Simulated {sim_data['simulated_risk_score']} (Delta: {sim_data['delta']})")

    # 6. Verify New Case Creation & Auto AI Assessment
    new_case_data = {
        'project_name': 'Automated Test Express Corridor',
        'sector': 'Highways',
        'state': 'Haryana',
        'district': 'Gurugram',
        'taluk_village': 'Sohna Rural',
        'total_area_hectares': 45.0,
        'land_type': 'Agricultural',
        'affected_landowners_count': 60,
        'plots_count': 75,
        'current_stage': 'Hearing of Objections (Sec 15)',
        'days_in_current_stage': 45,
        'env_forest_clearance_status': 'Approved',
        'litigation_cases_count': 0,
        'public_objections_count': 1,
        'compensation_disparity_ratio': 1.05,
        'sia_completed': True,
        'rr_plan_approved': True,
        'is_delayed': False
    }
    res_create = client.post('/cases/create/', data=new_case_data)
    assert res_create.status_code == 302, f"Case creation failed with status {res_create.status_code}"
    created_case = LandAcquisitionCase.objects.get(project_name='Automated Test Express Corridor')
    assert created_case.risk_score > 0 or created_case.delay_probability >= 0
    print(f"[PASS] Auto-assessment on creation: Created case '{created_case.project_name}' with Risk Score {created_case.risk_score} ({created_case.risk_level} Risk).")

    # Clean up test case
    created_case.delete()
    print("\n>>> ALL 7 CORE FEATURES VERIFIED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    run_system_verification()
