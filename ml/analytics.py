import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
import joblib
import warnings
import os
import random

# Silence warnings for a clean terminal
warnings.filterwarnings("ignore")


class EcoBrain:
    def __init__(self):
        # 1. SETUP PATHS (Robust Logic)
        # This ensures we always find the file, no matter where you run python from.
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.base_dir, "ecocore_research_data.csv")
        self.model_path = os.path.join(self.base_dir, "water_demand_model.pkl")

        self.model = None

        # 2. TRY TO LOAD. IF FAIL -> AUTO-TRAIN
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            print("Model file not found. Auto-training a new AI model now...")
            self.train_new_model()

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            print(f"EcoBrain loaded successfully from: {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Attempting to re-train...")
            self.train_new_model()

    def train_new_model(self):
        # 1. Check if Data Exists. If not, create it.
        if not os.path.exists(self.data_path):
            print("Data file missing. Generating synthetic data...")
            self.generate_data()

        # 2. Load Data
        df = pd.read_csv(self.data_path)
        X = df[['hour', 'occupancy', 'light_lux']]
        y = df['water_flow']

        # 3. Train Model
        print("Training Gradient Boosting Regressor...")
        model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)
        model.fit(X, y)

        # 4. Save Model
        joblib.dump(model, self.model_path)
        self.model = model
        print(f"New model saved to: {self.model_path}")

    def generate_data(self):
        # Internal generator in case data_generator.py wasn't run
        data = []
        for _ in range(1000):
            hour = random.randint(0, 23)
            occupancy = random.randint(0, 100) if 9 <= hour <= 18 else random.randint(0, 5)
            light_lux = (occupancy * 5) + random.randint(0, 50) if occupancy > 0 else 0
            water_flow = (occupancy * 0.2) + 2.0 + random.uniform(-0.5, 0.5)
            data.append([hour, occupancy, light_lux, round(water_flow, 2)])

        df = pd.DataFrame(data, columns=['hour', 'occupancy', 'light_lux', 'water_flow'])
        df.to_csv(self.data_path, index=False)
        print("✅ Synthetic data generated internally.")

    def predict_demand(self, hour, occupancy, light_lux):
        if not self.model:
            return (occupancy * 0.2) + 2.0  # Fallback

        try:
            input_data = pd.DataFrame([[hour, occupancy, light_lux]],
                                      columns=['hour', 'occupancy', 'light_lux'])
            prediction = self.model.predict(input_data)[0]
            return max(0.0, round(prediction, 2))
        except:
            return 0.0


if __name__ == "__main__":
    brain = EcoBrain()
    brain.train_new_model()