import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import job_lib
import os

def check_model_drift(reference_path, current_data_df):
    # 1. ట్రైనింగ్ అప్పుడు వాడిన డేటాను లోడ్ చెయ్ (Reference)
    reference_df = pd.read_csv(reference_path)
    
    # 2. Evidently Report సెటప్
    drift_report = Report(metrics=[DataDriftPreset()])
    
    # 3. రెండింటినీ కంపేర్ చెయ్
    # గమనిక: రెండు డేటాసెట్లలో కాలమ్ పేర్లు ఒకేలా ఉండాలి
    drift_report.run(reference_data=reference_df, current_data=current_data_df)
    
    report_dict = drift_report.as_dict()
    
    # 4. Drift జరిగిందో లేదో పట్టుకో
    # ఉదాహరణకు: 50% కంటే ఎక్కువ ఫీచర్స్ మారితే Drift ఉన్నట్టు లెక్క
    drift_detected = report_dict['metrics'][0]['result']['dataset_drift']
    
    return drift_detected, report_dict