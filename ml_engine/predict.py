"""
Predictive Land Acquisition Delay & Risk Inference Interface.
Integrates trained ML models, Explainable AI (XAI), and Recommendation Engines.
"""

import os
import joblib
import pandas as pd
from .explainer import explain_prediction
from .recommender import generate_recommendations

_MODELS_CACHE = {}

def get_artifacts():
    """Lazy-loads and caches model artifacts."""
    if not _MODELS_CACHE:
        artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        delay_path = os.path.join(artifacts_dir, 'delay_model.joblib')
        stage_path = os.path.join(artifacts_dir, 'stage_model.joblib')
        meta_path = os.path.join(artifacts_dir, 'feature_meta.joblib')

        if not (os.path.exists(delay_path) and os.path.exists(stage_path)):
            raise FileNotFoundError("Trained models not found. Please run ml_engine/train.py first.")

        _MODELS_CACHE['delay_model'] = joblib.load(delay_path)
        _MODELS_CACHE['stage_model'] = joblib.load(stage_path)
        _MODELS_CACHE['feature_meta'] = joblib.load(meta_path)

    return _MODELS_CACHE

def assess_case_risk(case_data):
    """
    Main entry point for evaluating a land acquisition case.
    Args:
        case_data (dict): Dictionary with all required parameters.
    Returns:
        dict with delay_probability, risk_score, risk_level,
        predicted_delay_stage, top_risk_factors, recommendations, warning_severity.
    """
    artifacts = get_artifacts()
    delay_model = artifacts['delay_model']
    stage_model = artifacts['stage_model']
    meta = artifacts['feature_meta']

    # Ensure all required features exist with safe defaults
    feature_row = {
        'sector': case_data.get('sector', 'Highways'),
        'land_type': case_data.get('land_type', 'Agricultural'),
        'current_stage': case_data.get('current_stage', 'Survey & Demarcation'),
        'env_forest_clearance_status': case_data.get('env_forest_clearance_status', 'Approved'),
        'total_area_hectares': float(case_data.get('total_area_hectares', 25.0)),
        'affected_landowners_count': int(case_data.get('affected_landowners_count', 40)),
        'plots_count': int(case_data.get('plots_count', 50)),
        'days_in_current_stage': int(case_data.get('days_in_current_stage', 30)),
        'litigation_cases_count': int(case_data.get('litigation_cases_count', 0)),
        'public_objections_count': int(case_data.get('public_objections_count', 0)),
        'compensation_disparity_ratio': float(case_data.get('compensation_disparity_ratio', 1.0)),
        'sia_completed': 1 if case_data.get('sia_completed', True) else 0,
        'rr_plan_approved': 1 if case_data.get('rr_plan_approved', True) else 0,
    }

    df_sample = pd.DataFrame([feature_row])

    # 1. Delay Probability
    delay_prob = float(delay_model.predict_proba(df_sample)[0][1]) * 100.0
    delay_prob = round(min(99.0, max(1.0, delay_prob)), 1)

    # 2. Risk Score (0 - 100) & Classification (Low / Medium / High)
    risk_score = int(delay_prob)
    if risk_score >= 70:
        risk_level = 'High'
    elif risk_score >= 35:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'

    # 3. Delay Stage Bottleneck Prediction
    predicted_delay_stage = str(stage_model.predict(df_sample)[0])

    # 4. Explainable AI (XAI)
    top_factors = explain_prediction(feature_row, meta)

    # 5. Early Warning & Recommendations
    warning_severity, recommendations = generate_recommendations(feature_row, top_factors, risk_level)

    return {
        'delay_probability': delay_prob,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'predicted_delay_stage': predicted_delay_stage,
        'top_risk_factors': top_factors,
        'recommendations': recommendations,
        'warning_severity': warning_severity,
    }
