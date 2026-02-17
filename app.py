import streamlit as st
import joblib
import pandas as pd

# Load model
model = joblib.load("pilot_match_model.pkl")

st.title("🚁 Drone Operations AI Coordinator")

st.subheader("Pilot-Mission Suitability Prediction")

skill_match = st.number_input("Skill Match Score", min_value=0)
cert_match = st.selectbox("Certification Match", [0, 1])
location_match = st.selectbox("Location Match", [0, 1])
cost_fit = st.number_input("Budget Remaining After Cost")
experience = st.number_input("Experience (years)", min_value=0)

if st.button("Predict Suitability"):
    df = pd.DataFrame([[skill_match, cert_match, location_match, cost_fit, experience]],
                      columns=["skill_match", "cert_match", "location_match", "cost_fit", "experience"])

    prediction = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]

    st.success(f"Prediction: {prediction}")
    st.info(f"Confidence: {prob:.2f}")
