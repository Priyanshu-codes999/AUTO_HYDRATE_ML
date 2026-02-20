import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

data = pd.read_csv("data/hydration_data.csv")

X = data.drop("water_intake", axis=1)
X = pd.get_dummies(X)   # activity_level convert

y = data["water_intake"]

model = LinearRegression()
model.fit(X, y)

pickle.dump(model, open("ml_model/model.pkl", "wb"))

print("Model trained successfully")
