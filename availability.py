import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class FacultyAvailabilityModel:
    def __init__(self, schedule_file='schedule.csv'):
        self.schedule_file = schedule_file
        self.model_path = 'faculty_availability_models.pkl'
        self.models = {}

    def train_model(self):
        if not os.path.exists(self.schedule_file):
            print("⚠️ Schedule file not found. Run generate_schedule.py first.")
            return

        data = pd.read_csv(self.schedule_file)
        # Logic: If faculty_id > 0, they are BUSY (1). If 0 (Library), they are FREE (0).
        # Note: We only care about assigning 'is_busy' to actual faculty, not the placeholder ID 0.
        
        # Get list of all real faculty IDs
        all_faculty = data[data['faculty_id'] != 0]['faculty_id'].unique()
        
        for f_id in all_faculty:
            # Get all entries for this faculty
            df_f = data[data['faculty_id'] == f_id].copy()
            
            # We need negative samples (times they are NOT teaching).
            # The schedule only lists times they ARE teaching (mostly).
            # A robust way: Create a full grid of Day/Hour and mark 1 if present in schedule, 0 if not.
            
            full_grid = []
            for d in range(1, 7): # Days 1-6
                for h in range(1, 9): # Hours 1-8
                    # Check if assigned in real schedule
                    is_assigned = not df_f[(df_f['day'] == d) & (df_f['hour'] == h)].empty
                    full_grid.append({'day': d, 'hour': h, 'is_busy': 1 if is_assigned else 0})
            
            grid_df = pd.DataFrame(full_grid)
            
            # Train
            X = grid_df[['day', 'hour']]
            y = grid_df['is_busy']
            
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X, y)
            self.models[f_id] = model

        joblib.dump(self.models, self.model_path)
        print("✅ ML Models trained and saved.")

    def get_free_predictions(self, day, hour):
        """Returns a set of faculty_ids predicted to be FREE (0) at this time."""
        if not self.models:
            if os.path.exists(self.model_path):
                self.models = joblib.load(self.model_path)
            else:
                return set()
        
        free_ids = set()
        for f_id, model in self.models.items():
            # Predict: 0=Free, 1=Busy
            prediction = model.predict([[day, hour]])[0]
            if prediction == 0:
                free_ids.add(f_id)
        return free_ids
