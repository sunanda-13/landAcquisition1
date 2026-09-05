"""
Test verification script for ML inference, XAI, and early warning recommendation engine.
"""

from ml_engine.predict import assess_case_risk

def test_predictions():
    # Scenario 1: High Risk Project (Litigation + Forest Clearance bottleneck)
    high_risk_case = {
        'sector': 'Highways',
        'land_type': 'Forest',
        'current_stage': 'Hearing of Objections (Sec 15)',
        'env_forest_clearance_status': 'Pending',
        'total_area_hectares': 120.0,
        'affected_landowners_count': 320,
        'plots_count': 410,
        'days_in_current_stage': 210,
        'litigation_cases_count': 4,
        'public_objections_count': 12,
        'compensation_disparity_ratio': 0.62,
        'sia_completed': False,
        'rr_plan_approved': False,
    }

    # Scenario 2: Low Risk Smooth Project
    low_risk_case = {
        'sector': 'Energy',
        'land_type': 'Government/Barren',
        'current_stage': 'Declaration of Acquisition (Sec 19)',
        'env_forest_clearance_status': 'Approved',
        'total_area_hectares': 30.0,
        'affected_landowners_count': 15,
        'plots_count': 18,
        'days_in_current_stage': 35,
        'litigation_cases_count': 0,
        'public_objections_count': 0,
        'compensation_disparity_ratio': 1.15,
        'sia_completed': True,
        'rr_plan_approved': True,
    }

    print("=== SCENARIO 1: HIGH RISK CASE ===")
    res_high = assess_case_risk(high_risk_case)
    print(f"Delay Probability: {res_high['delay_probability']}%")
    print(f"Risk Score: {res_high['risk_score']} / 100 ({res_high['risk_level']} Risk)")
    print(f"Warning Severity: {res_high['warning_severity']}")
    print(f"Predicted Bottleneck Stage: {res_high['predicted_delay_stage']}")
    print(f"Top Contributing Factors ({len(res_high['top_risk_factors'])}):")
    for f in res_high['top_risk_factors'][:3]:
        print(f"  - [{f['impact_type']}] {f['factor']} (+{f['impact_score']}): {f['description']}")
    print(f"Recommendations ({len(res_high['recommendations'])}):")
    for r in res_high['recommendations'][:2]:
        print(f"  * [{r['urgency']}] {r['category']}: {r['action']}")

    print("\n=== SCENARIO 2: LOW RISK CASE ===")
    res_low = assess_case_risk(low_risk_case)
    print(f"Delay Probability: {res_low['delay_probability']}%")
    print(f"Risk Score: {res_low['risk_score']} / 100 ({res_low['risk_level']} Risk)")
    print(f"Warning Severity: {res_low['warning_severity']}")
    print(f"Predicted Bottleneck Stage: {res_low['predicted_delay_stage']}")
    print("Verification completed successfully!")

if __name__ == '__main__':
    test_predictions()
