import pandas as pd
import random

rows = 500   # jitni rows chahiye change kar sakte ho

data = []

for _ in range(rows):
    temperature = random.randint(20, 42)
    humidity = random.randint(30, 80)
    activity_level = random.choice(["low", "medium", "high"])
    age = random.randint(18, 70)
    weight = random.randint(50, 95)
    heart_rate = random.randint(60, 110)
    sleep_hours = random.randint(4, 9)
    medical_condition = random.choice(
        ["normal", "diabetic", "kidney", "athlete"]
    )

    # Simple hydration logic (realistic approx)
    water_intake = round(
        (weight * 0.033)
        + (temperature - 25) * 0.05
        + (0.5 if activity_level == "high" else 0)
        + random.uniform(-0.3, 0.3),
        2
    )

    data.append([
        temperature, humidity, activity_level, age,
        weight, heart_rate, sleep_hours,
        medical_condition, water_intake
    ])

columns = [
    "temperature", "humidity", "activity_level",
    "age", "weight", "heart_rate",
    "sleep_hours", "medical_condition",
    "water_intake"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("data/hydration_data.csv", index=False)

print("Dataset generated successfully!")
