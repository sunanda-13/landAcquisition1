"""
Intelligence Service bridging Django ORM with the ml_engine.
"""

from ml_engine.predict import assess_case_risk

def run_case_intelligence(case):
    """
    Evaluates risk and updates case instance.
    """
    return case.run_risk_assessment()

def simulate_what_if(case, overrides):
    """
    Runs an ephemeral what-if risk simulation without mutating the stored database record.
    Useful for interactive scenario testing (e.g. 'What if Forest Clearance is granted?',
    'What if compensation ratio is raised to 1.1?').
    """
    base_data = case.to_ml_dict()
    # Apply overrides
    for key, value in overrides.items():
        if key in base_data:
            # Cast according to type
            if key in ['total_area_hectares', 'compensation_disparity_ratio']:
                base_data[key] = float(value)
            elif key in ['affected_landowners_count', 'plots_count', 'days_in_current_stage', 'litigation_cases_count', 'public_objections_count', 'sia_completed', 'rr_plan_approved']:
                base_data[key] = int(value)
            else:
                base_data[key] = str(value)

    simulation_result = assess_case_risk(base_data)
    return {
        'original_risk_score': case.risk_score,
        'simulated_risk_score': simulation_result['risk_score'],
        'delta': simulation_result['risk_score'] - case.risk_score,
        'simulated_result': simulation_result
    }
