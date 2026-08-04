import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from preprocessor import DataPreprocessor

class ThreatDetectionTrainer:
    def __init__(self):
        # Initialize our models
        # Random Forest for signature-based fraud detection
        self.rf_model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=15, 
            random_state=42, 
            n_jobs=-1 # Use all CPU cores for faster training
        )
        
        # Isolation Forest for zero-day anomaly detection
        # contamination=0.08 matches the ~8% anomaly rate we generated
        self.iso_model = IsolationForest(
            n_estimators=100, 
            contamination=0.08, 
            random_state=42,
            n_jobs=-1
        )

    def train_and_evaluate(self):
        print("[*] Initializing Data Pipeline...")
        # 1. Fetch preprocessed, scaled, and SMOTE-balanced data
        processor = DataPreprocessor(data_path="telecom_security_data.csv")
        X_train, X_test, y_train, y_test = processor.load_and_preprocess()
        
        print("\n==============================================")
        print("[*] Training Engine 1: Random Forest (Supervised)")
        print("==============================================")
        self.rf_model.fit(X_train, y_train)
        rf_predictions = self.rf_model.predict(X_test)
        
        print("\n[+] Random Forest Evaluation Metrics:")
        print(classification_report(y_test, rf_predictions, target_names=['Normal', 'Threat']))
        print("Confusion Matrix:\n", confusion_matrix(y_test, rf_predictions))
        print(f"ROC-AUC Score: {roc_auc_score(y_test, rf_predictions):.4f}")

        print("\n==============================================")
        print("[*] Training Engine 2: Isolation Forest (Unsupervised)")
        print("==============================================")
        # Isolation forest doesn't use y_train (labels) for training, it only looks at features
        self.iso_model.fit(X_train)
        
        # Isolation Forest outputs 1 for normal, -1 for anomaly. 
        # We must map this to 0 for normal, 1 for anomaly to match our dataset labels.
        iso_raw_predictions = self.iso_model.predict(X_test)
        iso_predictions = np.array([1 if x == -1 else 0 for x in iso_raw_predictions])
        
        print("\n[+] Isolation Forest Evaluation Metrics:")
        print(classification_report(y_test, iso_predictions, target_names=['Normal', 'Threat']))
        print("Confusion Matrix:\n", confusion_matrix(y_test, iso_predictions))

        # 3. Save Models for Production
        self._save_models()

    def _save_models(self):
        """Saves the trained models to disk for the real-time API to use."""
        print("\n[*] Saving models to disk...")
        joblib.dump(self.rf_model, 'models/random_forest_engine.pkl')
        joblib.dump(self.iso_model, 'models/isolation_forest_engine.pkl')
        print("[+] Models successfully saved in the 'models/' directory.")

if __name__ == "__main__":
    trainer = ThreatDetectionTrainer()
    trainer.train_and_evaluate()