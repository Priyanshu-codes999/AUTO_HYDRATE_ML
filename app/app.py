import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime
import smtplib
from email.mime.text import MIMEText

from ml_model.predict import predict_water
from database.db_connection import connect_db

st.set_page_config(page_title="Auto Hydrate ML", layout="wide")

# ================= AUTH SYSTEM =================
def auth_system():
    st.sidebar.title("User Panel")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Reset Password"])

    if menu == "Signup":
        st.sidebar.subheader("Create Account")
        user = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email")
        pwd = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Signup"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
                (user, email, pwd),
            )
            conn.commit()
            conn.close()
            st.sidebar.success("Account created")

    elif menu == "Login":
        user = st.sidebar.text_input("Username")
        pwd = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            conn = connect_db()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (user, pwd),
            )
            res = cur.fetchone()
            conn.close()

            if res:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.sidebar.success("Login successful")
            else:
                st.sidebar.error("Invalid credentials")

    elif menu == "Reset Password":
        st.sidebar.subheader("Reset Password")
        user = st.sidebar.text_input("Username")
        new_pwd = st.sidebar.text_input("New Password", type="password")

        if st.sidebar.button("Update Password"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET password=%s WHERE username=%s",
                (new_pwd, user),
            )
            conn.commit()
            conn.close()
            st.sidebar.success("Password updated")

    if st.session_state.logged_in:
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()


auth_system()

if not st.session_state.logged_in:
    st.stop()


# ================= WEATHER =================
def get_temperature(city="Delhi"):
    try:
        api_key = "0aaa2817435416741f9d17bb49db6c2d"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        return requests.get(url).json()["main"]["temp"]
    except:
        return None


# ================= EMAIL =================
def send_email(email, msg_text):
    sender = "priyanshu9999agrawal@gmail.com"
    password = "iejw ptyx iffc dprr"

    msg = MIMEText(msg_text)
    msg["Subject"] = "Hydration Reminder"
    msg["From"] = sender
    msg["To"] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        st.success("Reminder email sent")
    except Exception as e:
        st.warning(e)


st.title("Auto Hydrate ML Healthcare App")


# ================= PROFILE PAGE =================
if st.sidebar.checkbox("Profile Page"):
    st.header("User Profile")
    st.write("Logged in as:", st.session_state.user)
    st.stop()


# ================= PATIENT RECOGNITION =================
patient_id = st.text_input("Patient ID")
existing = None

if patient_id:
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM patient_data WHERE patient_id=%s ORDER BY record_time DESC LIMIT 1",
        (patient_id,),
    )
    existing = cur.fetchone()
    conn.close()

if existing:
    st.success("Returning patient detected")
else:
    st.info("New patient")


col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Patient Name", value=existing["patient_name"] if existing else "")
    email = st.text_input("Email", value=existing.get("email", "") if existing else "")
    age = st.number_input("Age", value=int(existing["age"]) if existing else 0)
    weight = st.number_input("Weight", value=float(existing["weight"]) if existing else 0.0)

with col2:
    temp = get_temperature() or st.number_input("Temperature")
    hr = st.number_input("Heart Rate")
    humidity = st.number_input("Humidity")

activity = st.selectbox("Activity", ["low", "medium", "high"])
sleep = st.number_input("Sleep Hours")
medical = st.selectbox("Medical", ["normal", "diabetic", "kidney", "athlete"])
drink = st.selectbox("Drink", ["Water", "Coconut", "Juice", "Chaach", "Electrolyte"])


# ================= PREDICTION =================
if st.button("Predict Hydration"):
    data = {
        "temperature": temp,
        "humidity": humidity,
        "activity_level": activity,
        "age": age,
        "weight": weight,
        "heart_rate": hr,
        "sleep_hours": sleep,
        "medical_condition": medical,
    }

    prediction = predict_water(data)
    st.success(f"Recommended water: {prediction:.2f} L")

    send_email(email, f"Drink approx {prediction:.2f}L today")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patient_data(patient_id,patient_name,email,age,weight,temperature,heart_rate,humidity,activity_level,predicted_water,drink_type,record_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            patient_id,
            name,
            email,
            age,
            weight,
            temp,
            hr,
            humidity,
            activity,
            prediction,
            drink,
            datetime.datetime.now(),
        ),
    )
    conn.commit()
    conn.close()


# ================= USER-SPECIFIC DASHBOARD =================
st.header("Personal Dashboard")

if st.button("Show My Data") and patient_id:
    conn = connect_db()
    df = pd.read_sql(
        "SELECT * FROM patient_data WHERE patient_id=%s",
        conn,
        params=(patient_id,),
    )
    conn.close()

    if not df.empty:
        st.dataframe(df)

        fig1, ax1 = plt.subplots()
        ax1.plot(df["predicted_water"])
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        df["drink_type"].value_counts().plot(kind="bar", ax=ax2)
        st.pyplot(fig2)

        st.metric("Average", f"{df['predicted_water'].mean():.2f} L")
    else:
        st.warning("No data for this patient")
        