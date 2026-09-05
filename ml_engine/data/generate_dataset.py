"""
Synthetic Dataset Generator for Land Acquisition Delay & Risk Prediction.
Generates realistic data based on RFCTLARR (Right to Fair Compensation and 
Transparency in Land Acquisition, Rehabilitation and Resettlement) indicators.
"""

import os
import random
import numpy as np
import pandas as pd

SECTORS = ['Highways', 'Railways', 'Urban Infrastructure', 'Irrigation', 'Energy', 'Industrial']
LAND_TYPES = ['Agricultural', 'Forest', 'Residential', 'Commercial', 'Government/Barren']
CURRENT_STAGES = [
    'Survey & Demarcation',
    'Preliminary Notification (Sec 11)',
    'Hearing of Objections (Sec 15)',
    'Declaration of Acquisition (Sec 19)',
    'Award & Compensation (Sec 23)',
    'R&R Implementation',
    'Physical Possession'
]
CLEARANCE_STATUSES = ['Approved', 'Pending', 'Rejected', 'Not Applicable']
DELAY_STAGES = [
    'Approval',
    'Compensation',
    'Legal',
    'Rehabilitation & Resettlement',
    'Possession',
    'Documentation/Survey'
]

def generate_synthetic_dataset(num_samples=1500, random_seed=42):
    random.seed(random_seed)
    np.random.seed(random_seed)

    records = []

    for i in range(num_samples):
        sector = random.choice(SECTORS)
        land_type = random.choices(LAND_TYPES, weights=[0.45, 0.15, 0.15, 0.10, 0.15])[0]
        current_stage = random.choice(CURRENT_STAGES)
        
        # Sector-specific or land-type realistic area
        if sector in ['Highways', 'Railways']:
            total_area_hectares = round(random.uniform(15.0, 250.0), 2)
        elif sector == 'Irrigation':
            total_area_hectares = round(random.uniform(50.0, 500.0), 2)
        else:
            total_area_hectares = round(random.uniform(5.0, 80.0), 2)

        # Scale landowners with area and land type
        density_multiplier = 4.5 if land_type in ['Residential', 'Commercial'] else (2.0 if land_type == 'Agricultural' else 0.4)
        affected_landowners = max(1, int(total_area_hectares * density_multiplier * random.uniform(0.6, 1.4)))
        plots_count = max(1, int(affected_landowners * random.uniform(1.1, 2.5)))

        days_in_current_stage = int(np.random.exponential(scale=90) + 15)
        
        # Clearance status
        if land_type == 'Forest':
            clearance_status = random.choices(['Pending', 'Approved', 'Rejected'], weights=[0.55, 0.35, 0.10])[0]
        else:
            clearance_status = random.choices(['Approved', 'Pending', 'Not Applicable'], weights=[0.60, 0.20, 0.20])[0]

        # Legal litigation cases (correlated with landowners & urban/residential)
        litigation_chance = 0.6 if land_type in ['Residential', 'Commercial'] or affected_landowners > 200 else 0.25
        litigation_count = int(np.random.poisson(lam=1.8)) if random.random() < litigation_chance else 0

        # Public objections count
        objections_chance = 0.7 if affected_landowners > 150 or land_type == 'Forest' else 0.3
        public_objections_count = int(np.random.poisson(lam=4.0)) if random.random() < objections_chance else random.randint(0, 2)

        # Compensation disparity ratio (Proposed Rate / Local Market Expectation)
        # 1.0 means matched market rate; < 0.8 means severe dissatisfaction
        compensation_disparity_ratio = round(random.betavariate(alpha=5, beta=3) * 0.7 + 0.4, 2)

        # Social Impact Assessment (SIA) & R&R status
        sia_completed = 1 if (random.random() > 0.25 or current_stage not in ['Survey & Demarcation', 'Preliminary Notification (Sec 11)']) else 0
        rr_plan_approved = 1 if (random.random() > 0.35 and affected_landowners > 50) else (1 if affected_landowners <= 50 else 0)

        # Calculate a realistic delay risk score (0 to 100)
        risk_score = 0.0
        
        # Risk factors weighting
        if litigation_count > 0:
            risk_score += min(35.0, litigation_count * 12.0)
        if clearance_status == 'Pending':
            risk_score += 24.0
        elif clearance_status == 'Rejected':
            risk_score += 40.0
        if compensation_disparity_ratio < 0.75:
            risk_score += 28.0
        elif compensation_disparity_ratio < 0.90:
            risk_score += 14.0
        if public_objections_count > 5:
            risk_score += min(20.0, public_objections_count * 2.5)
        if days_in_current_stage > 180:
            risk_score += 18.0
        elif days_in_current_stage > 90:
            risk_score += 9.0
        if land_type == 'Forest':
            risk_score += 12.0
        if sia_completed == 0 and current_stage not in ['Survey & Demarcation']:
            risk_score += 15.0
        if rr_plan_approved == 0 and affected_landowners > 100:
            risk_score += 18.0

        # Add slight realistic stochastic noise
        risk_score += random.gauss(0, 5)
        risk_score = max(5.0, min(98.0, risk_score))

        # Binary label for delay
        is_delayed = 1 if risk_score >= 50.0 else 0

        # Determine most likely delay stage bottleneck
        stage_scores = {
            'Legal': litigation_count * 18.0,
            'Compensation': (1.1 - min(1.1, compensation_disparity_ratio)) * 40.0 + (public_objections_count * 1.5),
            'Approval': (25.0 if clearance_status in ['Pending', 'Rejected'] else 0.0) + (15.0 if sia_completed == 0 else 0.0),
            'Rehabilitation & Resettlement': (25.0 if rr_plan_approved == 0 and affected_landowners > 80 else 5.0),
            'Documentation/Survey': (18.0 if current_stage == 'Survey & Demarcation' or plots_count > 300 else 4.0),
            'Possession': (20.0 if days_in_current_stage > 120 and public_objections_count > 3 else 6.0)
        }
        
        # Add random perturbation to stage scores
        for stg in stage_scores:
            stage_scores[stg] += random.uniform(0, 8)
            
        predicted_delay_stage = max(stage_scores, key=stage_scores.get)

        records.append({
            'sector': sector,
            'land_type': land_type,
            'total_area_hectares': total_area_hectares,
            'affected_landowners_count': affected_landowners,
            'plots_count': plots_count,
            'current_stage': current_stage,
            'days_in_current_stage': days_in_current_stage,
            'env_forest_clearance_status': clearance_status,
            'litigation_cases_count': litigation_count,
            'public_objections_count': public_objections_count,
            'compensation_disparity_ratio': compensation_disparity_ratio,
            'sia_completed': sia_completed,
            'rr_plan_approved': rr_plan_approved,
            'risk_score': round(risk_score, 1),
            'is_delayed': is_delayed,
            'delay_stage': predicted_delay_stage
        })

    df = pd.DataFrame(records)
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, 'land_acquisition_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully at {output_path} with {len(df)} records.")
    return output_path

if __name__ == '__main__':
    generate_synthetic_dataset()
