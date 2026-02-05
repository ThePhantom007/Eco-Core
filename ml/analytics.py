import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

class EcoBrain:
    def __init__(self):
        self.model = None
        self.best_model_name = "None"
        self.best_params = {}

    def train_model(self, csv_path = 'encore_research_data.csv'):
        data = pd.read_csv(csv_path)

        # Preparing the data
        X = data[['hour', 'occupancy', 'light lux']]
        y = data['water_flow']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Contending models
        models = {
            'Random Forest': (
                RandomForestRegressor(random_state=42, n_jobs=-1),
                {
                    'n_estimators': [50, 100, 200, 300],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_leaf': [1, 2, 4],
                    'min_samples_split': [2, 5, 10],
                    'bootstrap': [True, False]
                }
            ),
            'Gradient Boosting': (
                GradientBoostingRegressor(random_state=42),
                {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            )
        }

        best_rmse = np.inf
        best_model = None
        best_r2 = 0

        print(f"\n GRID SEARCH RESULTS (Sorted by Error):")
        print(f"{'MODEL':<20} | {'RMSE (L/min)':<15} | {'ACCURACY (R²)'}")
        print("-" * 65)

        for model_name, (model, param_grid) in models.items():
            grid_search = GridSearchCV(estimator=model, param_grid=param_grid,
                                       scoring='neg_mean_squared_error', cv=5, n_jobs=-1, verbose=3)
            grid_search.fit(X_train, y_train)
            best_estimator = grid_search.best_estimator_
            params = grid_search.best_params_

            y_pred = best_estimator.predict(X_test)

            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            print(f"{model_name:<20} | {rmse:<15.4f} | {r2:.4f}")

            # Checking for the best model
            if rmse < best_rmse:
                best_rmse = rmse
                best_r2 = r2
                best_model = best_estimator
                self.best_model_name = model_name
                self.best_params = params

        # Saving the best model
        self.model = best_model
        joblib.dump(self.model, 'water_demand_model.pkl')

        print("\n FINAL RESULTS:")
        print(f"WINNER: {self.best_model_name}")
        print(f"Best Params: {self.best_params}")
        print(f"Lowest Error (RMSE): {best_rmse:.4f} Liters/min")
        print(f"Percentage Accuracy (R²): {best_r2:.4f} ({(best_r2 * 100):.1f}%)")

        return {
            'model_name': self.best_model_name,
            'best_params': self.best_params,
            'rmse': best_rmse,
            'r2': best_r2
        }

    def predict_demand(self, hour, occupancy, light_lux):
        if self.model is None:
            self.model = joblib.load('water_demand_model.pkl')

        input_data = pd.DataFrame({
            'hour': [hour],
            'occupancy': [occupancy],
            'light lux': [light_lux]
        })

        prediction = self.model.predict(input_data)
        return max(0.0, round(prediction[0], 2))

if __name__ == "__main__":
    eco_brain = EcoBrain()
    eco_brain.train_model()