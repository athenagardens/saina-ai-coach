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
st.title("Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# 3. LOAD INVENTORY
df = pd.read_csv("saina_products.csv")

catalog_summary = ""
for _, row in df.iterrows():
    catalog_summary += f"- {row['Product Name']} ({row['Category']}): P{row['Price (BWP)']}. Uses: {row['Primary Uses']}\n"

# 4. USER INPUT & AI GENERATION
user_symptoms = st.text_input("How can we help you today?", placeholder="e.g., I have a headache and feel stressed")

if st.button("Generate My Routine"):
    if user_symptoms:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        system_instructions = (
            "You are Saina's AI Herbalist. Recommend products strictly from the provided inventory list. "
            "Keep recommendations concise. List only the recommended product names and prices in this exact clean line format:\n"
            "PRODUCT: [Exact Product Name] | PRICE: [Numeric Price Only]\n"
            "Do not add markdown formatting or extra text lines in between PRODUCT lines."
        )
        
        user_prompt = f"Catalog:\n{catalog_summary}\n\nCustomer Symptoms: {user_symptoms}"
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300
            )
            
            raw_response = completion.choices[0].message.content
            st.session_state["raw_ai_output"] = raw_response
            
        except Exception as e:
            st.error(f"Error connecting to AI service: {e}")

# 5. DYNAMIC ITEM SELECTION & CHECKOUT
if "raw_ai_output" in st.session_state:
    st.markdown("---")
    st.subheader("🌿 Customize Your Order")
    st.write("Uncheck any items you do not wish to purchase right now:")
    
    # Parse items returned by AI
    lines = st.session_state["raw_ai_output"].strip().split("\n")
    selected_items = []
    total_price = 0
    
    for line in lines:
        if "PRODUCT:" in line and "PRICE:" in line:
            try:
                parts = line.split("|")
                prod_name = parts[0].replace("PRODUCT:", "").strip()
                price_str = parts[1].replace("PRICE:", "").replace("P", "").strip()
                price = float(price_str)
                
                # Create a Streamlit Checkbox for each product
                if st.checkbox(f"{prod_name} — P{price:.2f}", value=True, key=prod_name):
                    selected_items.append(f"• {prod_name} (P{price:.2f})")
                    total_price += price
            except Exception:
                continue

    st.markdown(f"### 💰 **Confirmed Total: P{total_price:.2f}**")
    
    # 6. WHATSAPP BUTTON WITH ONLY CHECKED ITEMS
    if selected_items:
        items_formatted = "\n".join(selected_items)
        phone_number = "26771334355"
        
        whatsapp_msg = (
            f"🌿 *SAINA ESSENTIAL — CONFIRMED ORDER* 🌿\n\n"
            f"Hello! I have selected the following items from my AI consultation:\n\n"
            f"{items_formatted}\n\n"
            f"💰 *TOTAL ORDER: P{total_price:.2f}*\n\n"
            f"Please verify stock and issue an invoice so I can provide Proof of Payment (POP)."
        )
        
        encoded_msg = urllib.parse.quote(whatsapp_msg)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
        
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold;">📲 Send Confirmed Items to WhatsApp</button>'
            f'</a>', 
            unsafe_allow_html=True
        )
    else:
        st.warning("Please check at least one item to proceed to WhatsApp checkout.")
