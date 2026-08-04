import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

class DataPreprocessor:
    def __init__(self, data_path="telecom_security_data.csv"):
        self.data_path = data_path
        # We save the scaler to use it later in Phase 4 (Real-time Engine)
        self.scaler = StandardScaler()
        
    def load_and_preprocess(self):
        print("[*] Loading dataset...")
        df = pd.read_csv(self.data_path)
        
        X = df.drop('label', axis=1)
        y = df['label']
        
        # 1. Train/Test Split (80/20)
        # Stratify ensures the 8% fraud ratio is maintained in both splits
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"[*] Original training shape: {X_train.shape}")
        
        # 2. Feature Scaling
        # We fit the scaler ONLY on training data to prevent data leakage
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Save the fitted scaler for production use
        joblib.dump(self.scaler, 'scaler.pkl')
        print("[+] Scaler saved to scaler.pkl")
        
        # 3. Handle Class Imbalance using SMOTE
        print("[*] Applying SMOTE to balance training classes...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
        
        print(f"[+] Balanced training shape: {X_train_balanced.shape}")
        print(f"[+] Fraud cases before SMOTE: {sum(y_train == 1)}, After: {sum(y_train_balanced == 1)}")
        
        return X_train_balanced, X_test_scaled, y_train_balanced, y_test

if __name__ == "__main__":
    processor = DataPreprocessor()
    X_train, X_test, y_train, y_test = processor.load_and_preprocess()
    print("[+] Preprocessing Pipeline Validated Successfully. Ready for modeling.")