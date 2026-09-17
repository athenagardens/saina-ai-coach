import streamlit as st
import pandas as pd
import urllib.parse
from groq import Groq

# 1. DISPLAY LOGO
try:
    st.image("logo.png", width=160)
except Exception:
    st.write("🌿 **Saina Essential**")

# 2. APP HEADER
st.title("Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# 3. LOAD INVENTORY & OPTIMIZE CATALOG
df = pd.read_csv("saina_products.csv")

catalog_summary = ""
for _, row in df.iterrows():
    catalog_summary += f"- {row['Product Name']} ({row['Category']}): P{row['Price (BWP)']}. Uses: {row['Primary Uses']}\n"

# 4. USER INPUT & AI GENERATION
user_symptoms = st.text_input("How can we help you today?", placeholder="e.g., I have a headache and feel stressed")

if st.button("Generate My Routine"):
    if user_symptoms:
        # Initialize Groq Client
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        system_instructions = (
            "You are Saina's AI Herbalist. Recommend products strictly from the provided inventory list. "
            "Keep recommendations concise. Always prefix the header with '🌿 SAINA ESSENTIAL 🌿'. "
            "Format your output strictly as a clear itemized list with numbers so customers can select what they want:\n\n"
            "🌿 SAINA ESSENTIAL — RECOMMENDED ROUTINE:\n"
            "1️⃣ [Item Name] — (P[Price]) — [Brief usage]\n"
            "2️⃣ [Item Name] — (P[Price]) — [Brief usage]\n\n"
            "💰 ESTIMATED TOTAL: P[Sum]\n\n"
            "Reply to this message with the numbers you want to keep!"
        )
        
        user_prompt = f"Catalog:\n{catalog_summary}\n\nCustomer Symptoms: {user_symptoms}"
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400
            )
            
            routine_text = completion.choices[0].message.content
            
            st.success("Your Personalized Saina Routine & Quote:")
            st.write(routine_text)
            
            # 5. WHATSAPP CHECKOUT BUTTON WITH BRANDED INTERACTIVE TEMPLATE
            phone_number = "26771334355"
            
            message = (
                f"🌿 *SAINA ESSENTIAL — ORDER SELECTION* 🌿\n\n"
                f"Hello! I generated this custom routine using your AI Coach:\n\n"
                f"{routine_text}\n\n"
                f"---"
                f"Please let me know stock availability so I can confirm my final item selection!"
            )
            
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
            
            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold;">📲 Send Order & Selection to WhatsApp</button>'
                f'</a>', 
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error connecting to AI service: {e}")
