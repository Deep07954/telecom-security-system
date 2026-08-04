import time
import random
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

class ThreatDetectionEngine:
    def __init__(self):
        print("[*] Booting up AI Detection Engine...")
        try:
            # Load the pre-trained models and scaler from Phase 2 & 3
            self.scaler = joblib.load('models/scaler.pkl')
            self.rf_model = joblib.load('models/random_forest_engine.pkl')
            self.iso_model = joblib.load('models/isolation_forest_engine.pkl')
            print("[+] Models and Scaler loaded successfully.\n")
        except FileNotFoundError:
            print("[-] ERROR: Models not found. Did you run preprocessor.py and train_models.py?")
            exit()

        # The exact feature order used during training
        self.feature_names = [
            'session_duration', 'packet_rate', 'login_attempts', 
            'location_switch_freq', 'bandwidth_usage', 'call_failures'
        ]

    def process_event(self, event_data):
        """Processes a single real-time event through the dual-engine AI."""
        # Convert JSON/dict to DataFrame to keep feature names consistent for the scaler
        df_event = pd.DataFrame([event_data], columns=self.feature_names)
        
        # 1. Scale the incoming data
        scaled_features = self.scaler.transform(df_event)
        
        # 2. Run Inference
        rf_prediction = self.rf_model.predict(scaled_features)[0] # 1 is threat, 0 is normal
        
        iso_raw = self.iso_model.predict(scaled_features)[0]
        iso_prediction = 1 if iso_raw == -1 else 0 # Convert -1 to 1 (anomaly)
        
        # 3. Calculate Severity Score and Risk Level
        return self._evaluate_risk(rf_prediction, iso_prediction, event_data)

    def _evaluate_risk(self, rf_pred, iso_pred, event_data):
        """Matrix logic for assigning threat severity."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if rf_pred == 1 and iso_pred == 1:
            severity = random.randint(95, 100)
            status = "CRITICAL: Known Attack & Severe Anomaly"
            color = "\033[91m" # Red
        elif rf_pred == 1:
            severity = random.randint(80, 90)
            status = "HIGH: Signature-based Threat Detected"
            color = "\033[93m" # Yellow
        elif iso_pred == 1:
            severity = random.randint(60, 75)
            status = "MEDIUM: Unknown Network Anomaly"
            color = "\033[95m" # Purple
        else:
            severity = random.randint(1, 20)
            status = "CLEAN: Normal Traffic"
            color = "\033[92m" # Green
            
        reset_color = "\033[0m"
        
        # Create the alert payload
        alert = {
            "timestamp": timestamp,
            "severity_score": severity,
            "status": status,
            "rf_flag": int(rf_pred),
            "iso_flag": int(iso_pred),
            "raw_metrics": event_data
        }
        
        # Console output for hackathon wow-factor
        if severity > 50:
            print(f"{color}[!] ALERT [{timestamp}] | Severity: {severity}/100 | {status}{reset_color}")
            print(f"    -> Metrics triggered: Packets/s: {event_data['packet_rate']:.1f}, Loc Switches: {event_data['location_switch_freq']}")
        else:
            print(f"{color}[✓] LOG   [{timestamp}] | Severity: {severity}/100 | {status}{reset_color}")
            
        return alert

class TrafficSimulator:
    """Generates a live stream of simulated telecom events."""
    @staticmethod
    def generate_event(force_attack=False):
        # 90% normal traffic, 10% chance of a random attack (if not forced)
        is_attack = force_attack or random.random() < 0.10
        
        if not is_attack:
            # Baseline Normal Traffic
            return {
                'session_duration': random.uniform(10, 300),
                'packet_rate': random.uniform(20, 80),
                'login_attempts': random.randint(1, 2),
                'location_switch_freq': random.randint(0, 1),
                'bandwidth_usage': random.uniform(1.0, 10.0),
                'call_failures': random.randint(0, 1)
            }
        else:
            # Randomly select an attack vector to inject
            attack_type = random.choice(['ddos', 'sim_clone', 'brute_force'])
            
            if attack_type == 'ddos':
                return {
                    'session_duration': random.uniform(10, 300),
                    'packet_rate': random.uniform(400, 800), # Massive spike
                    'bandwidth_usage': random.uniform(80.0, 150.0),
                    'login_attempts': 1, 'location_switch_freq': 0, 'call_failures': 0
                }
            elif attack_type == 'sim_clone':
                return {
                    'session_duration': random.uniform(5, 50),
                    'location_switch_freq': random.randint(8, 20), # Impossible travel
                    'packet_rate': 40, 'login_attempts': 1, 'bandwidth_usage': 5.0, 'call_failures': 2
                }
            else: # brute_force
                return {
                    'session_duration': random.uniform(5, 30),
                    'login_attempts': random.randint(15, 50), # Spammed logins
                    'call_failures': random.randint(10, 30),
                    'packet_rate': 30, 'location_switch_freq': 0, 'bandwidth_usage': 2.0
                }

if __name__ == "__main__":
    # Initialize our system
    engine = ThreatDetectionEngine()
    
    print("===================================================")
    print(" LIVE TELECOM THREAT MONITORING STARTED")
    print("Press Ctrl+C to stop the stream.")
    print("===================================================\n")
    
    try:
        # Infinite loop to simulate real-time streaming
        while True:
            # Generate a live event
            live_event = TrafficSimulator.generate_event()
            
            # Process it through the AI
            engine.process_event(live_event)
            
            # Pause for 0.5 to 1.5 seconds to mimic real network flow latency
            time.sleep(random.uniform(0.5, 1.5))
            
    except KeyboardInterrupt:
        print("\n[*] Monitoring manually stopped. Shutting down engines.")