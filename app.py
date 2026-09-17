import streamlit as st
import pandas as pd
import urllib.parse
import datetime
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

# 5. AUTOMATED ITEM SELECTION & INVOICE GENERATION
if "raw_ai_output" in st.session_state:
    st.markdown("---")
    st.subheader("🌿 Customize Your Order")
    st.info("👉 **Please select the items you want to purchase by ticking the boxes below:**")
    
    lines = st.session_state["raw_ai_output"].strip().split("\n")
    selected_items = []
    total_price = 0
    
    for line in lines:
        if "PRODUCT:" in line and "PRICE:" in line:
            try:
                parts = line.split("|")
                prod_name = parts[0].replace("PRODUCT:", "").strip()
                price = float(parts[1].replace("PRICE:", "").replace("P", "").strip())
                
                # Checkboxes now default to Unticked (value=False)
                if st.checkbox(f"{prod_name} — P{price:.2f}", value=False, key=prod_name):
                    selected_items.append((prod_name, price))
                    total_price += price
            except Exception:
                continue

    if selected_items:
        invoice_num = f"SE-{datetime.datetime.now().strftime('%M%S')}"
        today_date = datetime.date.today().strftime("%B %d, %Y")
        
        # DISPLAY DIGITAL INVOICE ON SCREEN
        st.markdown(f"### 📋 **AUTOMATED INVOICE: #{invoice_num}**")
        st.write(f"**Date:** {today_date}")
        
        invoice_text = f"🌿 **SAINA ESSENTIAL — INVOICE #{invoice_num}**\n\n"
        items_msg = ""
        for name, p in selected_items:
            items_msg += f"• {name} — P{p:.2f}\n"
            
        invoice_text += items_msg
        invoice_text += f"\n💰 **TOTAL DUE: P{total_price:.2f}**\n\n"
        invoice_text += "🏦 **BANK DETAILS:**\n"
        invoice_text += "• Bank: FNB / First National Bank\n"
        invoice_text += "• Account Name: Saina Essential\n"
        invoice_text += "• Account Number: [Your Acc Number]\n"
        invoice_text += f"• Reference: {invoice_num}"
        
        st.code(invoice_text, language="markdown")
        
        # 6. WHATSAPP BUTTON WITH INVOICE DETAILS PRE-FILLED
        phone_number = "26771334355"
        
        whatsapp_msg = (
            f"Hello Saina Essential! I generated Invoice #{invoice_num} for my selected order:\n\n"
            f"{items_msg}\n"
            f"💰 TOTAL: P{total_price:.2f}\n\n"
            f"Please verify stock so I can transfer funds using Reference: {invoice_num} and submit my Proof of Payment."
        )
        
        encoded_msg = urllib.parse.quote(whatsapp_msg)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
        
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold;">📲 Submit Order & Invoice #{invoice_num} to WhatsApp</button>'
            f'</a>', 
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ No items selected yet. Please tick at least one item above to generate your invoice and WhatsApp checkout button.")
