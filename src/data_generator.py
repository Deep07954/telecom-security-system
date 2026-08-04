import numpy as np
import pandas as pd
import random

class TelecomDataGenerator:
    def __init__(self, num_samples=10000, anomaly_rate=0.05):
        self.num_samples = num_samples
        self.anomaly_rate = anomaly_rate
        self.num_anomalies = int(num_samples * anomaly_rate)
        
    def generate_normal_traffic(self):
        """Generates baseline, healthy network traffic."""
        np.random.seed(42)
        
        data = {
            'session_duration': np.random.normal(loc=120, scale=30, size=self.num_samples), # seconds
            'packet_rate': np.random.normal(loc=50, scale=10, size=self.num_samples), # packets/sec
            'login_attempts': np.random.poisson(lam=1.2, size=self.num_samples), # mostly 1 or 2
            'location_switch_freq': np.random.poisson(lam=0.1, size=self.num_samples), # rarely switch cells quickly
            'bandwidth_usage': np.random.normal(loc=5.0, scale=1.5, size=self.num_samples), # MB
            'call_failures': np.random.poisson(lam=0.05, size=self.num_samples),
            'label': 0 # 0 = Normal
        }
        
        # Ensure no negative values where impossible
        data['session_duration'] = np.clip(data['session_duration'], 1, None)
        data['packet_rate'] = np.clip(data['packet_rate'], 1, None)
        data['bandwidth_usage'] = np.clip(data['bandwidth_usage'], 0.1, None)
        
        return pd.DataFrame(data)

    def inject_threats(self, df):
        """Injects specific cyber/telecom threats into the dataset."""
        indices = np.random.choice(df.index, self.num_anomalies, replace=False)
        
        # Split anomalies into different attack types
        ddos_idx = indices[:self.num_anomalies//3]
        sim_clone_idx = indices[self.num_anomalies//3: (2*self.num_anomalies)//3]
        brute_force_idx = indices[(2*self.num_anomalies)//3:]
        
        # Threat 1: DDoS / Network Intrusion (High packet rate, high bandwidth)
        df.loc[ddos_idx, 'packet_rate'] = np.random.normal(500, 100, len(ddos_idx))
        df.loc[ddos_idx, 'bandwidth_usage'] = np.random.normal(100, 20, len(ddos_idx))
        df.loc[ddos_idx, 'label'] = 1
        
        # Threat 2: SIM Cloning / Impossible Travel (High location switches)
        df.loc[sim_clone_idx, 'location_switch_freq'] = np.random.randint(5, 15, len(sim_clone_idx))
        df.loc[sim_clone_idx, 'session_duration'] = np.random.normal(30, 10, len(sim_clone_idx))
        df.loc[sim_clone_idx, 'label'] = 1
        
        # Threat 3: Account Takeover / Brute Force (High login attempts, high failures)
        df.loc[brute_force_idx, 'login_attempts'] = np.random.randint(10, 50, len(brute_force_idx))
        df.loc[brute_force_idx, 'call_failures'] = np.random.randint(5, 20, len(brute_force_idx))
        df.loc[brute_force_idx, 'label'] = 1
        
        return df

    def create_dataset(self, filename="telecom_security_data.csv"):
        print(f"[*] Generating {self.num_samples} records...")
        df = self.generate_normal_traffic()
        df = self.inject_threats(df)
        
        # Shuffle dataset
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv(filename, index=False)
        print(f"[+] Dataset saved to {filename}")
        print(df['label'].value_counts(normalize=True))
        return df

if __name__ == "__main__":
    generator = TelecomDataGenerator(num_samples=20000, anomaly_rate=0.08)
    df = generator.create_dataset()