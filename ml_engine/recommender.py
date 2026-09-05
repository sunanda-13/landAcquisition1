"""
Early Warning & Decision-Support Recommendation Engine.
Generates tailored, actionable administrative mitigations based on detected risk factors.
"""

def generate_recommendations(case_dict, top_factors, risk_level):
    """
    Generates structured early warning alerts and actionable recommendations.
    Returns:
        warning_severity: 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'
        recommendations: list of dicts with {category, action, authority, urgency}
    """
    recommendations = []

    # Map risk level to default warning severity
    if risk_level == 'High':
        warning_severity = 'CRITICAL' if case_dict.get('litigation_cases_count', 0) >= 3 else 'HIGH'
    elif risk_level == 'Medium':
        warning_severity = 'MODERATE'
    else:
        warning_severity = 'LOW'

    factor_names = [f['factor'] for f in top_factors if f.get('impact_score', 0) > 0]

    # Rule 1: Legal Litigations
    if any('Legal' in f or 'Litigation' in f for f in factor_names):
        recommendations.append({
            'category': 'Legal & Dispute Resolution',
            'action': 'Convene Lok Adalat bench or Special Fast-Track Land Acquisition Tribunal for out-of-court consent settlements.',
            'authority': 'District Collector / SLAO (Special Land Acquisition Officer)',
            'urgency': 'Immediate'
        })
        recommendations.append({
            'category': 'Judicial Compliance',
            'action': 'Appoint Standing State Counsel to submit urgent counter-affidavits opposing interim stay orders.',
            'authority': 'Project Legal Cell',
            'urgency': 'Within 7 Days'
        })

    # Rule 2: Compensation Disparity
    if any('Compensation' in f for f in factor_names):
        disp_ratio = case_dict.get('compensation_disparity_ratio', 1.0)
        recommendations.append({
            'category': 'Financial & Valuation',
            'action': f"Review District Level Land Purchase Committee (DLLPC) rates; verify 100% solatium and multiplying factor under Schedule 1 (Current ratio: {disp_ratio:.2f}).",
            'authority': 'Revenue Valuation Officer / DLLPC',
            'urgency': 'High Priority'
        })

    # Rule 3: Environmental / Forest Clearance
    if any('Clearance' in f for f in factor_names):
        recommendations.append({
            'category': 'Statutory Clearances',
            'action': 'Deploy dedicated Nodal Liaison Officer to Parivesh Portal coordination with State Forest Advisory Committee (FAC).',
            'authority': 'State Forest Department Liaison Officer',
            'urgency': 'Immediate'
        })

    # Rule 4: Public & Community Objections
    if any('Objection' in f for f in factor_names):
        recommendations.append({
            'category': 'Stakeholder Engagement',
            'action': 'Organize open Gram Sabha / Ward consultation meetings under Section 15 to address specific rehabilitation demands.',
            'authority': 'Sub-Divisional Magistrate (SDM) / Local Tehsildar',
            'urgency': 'High Priority'
        })

    # Rule 5: Stage Stagnation
    if any('Stagnation' in f or 'Timeline' in f for f in factor_names):
        current_stage = case_dict.get('current_stage', 'Current Stage')
        days = case_dict.get('days_in_current_stage', 0)
        recommendations.append({
            'category': 'Project Governance',
            'action': f"Trigger administrative escalation for '{current_stage}' (Pending {days} days); set 15-day strict milestone with concerned field team.",
            'authority': 'Project Director / Chief Engineer',
            'urgency': 'Immediate'
        })

    # Rule 6: R&R Plan Missing
    if any('R&R' in f for f in factor_names):
        recommendations.append({
            'category': 'Rehabilitation & Resettlement',
            'action': 'Formulate and notify draft R&R scheme under Section 16; conduct public hearing with displaced families.',
            'authority': 'Administrator (R&R)',
            'urgency': 'Within 14 Days'
        })

    # Default fallback if low risk or factors addressed
    if not recommendations:
        recommendations.append({
            'category': 'Standard Monitoring',
            'action': 'Maintain bi-weekly progress tracker and ensure timely fund disbursement to avoid future escalation.',
            'authority': 'Case Officer / Executive Engineer',
            'urgency': 'Routine'
        })

    return warning_severity, recommendations
