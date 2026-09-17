import streamlit as st
import pandas as pd
import urllib.parse
import datetime
import json
import io
import os
from groq import Groq

# ReportLab imports for automated PDF invoice generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. DISPLAY LOGO IN STREAMLIT UI (COMPACT & UN-SQUASHED)
if os.path.exists("saina logo 2025.jpg"):
    st.image("logo.png", width=120)
else:
    st.write("🌿 **Saina Essential**")

# 2. APP HEADER
st.title("Saina Essential AI Health Coach")
st.write("Tell us how you're feeling, and we'll craft your custom wellness routine.")

# 3. LOAD INVENTORY
df = pd.read_csv("saina_products.csv")

catalog_summary = ""
for _, row in df.iterrows():
    catalog_summary += f"- Name: {row['Product Name']} | Category: {row['Category']} | Price: {row['Price (BWP)']} | Uses: {row['Primary Uses']}\n"

# 4. USER INPUT & FUZZY AI GENERATION
user_symptoms = st.text_input(
    "How can we help you today?", 
    placeholder="e.g., headche, stmach ache, feeling stressd"
)

if st.button("Generate My Routine"):
    if user_symptoms:
        with st.spinner("🌿 Analyzing symptoms & crafting your routine..."):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            system_instructions = (
                "You are Saina's AI Herbalist. Analyze the user's symptoms, accounting for typos or spelling mistakes "
                "(e.g., 'headche' = headache, 'stmach' = stomach).\n"
                "Recommend 2 to 4 relevant products strictly from the provided inventory list.\n"
                "Output your response strictly as a JSON object with a single key 'recommendations' containing a list of objects.\n"
                "Each object must have 'product_name' (string) and 'price' (number).\n"
                "Example format:\n"
                "{\n"
                '  "recommendations": [\n'
                '    {"product_name": "Hibiscus Tea", "price": 120.00},\n'
                '    {"product_name": "Peppermint Essential Oil", "price": 200.00}\n'
                "  ]\n"
                "}\n"
                "Do NOT include markdown formatting or extra conversational text. Return ONLY valid raw JSON."
            )
            
            user_prompt = f"Catalog:\n{catalog_summary}\n\nCustomer Symptoms: {user_symptoms}"
            
            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=400,
                    response_format={"type": "json_object"}
                )
                
                raw_response = completion.choices[0].message.content
                st.session_state["ai_json_output"] = json.loads(raw_response)
                
            except Exception as e:
                st.error(f"Error connecting to AI service: {e}")

