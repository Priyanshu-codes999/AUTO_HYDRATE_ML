import pickle
import pandas as pd

model = pickle.load(open("ml_model/model.pkl", "rb"))

def predict_water(data):
    df = pd.DataFrame([data])
    df = pd.get_dummies(df)
    required_cols = model.feature_names_in_
    for col in required_cols: 
        if col not in df.columns: 
            df[col] = 0 
    df = df[required_cols]
    return model.predict(df)[0]
