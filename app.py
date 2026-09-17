import streamlit as st
import pandas as pd
import urllib.parse
from groq import Groq

# 1. DISPLAY LOGO
try:
    st.image("saina logo 2025.jpg", width=160)
except Exception:
    st.write("🌿 **Saina Essential**")

# 2. APP HEADER
st.title("🌿Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# 3. LOAD INVENTORY
df = pd.read_csv("saina_products.csv")

# 4. USER INPUT & AI GENERATION
user_symptoms = st.text_input("How can we help you today?", placeholder="e.g., I have a headache and feel stressed")

if st.button("Generate My Routine"):
    if user_symptoms:
        # Initialize Groq Client using your secret key
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        context = f"Saina Inventory Products and Prices:\n{df.to_string()}\n\nUser Issue: {user_symptoms}"
        
        system_instructions = (
            "You are Saina's AI Herbalist. Recommend products strictly from the provided inventory. "
            "Format your output as a clear QUOTE with this exact layout:\n\n"
            "📋 RECOMMENDED ROUTINE:\n- [Item 1]: [Instructions] (P[Price])\n- [Item 2]: [Instructions] (P[Price])\n\n"
            "💰 ORDER QUOTE TOTAL: P[Sum]\n\n"
            "Click the button below to send this quote to WhatsApp and receive payment details."
        )
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": context}
                ]
            )
            
            routine_text = completion.choices[0].message.content
            
            st.success("Your Personalized Saina Routine & Quote:")
            st.write(routine_text)
            
            # 5. WHATSAPP CHECKOUT BUTTON
            phone_number = "26774501880"
            
            message = f"Hello Saina Essential! I used your AI Coach and would like to place an order:\n\n{routine_text}"
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
            
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold;">📲 Send Order & Total to WhatsApp</button>'
                f'</a>', 
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error connecting to AI service: {e}")
