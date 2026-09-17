import streamlit as st
import openai
import pandas as pd
import urllib.parse  # Used to format text into a WhatsApp web link

# --- 1. DISPLAY LOGO ---
# Make sure your image file in GitHub is named "logo.png" (or update the filename below)
try:
    st.image("saina logo 2025.jpg", width=160)
except Exception:
    st.write("🌿 **Saina Essential**")  # Fallback text if logo.png is not found yet

# --- 2. APP HEADER ---
st.title("🌿Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# --- 3. LOAD INVENTORY ---
df = pd.read_csv("saina_products.csv")

# --- 4. USER INPUT & AI GENERATION ---
user_symptoms = st.text_input("How can we help you today?", placeholder="e.g., I have a headache and feel stressed")

if st.button("Generate My Routine"):
    if user_symptoms:
        # Load API key securely from Streamlit secrets
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Build prompt context
        context = f"Saina Inventory Products:\n{df.to_string()}\n\nUser Issue: {user_symptoms}"
        
        system_instructions = (
    "You are Saina's AI Herbalist. Recommend products strictly from the provided inventory. "
    "Format your output as a clear QUOTE with this exact layout:\n\n"
    "📋 RECOMMENDED ROUTINE:\n- [Item 1]: [Instructions] (P[Price])\n- [Item 2]: [Instructions] (P[Price])\n\n"
    "💰 ORDER QUOTE TOTAL: P[Sum]\n\n"
    "Click the button below to send this quote to WhatsApp and receive payment details."
)
        
        routine_text = response.choices[0].message.content
        
        st.success("Your Personalized Saina Routine:")
        st.write(routine_text)
        
        # --- 5. WHATSAPP ORDER BUTTON ---
        # Replace 26771234567 with your actual Botswana WhatsApp phone number
        phone_number = "26771334355"  
        
        message = f"Hello Saina Essential! I used your AI Coach. Here is my recommended routine:\n\n{routine_text}\n\nI would like to order these items!"
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
        
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold;">📲 Order This Routine via WhatsApp</button>'
            f'</a>', 
            unsafe_allow_html=True
        )