# 5. DYNAMIC ITEM SELECTION, DELIVERY & INVOICING
if "ai_json_output" in st.session_state:
    st.markdown("---")
    st.subheader("🌿 Customize Your Order")
    st.info("👉 **Please select the items you want to purchase by ticking the boxes below:**")
    
    data = st.session_state["ai_json_output"]
    recommendations = data.get("recommendations", [])
    
    selected_items = []
    subtotal = 0.0
    
    for idx, item in enumerate(recommendations):
        p_name = item.get("product_name", "Unknown Product")
        p_price = float(item.get("price", 0.0))
        
        if st.checkbox(f"{p_name} — P{p_price:.2f}", value=False, key=f"rec_{idx}_{p_name}"):
            selected_items.append((p_name, p_price))
            subtotal += p_price

    # 6. DELIVERY OPTIONS
    st.markdown("#### 🚚 Delivery Options")
    delivery_option = st.selectbox(
        "Choose fulfillment method:",
        ["Gaborone Pickup (Free)", "Gaborone Local Delivery (P30.00)", "Regional Botswana Courier (P60.00)"]
    )
    
    delivery_cost = 0.0
    if "P30.00" in delivery_option:
        delivery_cost = 30.00
    elif "P60.00" in delivery_option:
        delivery_cost = 60.00

    grand_total = subtotal + delivery_cost

    if selected_items:
        invoice_num = f"SE-{datetime.datetime.now().strftime('%M%S')}"
        today_date = datetime.date.today().strftime("%B %d, %Y")
        
        st.markdown(f"### 📋 **AUTOMATED INVOICE: #{invoice_num}**")
        st.write(f"**Date:** {today_date}")
        
        # DISPLAY SUMMARY ON SCREEN
        invoice_summary = f"🌿 **SAINA ESSENTIAL — INVOICE #{invoice_num}**\n\n"
        items_msg = ""
        for name, p in selected_items:
            items_msg += f"• {name} — P{p:.2f}\n"
            
        invoice_summary += items_msg
        invoice_summary += f"• Delivery ({delivery_option.split(' (')[0]}) — P{delivery_cost:.2f}\n\n"
        invoice_summary += f"💰 **GRAND TOTAL DUE: P{grand_total:.2f}**\n\n"
        invoice_summary += "🏦 **BANK DETAILS:**\n"
        invoice_summary += "• Bank: First National Bank (FNB)\n"
        invoice_summary += "• Account Name: Saina Essential\n"
        invoice_summary += "• Account Number: [Your Acc Number]\n"
        invoice_summary += f"• Reference: {invoice_num}"
        
        st.code(invoice_summary, language="markdown")
        
        # 7. GENERATE PDF INVOICE IN MEMORY (SHADES OF GREEN DESIGN)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        story = []
        
        # Perfectly scaled logo without stretching/squashing
        if os.path.exists("saina logo 2025.jpg"):
            logo_img = RLImage("saina logo 2025.jpg", width=90, height=50, kind='proportional')
            logo_img.hAlign = 'LEFT'
            story.append(logo_img)
            story.append(Spacer(1, 8))
            
        # Green Palette Definition
        forest_green = colors.HexColor("#1B4D3E")
        sage_green = colors.HexColor("#4A7C59")
        mint_bg = colors.HexColor("#E8F5E9")
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=forest_green)
        story.append(Paragraph("OFFICIAL INVOICE", title_style))
        story.append(Spacer(1, 8))
        
        meta_text = f"<b>Invoice #:</b> {invoice_num}<br/><b>Date:</b> {today_date}<br/><b>Status:</b> Awaiting Payment (POP)"
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Table data formatted with green theme
        table_data = [["Item Description", "Price (BWP)"]]
        for name, p in selected_items:
            table_data.append([name, f"P{p:.2f}"])
        table_data.append([f"Fulfillment: {delivery_option}", f"P{delivery_cost:.2f}"])
        table_data.append(["TOTAL DUE", f"P{grand_total:.2f}"])
        
        t = Table(table_data, colWidths=[350, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), forest_green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, -1), (-1, -1), mint_bg),
            ('TEXTCOLOR', (0, -1), (-1, -1), forest_green),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, sage_green),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))
        
        bank_text = (
            "<font color='#1B4D3E'><b>BANKING DETAILS FOR TRANSFER:</b></font><br/>"
            "Bank: First National Bank (FNB)<br/>"
            "Account Name: Saina Essential<br/>"
            "Account Number: [Your Account Number]<br/>"
            "Branch Code: [Branch Code]<br/>"
            "<b>Reference: " + invoice_num + "</b>"
        )
        story.append(Paragraph(bank_text, styles['Normal']))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        
        # DOWNLOAD PDF BUTTON
        st.download_button(
            label="📄 Download Official PDF Invoice",
            data=pdf_bytes,
            file_name=f"Invoice_{invoice_num}.pdf",
            mime="application/pdf"
        )
        
        # 8. WHATSAPP CHECKOUT BUTTON (PHONE NUMBER PRESERVED)
        phone_number = "26774501880"
        
        whatsapp_msg = (
            f"Hello Saina Essential! I generated Invoice #{invoice_num} for my order:\n\n"
            f"{items_msg}"
            f"• Fulfillment: {delivery_option}\n\n"
            f"💰 GRAND TOTAL: P{grand_total:.2f}\n\n"
            f"Please verify stock so I can transfer funds using Reference: {invoice_num} and attach my Proof of Payment."
        )
        
        encoded_msg = urllib.parse.quote(whatsapp_msg)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
        
        st.markdown(
            f'<a href="{whatsapp_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold; margin-top:10px;">📲 Submit Order & Invoice #{invoice_num} to WhatsApp</button>'
            f'</a>', 
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ No items selected yet. Please tick at least one item above to generate your invoice and checkout options.")
