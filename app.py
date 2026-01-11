from flask import Flask, render_template, request
import numpy as np
import random
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# ==========================================
# 1. MACHINE LEARNING MODEL (Price Logic)
# ==========================================
def train_custom_model():
    """
    Trains the AI based on the user's specific rule:
    1 Cent = 15 Lakhs (includes furniture)
    2 Cents = 30 Lakhs
    ... and so on.
    """
    X_data = []
    y_data = []

    print(">> Training AI on Custom Price Logic (15L per Cent)...")

    # Generate data points following the 15L multiplier
    for i in range(1, 25): # Increased range for better scaling
        cents = float(i)
        
        # Base Price Rule: 15 Lakhs per Cent
        base_price = cents * 1500000
        
        # Add tiny random noise (+/- ₹5,000) to simulate ML variation
        noise = random.randint(-5000, 5000)
        final_price = base_price + noise
        
        X_data.append([cents])
        y_data.append(final_price)

    model = LinearRegression()
    model.fit(np.array(X_data), np.array(y_data))
    return model

# Initialize the AI Model once when app starts
model = train_custom_model()

# ==========================================
# 2. BLUEPRINT GENERATOR (Visual Diagrams)
# ==========================================
def get_custom_layout(cents):
    """Returns the ASCII blueprint based on plot size."""
    
    if cents < 1.8:
        # --- 1 CENT PLAN (1 BHK) ---
        return """
    +---------------------------+
    |          |                |
    |  KITCHEN |   BEDROOM      |
    |  (6'x7') |   (9'x10')     |
    |          |                |
    |----------+-------+--------|
    |          |       |  ATT.  |
    |   HALL   | GOD   |  BATH  |
    | (10'x10')| SHELF | (4'x6')|
    |          |       |        |
    +---------------------------+
    
    [ ESTIMATE: ~₹15 Lakhs ]
        """
    
    elif cents < 2.8:
        # --- 2 CENTS PLAN (2 BHK) ---
        return """
    +-----------------------+------------------+
    |           |           |                  |
    |  KITCHEN  | GUEST     |   MASTER BED     |
    |  (8'x10') | BATH      |   (11'x12')      |
    |           | (4'x6')   |                  |
    |-----------+-----------+--------+---------|
    |                       |        |         |
    |      LIVING HALL      |        |  ATT.   |
    |      (14'x 12')       |        |  BATH   |
    |                       |        | (4'x6') |
    |-----------+-----------|        |         |
    |           |           |        |         |
    |  GOD ROOM | SMALL BED |        |         |
    |  (4'x5')  | (9'x10')  |        |         |
    +-----------+-----------+--------+---------+
    
    [ ESTIMATE: ~₹30 Lakhs ]
        """

    elif cents < 3.8:
        # --- 3 CENTS PLAN (SQUARE LUXURY) ---
        return """
    +-----------------------------+-----------------------------+
    |              |              |                             |
    |  BEDROOM 2   |  ATT. BATH   |         KITCHEN             |
    |  (11'x11')   |   (5'x7')    |        (10'x10')            |
    |              |              |                             |
    |--------------+--------------+-------------+---------------|
    |                             |             |               |
    |        CENTRAL HALL         |             |   UTILITY     |
    |        (16' x 16')          |-------------+---------------|
    |                             |             |   GOD ROOM    |
    |                             |             |    (6'x6')    |
    |-----------------------------+-------------+---------------|
    |              |              |                             |
    |  MASTER BED  |  ATT. BATH   |        SIT-OUT /            |
    |  (12'x13')   |   (5'x7')    |        PARKING              |
    +--------------+--------------+-----------------------------+
    
    [ ESTIMATE: ~₹45 Lakhs ]
        """
    
    else:
        # --- N CENTS (SCALABLE) ---
        return f"""
    [ {cents} CENTS: LUXURY CUSTOM PLAN ]
    +-------------------------------------------------------+
    |                                                       |
    |    CUSTOM LUXURY VILLA LAYOUT ({int(cents)} BHK)      |
    |    (Consult Architect for detailed Drawing)           |
    |                                                       |
    |    - {int(cents)} Master Suites with Baths            |
    |    - Grand Hall + Family Lounge                       |
    |    - Large Kitchen + Utility                          |
    |    - Dedicated Pooja Room                             |
    |                                                       |
    +-------------------------------------------------------+
    
    [ ESTIMATE: ~₹{cents*15:,.0f} Lakhs ]
        """

# ==========================================
# 3. WEB ROUTES
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        cents = float(request.form['cents'])
        
        # 1. AI Predicts the TOTAL Inclusive Budget (e.g., 30 Lakhs for 2 cents)
        total_predicted_price = model.predict(np.array([[cents]]))[0]

        # 2. Reverse Calculate the Breakdown (For Display Only)
        # Typically: 75% goes to Structure, 25% goes to Interiors/Furniture
        structure_cost = total_predicted_price * 0.75
        furniture_cost = total_predicted_price * 0.25

        # 3. Get Blueprint
        blueprint_text = get_custom_layout(cents)
        
        # 4. Config String
        if cents < 1.8: config = "1 BHK Compact"
        elif cents < 2.8: config = "2 BHK Standard"
        else: config = f"{int(cents)} BHK Premium"

        return render_template('result.html', 
                               cents=cents,
                               config=config,
                               # Pass the split values to HTML
                               base_cost=f"{structure_cost:,.0f}",
                               furn_cost=f"{furniture_cost:,.0f}",
                               total=f"{total_predicted_price:,.0f}",
                               blueprint=blueprint_text)

    except ValueError:
        return "Invalid Input. Please go back and enter a number."

if __name__ == '__main__':
    app.run(debug=True)