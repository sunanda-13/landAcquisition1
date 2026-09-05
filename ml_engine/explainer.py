"""
Explainable AI (XAI) Engine for Land Acquisition Risk Intelligence.
Explains why a case received its risk score and extracts top contributing risk factors.
"""

def explain_prediction(case_dict, feature_meta=None):
    """
    Analyzes case parameters against baseline operational risk thresholds
    and returns a ranked list of major positive and negative contributing factors.
    """
    contributions = []

    litigation_count = case_dict.get('litigation_cases_count', 0)
    clearance_status = case_dict.get('env_forest_clearance_status', 'Not Applicable')
    disp_ratio = float(case_dict.get('compensation_disparity_ratio', 1.0))
    objections_count = case_dict.get('public_objections_count', 0)
    days_in_stage = case_dict.get('days_in_current_stage', 0)
    land_type = case_dict.get('land_type', 'Agricultural')
    landowners = case_dict.get('affected_landowners_count', 0)
    sia_completed = case_dict.get('sia_completed', 1)
    rr_plan_approved = case_dict.get('rr_plan_approved', 1)
    current_stage = case_dict.get('current_stage', '')

    # 1. Legal Litigations
    if litigation_count > 0:
        impact = min(35, litigation_count * 12)
        contributions.append({
            'factor': 'Active Legal Litigations',
            'impact_type': 'High Risk (+)',
            'impact_score': impact,
            'description': f"{litigation_count} active court cases/petitions pending in judicial forums, risking injunctions."
        })

    # 2. Environmental & Forest Clearance
    if clearance_status == 'Pending':
        contributions.append({
            'factor': 'Pending Environmental/Forest Clearance',
            'impact_type': 'High Risk (+)',
            'impact_score': 25,
            'description': "Statutory Stage-I/II environmental or forest clearance is currently pending approval."
        })
    elif clearance_status == 'Rejected':
        contributions.append({
            'factor': 'Clearance Rejection / Compliance Notice',
            'impact_type': 'Critical Risk (+)',
            'impact_score': 40,
            'description': "Environmental/Forest clearance application faced objections or rejection."
        })

    # 3. Compensation Disparity Ratio
    if disp_ratio < 0.75:
        contributions.append({
            'factor': 'Severe Compensation Disparity',
            'impact_type': 'High Risk (+)',
            'impact_score': 28,
            'description': f"Proposed rate is only {int(disp_ratio*100)}% of prevailing market rate, inducing severe resistance."
        })
    elif disp_ratio < 0.90:
        contributions.append({
            'factor': 'Below-Market Compensation Rate',
            'impact_type': 'Moderate Risk (+)',
            'impact_score': 14,
            'description': f"Compensation rate is at {int(disp_ratio*100)}% of market expectation; potential award disputes."
        })

    # 4. Public & Gram Sabha Objections
    if objections_count >= 5:
        contributions.append({
            'factor': 'Widespread Public Objections',
            'impact_type': 'High Risk (+)',
            'impact_score': min(25, objections_count * 3),
            'description': f"{objections_count} formal objections lodged under Section 15 hearings."
        })
    elif objections_count >= 2:
        contributions.append({
            'factor': 'Unresolved Stakeholder Objections',
            'impact_type': 'Moderate Risk (+)',
            'impact_score': 10,
            'description': f"{objections_count} unresolved stakeholder grievances."
        })

    # 5. Bottleneck Duration (Days in current stage)
    if days_in_stage > 180:
        contributions.append({
            'factor': 'Prolonged Stage Stagnation',
            'impact_type': 'High Risk (+)',
            'impact_score': 20,
            'description': f"Case has remained stuck in '{current_stage}' for {days_in_stage} days (> 6 months)."
        })
    elif days_in_stage > 90:
        contributions.append({
            'factor': 'Stage Timeline Overrun',
            'impact_type': 'Moderate Risk (+)',
            'impact_score': 10,
            'description': f"Current stage '{current_stage}' has taken {days_in_stage} days (> 3 months standard target)."
        })

    # 6. Social Impact Assessment (SIA)
    if not sia_completed and current_stage != 'Survey & Demarcation':
        contributions.append({
            'factor': 'Incomplete Social Impact Assessment',
            'impact_type': 'Moderate Risk (+)',
            'impact_score': 15,
            'description': "Section 4 mandatory Social Impact Assessment study has not been formally concluded."
        })

    # 7. R&R Plan Status with high displaced population
    if not rr_plan_approved and landowners > 75:
        contributions.append({
            'factor': 'Unapproved R&R Scheme for Large Population',
            'impact_type': 'High Risk (+)',
            'impact_score': 20,
            'description': f"Rehabilitation & Resettlement scheme unapproved despite {landowners} affected titleholders."
        })

    # 8. Forest Land Involvement
    if land_type == 'Forest':
        contributions.append({
            'factor': 'Forest Land Diversion Complexity',
            'impact_type': 'Moderate Risk (+)',
            'impact_score': 12,
            'description': "Involves forest parcel requiring compensatory afforestation and MoEF&CC approval."
        })

    # Mitigating / Favorable Factors
    if disp_ratio >= 1.05 and litigation_count == 0:
        contributions.append({
            'factor': 'Competitive Compensation Package',
            'impact_type': 'Low Risk (-)',
            'impact_score': -15,
            'description': "Compensation rate matches or exceeds prevailing circle and market rates."
        })
    if clearance_status == 'Approved':
        contributions.append({
            'factor': 'Clearance Fully Secured',
            'impact_type': 'Low Risk (-)',
            'impact_score': -12,
            'description': "All necessary statutory environmental & forest clearances are in place."
        })

    # Sort positive risk factors descending by impact score
    contributions.sort(key=lambda x: x['impact_score'], reverse=True)
    return contributions
