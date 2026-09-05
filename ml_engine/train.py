"""
Model Training Pipeline for Land Acquisition Delay & Risk Prediction.
Trains:
  1. Delay Risk Pipeline (Binary Classifier -> Delay Probability & Risk Level)
  2. Bottleneck Stage Pipeline (Multi-class Classifier -> Likely delay stage)
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

CATEGORICAL_FEATURES = [
    'sector',
    'land_type',
    'current_stage',
    'env_forest_clearance_status'
]

NUMERICAL_FEATURES = [
    'total_area_hectares',
    'affected_landowners_count',
    'plots_count',
    'days_in_current_stage',
    'litigation_cases_count',
    'public_objections_count',
    'compensation_disparity_ratio',
    'sia_completed',
    'rr_plan_approved'
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

def train_models():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'land_acquisition_data.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}. Run generate_dataset.py first.")

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows from {data_path}")

    X = df[ALL_FEATURES]
    y_delay = df['is_delayed']
    y_stage = df['delay_stage']

    # Preprocessor definition
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES),
            ('num', StandardScaler(), NUMERICAL_FEATURES)
        ]
    )

    # 1. Train Delay Risk Pipeline
    print("\n--- Training Delay Risk Model ---")
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
        X, y_delay, test_size=0.2, random_state=42, stratify=y_delay
    )

    delay_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=120, max_depth=9, random_state=42, class_weight='balanced'))
    ])

    delay_pipeline.fit(X_train_d, y_train_d)
    y_pred_d = delay_pipeline.predict(X_test_d)
    y_prob_d = delay_pipeline.predict_proba(X_test_d)[:, 1]

    acc_d = accuracy_score(y_test_d, y_pred_d)
    roc_d = roc_auc_score(y_test_d, y_prob_d)
    print(f"Delay Model Accuracy: {acc_d * 100:.2f}% | ROC-AUC: {roc_d:.3f}")
    print(classification_report(y_test_d, y_pred_d))

    # 2. Train Bottleneck Stage Pipeline
    print("\n--- Training Bottleneck Stage Model ---")
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X, y_stage, test_size=0.2, random_state=42, stratify=y_stage
    )

    stage_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=120, max_depth=10, random_state=42))
    ])

    stage_pipeline.fit(X_train_s, y_train_s)
    y_pred_s = stage_pipeline.predict(X_test_s)

    acc_s = accuracy_score(y_test_s, y_pred_s)
    print(f"Bottleneck Stage Model Accuracy: {acc_s * 100:.2f}%")
    print(classification_report(y_test_s, y_pred_s))

    # Extract feature importance names
    encoder = delay_pipeline.named_steps['preprocessor'].named_transformers_['cat']
    cat_feature_names = list(encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    transformed_feature_names = cat_feature_names + NUMERICAL_FEATURES
    importances = delay_pipeline.named_steps['classifier'].feature_importances_

    feature_meta = {
        'all_features': ALL_FEATURES,
        'categorical_features': CATEGORICAL_FEATURES,
        'numerical_features': NUMERICAL_FEATURES,
        'transformed_feature_names': transformed_feature_names,
        'importances': dict(zip(transformed_feature_names, importances)),
        'delay_classes': list(delay_pipeline.classes_),
        'stage_classes': list(stage_pipeline.classes_)
    }

    # Save artifacts
    artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)

    delay_path = os.path.join(artifacts_dir, 'delay_model.joblib')
    stage_path = os.path.join(artifacts_dir, 'stage_model.joblib')
    meta_path = os.path.join(artifacts_dir, 'feature_meta.joblib')

    joblib.dump(delay_pipeline, delay_path)
    joblib.dump(stage_pipeline, stage_path)
    joblib.dump(feature_meta, meta_path)

    print(f"\nArtifacts successfully saved to {artifacts_dir}:")
    print(f" - {delay_path}")
    print(f" - {stage_path}")
    print(f" - {meta_path}")

if __name__ == '__main__':
    train_models()
