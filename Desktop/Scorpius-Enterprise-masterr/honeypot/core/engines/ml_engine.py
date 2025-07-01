import asyncio
import os
import pickle
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class MLEngine:
    def __init__(self):
        self.classifier = None
        self.scaler = None
        self.feature_names = [
            "bytecode_length",
            "control_flow_complexity",
            "storage_op_ratio",
            "external_call_ratio",
            "selfdestruct_present",
            "delegatecall_present",
            "balance_check_present",
            "suspicious_function_count",
            "tx_volume_ratio",
            "unique_senders",
            "unique_receivers",
        ]
        self.model_path = "models/ml_models/trained_models/honeypot_classifier.pkl"
        self.scaler_path = "models/ml_models/trained_models/feature_scaler.pkl"

    async def load_models(self):
        """Load pre-trained ML models"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                print("Loading existing ML models...")
                self.classifier = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                print("ML models not found. Training initial models...")
                await self._train_initial_models()
        except Exception as e:
            print(f"Error loading ML models: {e}")
            await self._train_initial_models()

    async def predict(self, contract_data: dict) -> Dict[str, Any]:
        """Predict honeypot probability using ML"""
        try:
            if self.classifier is None or self.scaler is None:
                await self.load_models()

            # Extract features
            features = await self._extract_features(contract_data)
            features_array = np.array([features])

            # Scale features
            if self.scaler:
                scaled_features = self.scaler.transform(features_array)
            else:
                scaled_features = features_array

            # Make prediction
            probability = self.classifier.predict_proba(scaled_features)[0][1]
            prediction = self.classifier.predict(scaled_features)[0]

            # Extract feature importance
            feature_importance = {}
            if hasattr(self.classifier, "feature_importances_"):
                for i, importance in enumerate(self.classifier.feature_importances_):
                    if i < len(self.feature_names):
                        feature_importance[self.feature_names[i]] = float(importance)

            return {
                "confidence": float(probability),
                "prediction": bool(prediction),
                "features_used": len(features),
                "feature_importance": feature_importance,
            }

        except Exception as e:
            return {
                "confidence": 0.5,  # Default to uncertain
                "prediction": False,
                "error": str(e),
            }

    async def _extract_features(self, contract_data: dict) -> List[float]:
        """Extract ML features from contract data"""
        features = []

        # Bytecode features
        bytecode = contract_data.get("bytecode", "")
        bytecode_length = len(bytecode)
        features.append(bytecode_length)

        # Use bytecode metrics if available
        bytecode_metrics = contract_data.get("bytecode_metrics", {})

        # Control flow complexity
        control_flow = bytecode_metrics.get("control_flow_complexity", 0)
        features.append(control_flow)

        # Storage operation ratio
        storage_ratio = bytecode_metrics.get("storage_op_ratio", 0)
        features.append(storage_ratio)

        # External call ratio
        external_call_ratio = bytecode_metrics.get("external_call_ratio", 0)
        features.append(external_call_ratio)

        # Presence of dangerous opcodes
        selfdestruct_present = 1 if "SELFDESTRUCT" in bytecode.upper() else 0
        features.append(selfdestruct_present)

        delegatecall_present = 1 if "DELEGATECALL" in bytecode.upper() else 0
        features.append(delegatecall_present)

        balance_check_present = 1 if "BALANCE" in bytecode.upper() else 0
        features.append(balance_check_present)

        # ABI features
        abi = contract_data.get("abi", [])
        suspicious_functions = ["withdraw", "claim", "getReward", "collect"]
        suspicious_count = sum(
            1 for func in abi if func.get("name", "").lower() in suspicious_functions
        )
        features.append(suspicious_count)

        # Transaction features
        transactions = contract_data.get("transactions", [])
        tx_count = len(transactions)

        # Calculate transaction volume ratio (outgoing/incoming)
        incoming_value = sum(
            tx.get("value", 0)
            for tx in transactions
            if tx.get("to") == contract_data.get("address")
        )
        outgoing_value = sum(
            tx.get("value", 0)
            for tx in transactions
            if tx.get("from") == contract_data.get("address")
        )

        tx_volume_ratio = outgoing_value / incoming_value if incoming_value > 0 else 0
        features.append(tx_volume_ratio)

        # Count unique transaction senders/receivers
        unique_senders = len(set(tx.get("from") for tx in transactions))
        unique_receivers = len(set(tx.get("to") for tx in transactions))

        features.append(unique_senders)
        features.append(unique_receivers)

        # Fill any missing features with zeros
        while len(features) < len(self.feature_names):
            features.append(0.0)

        return features[: len(self.feature_names)]  # Ensure correct length

    async def _train_initial_models(self):
        """Train initial ML models with synthetic data"""
        print("Training initial ML models with synthetic data...")

        # Generate synthetic training data
        X_train, y_train = self._generate_synthetic_data(n_samples=1000)

        # Create and fit scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_train)

        # Train classifier
        self.classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.classifier.fit(X_scaled, y_train)

        # Save models
        joblib.dump(self.classifier, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        print(f"Initial models trained and saved to {self.model_path}")

    def _generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic data for initial model training"""
        np.random.seed(42)

        # Create synthetic features
        X = np.random.rand(n_samples, len(self.feature_names))

        # Honeypot signatures (simplified)
        # High bytecode length + high control flow complexity + high selfdestruct presence
        honeypot_idx = np.where(
            (X[:, 0] > 0.7)
            & (X[:, 1] > 0.7)  # High bytecode length
            & (X[:, 4] > 0.5)  # High control flow complexity  # Selfdestruct present
        )[0]

        # Another honeypot pattern: suspicious functions + imbalanced tx ratio
        honeypot_idx2 = np.where(
            (X[:, 7] > 0.7)
            & (  # High suspicious function count
                X[:, 8] < 0.3
            )  # Low tx volume ratio (funds coming in but not out)
        )[0]

        # Combine honeypot patterns
        all_honeypot_idx = np.unique(np.concatenate([honeypot_idx, honeypot_idx2]))

        # Create labels
        y = np.zeros(n_samples)
        y[all_honeypot_idx] = 1

        return X, y

    async def update_model(self, new_contracts_data, new_labels):
        """Update model with new labeled data"""
        if self.classifier is None or self.scaler is None:
            await self.load_models()

        # Extract features from new data
        new_features = []
        for contract_data in new_contracts_data:
            features = await self._extract_features(contract_data)
            new_features.append(features)

        X_new = np.array(new_features)
        y_new = np.array(new_labels)

        # Get existing training data (simplified, in production use a database)
        X_existing, y_existing = self._generate_synthetic_data(n_samples=1000)

        # Combine with existing data
        X_combined = np.vstack([X_existing, X_new])
        y_combined = np.concatenate([y_existing, y_new])

        # Update scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_combined)

        # Retrain model
        self.classifier = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.classifier.fit(X_scaled, y_combined)

        # Save updated models
        joblib.dump(self.classifier, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        # Calculate metrics
        y_pred = self.classifier.predict(X_scaled)
        metrics = {
            "accuracy": accuracy_score(y_combined, y_pred),
            "precision": precision_score(y_combined, y_pred),
            "recall": recall_score(y_combined, y_pred),
            "f1": f1_score(y_combined, y_pred),
        }

        return metrics
