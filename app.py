import streamlit as st
import openai
import pandas as pd
import streamlit as st

# Loads logo.png directly from your main repository folder
st.image("saina logo 2025.jpg", width=150)
# Load inventory
df = pd.read_csv("saina_products.csv")

st.title("🌿 Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# User Inputs
user_symptoms = st.text_input("How can we help you today?", placeholder="e.g., I have a headache and feel stressed")

if st.button("Generate My Routine"):
    if user_symptoms:
        # Load API key securely
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Build prompt context
        context = f"Saina Inventory Products:\n{df.to_string()}\n\nUser Issue: {user_symptoms}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Saina's AI Herbalist. Prescribe a custom routine using ONLY Saina inventory."},
                {"role": "user", "content": context}
            ]
        )
        
        # Output result
        st.success("Your Personalized Saina Routine:")
        st.write(response.choices[0].message.content)
