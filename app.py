import streamlit as st
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Birth certificate(出生証明書)", page_icon="📄", layout="centered")

# 2. SECURITY LOCK & STEALTH MODE
if st.query_params.get("access") != "namaste":
    st.error("🔒 Access Denied / アクセス拒否")
    st.warning("Please use the official link provided to access this tool. / このツールにアクセスするには、提供された公式リンクを使用してください。")
    st.stop()
    
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. APP HEADER
st.title("📄 Birth Certificate Generator")
st.markdown("Fill out the details below to instantly generate your formatted PDF certificate. / 以下の詳細を入力して、PDF証明書を作成してください。")
st.write("---")

def load_font():
    font_path = "msgothic.ttc" 
    try:
        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path, subfontIndex=0))
        return 'JapaneseFont'
    except Exception as e:
        st.error(f"⚠️ Font Error: Could not load '{font_path}'. Please ensure the font file is uploaded to the server.")
        return 'Helvetica'

def generate_pdf(data):
    buffer = io.BytesIO()
    font_name = load_font()

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=70, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName=font_name, fontSize=16, alignment=1, spaceAfter=15)
    center_style = ParagraphStyle('Center', fontName=font_name, fontSize=11, alignment=1)
    cell_style = ParagraphStyle('CellStyle', fontName=font_name, fontSize=10, leading=12)

    def P(text):
        return Paragraph(text, cell_style)

    # Add Issued Place
    elements.append(Paragraph(data["Issued Place (発行地)"], center_style))
    elements.append(Spacer(1, 10))

    # Add Title
    elements.append(Paragraph("出生登録証明書（Birth Certificate）", title_style))
    elements.append(Spacer(1, 10))

    # --- TABLE 1: MAIN DATA ---
    main_table_data = [
        [P("登録番号<br/>(Registration No.)"), "", P(data["Registration No. (登録番号)"])],
        [P("登録日<br/>(Registration Date)"), "", P(data["Registration Date (登録日)"])],
        [P("氏名<br/>(Full Name)"), "", P(data["Full Name (氏名)"])],
        [P("生年月日<br/>(Date of birth)"), "", P(data["Date of Birth (生年月日)"])],
        [P("性別<br/>(Sex)"), "", P(data["Gender (性別)"])],
        [P("永住住所<br/>(Permanent address)"), "", P(data["Permanent Address (永住住所)"])],
        [P("出生地<br/>(Birth place)"), "", P(data["Birth Place (出生地)"])],
        
        [P("父親<br/>(Father's Details)"), P("氏名<br/>(Name)"), P(data["Father's Name (父親の氏名)"])],
        ["", P("NIN / パスポート番号<br/>(ID/Passport No.)"), P(data["Father's ID/Passport (父親の身分証明書番号)"])],
        
        [P("母親<br/>(Mother's Details)"), P("氏名<br/>(Name)"), P(data["Mother's Name (母親の氏名)"])],
        ["", P("NIN / パスポート番号<br/>(ID/Passport No.)"), P(data["Mother's ID/Passport (母親の身分証明書番号)"])],
        
        [P("情報提供者<br/>(Informant's Details)"), P("氏名<br/>(Name)"), P(data["Informant Name (情報提供者の氏名)"])],
        ["", P("NIN / パスポート番号<br/>(ID/Passport No.)"), P(data["Informant ID/Passport (情報提供者の身分証明書番号)"])]
    ]

    t_main = Table(main_table_data, colWidths=[110, 140, 260]) 
    t_main.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (0, 5), (1, 5)),
        ('SPAN', (0, 6), (1, 6)),
        ('SPAN', (0, 7), (0, 8)),
        ('SPAN', (0, 9), (0, 10)),
        ('SPAN', (0, 11), (0, 12)),
    ]))
    
    elements.append(t_main)
    elements.append(Spacer(1, 15))

    # --- TABLE 2: TRANSLATOR DATA ---
    translator_table_data = [
        [P("翻訳者<br/>(Translator)"), "", P(data["Translator Name (翻訳者の氏名)"])],
        [P("日本の住所<br/>(Address in Japan)"), "", P(data["Address in Japan (日本での住所)"])]
    ]

    t_translator = Table(translator_table_data, colWidths=[110, 140, 260])
    t_translator.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
    ]))

    elements.append(t_translator)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

# --- DATE LISTS ---
years = ["Year"] + [str(y) for y in range(2040, 1920, -1)]
months = ["Month"] + [str(m).zfill(2) for m in range(1, 13)]
days = ["Day"] + [str(d).zfill(2) for d in range(1, 32)]

# --- UI FORM ---
issued_place = st.text_input("Issued Place (発行地)", placeholder="eg.ネパール・ガンダキ州カスキ郡ポカラ市役所（第33区）")
reg_no = st.text_input("Registration No. (登録番号)")

st.write("Registration Date (登録日)")
col1, col2, col3 = st.columns(3)
reg_y = col1.selectbox("年 (Year)", years, key="ry")
reg_m = col2.selectbox("月 (Month)", months, key="rm")
reg_d = col3.selectbox("日 (Day)", days, key="rd")
reg_date = f"{reg_y}-{reg_m}-{reg_d}" if "Year" not in reg_y and "Month" not in reg_m and "Day" not in reg_d else ""

full_name = st.text_input("Full Name (氏名)", placeholder="eg.プン，アルズン マガル")

st.write("Date of Birth (生年月日)")
col4, col5, col6 = st.columns(3)
dob_y = col4.selectbox("年 (Year)", years, key="dy")
dob_m = col5.selectbox("月 (Month)", months, key="dm")
dob_d = col6.selectbox("日 (Day)", days, key="dd")
dob_date = f"{dob_y}-{dob_m}-{dob_d}" if "Year" not in dob_y and "Month" not in dob_m and "Day" not in dob_d else ""

gender = st.selectbox("Gender (性別)", ["Male (男性)", "Female (女性)", "Third Gender (その他)"])
address = st.text_input("Permanent Address (永住住所)")
birth_place = st.text_input("Birth Place (出生地)")

f_name = st.text_input("Father's Name (父親の氏名)")
f_id = st.text_input("Father's ID/Passport (父親の身分証明書番号)")

m_name = st.text_input("Mother's Name (母親の氏名)")
m_id = st.text_input("Mother's ID/Passport (母親の身分証明書番号)")

st.write("---")

# --- SMART INFORMANT LOGIC ---
informant_options = []
if f_name: informant_options.append(f_name)
if m_name: informant_options.append(m_name)
if full_name: informant_options.append(full_name)
informant_options.append("Other (手動入力)")

informant_choice = st.selectbox("Informant Name (情報提供者の氏名)", informant_options)

# Auto-fill ID Logic based on choice
if informant_choice == "Other (手動入力)":
    informant_name = st.text_input("Enter the Informant's Full Name / 情報提供者の氏名を入力してください")
    default_inf_id = ""
else:
    informant_name = informant_choice
    if informant_choice == f_name and f_name != "":
        default_inf_id = f_id
    elif informant_choice == m_name and m_name != "":
        default_inf_id = m_id
    else:
        default_inf_id = "" # Clear ID if "Full Name" is chosen

informant_id = st.text_input("Informant ID/Passport (情報提供者の身分証明書番号)", value=default_inf_id)

# --- SMART TRANSLATOR LOGIC ---
display_name = full_name if full_name else "Same as Full Name (氏名と同じ)"
translator_choice = st.selectbox("Translator Name (翻訳者の氏名)", [display_name, "Other (手動入力)"])

if translator_choice == "Other (手動入力)":
    translator_name = st.text_input("Enter the Translator's Full Name / 翻訳者の氏名を入力してください")
else:
    translator_name = full_name

address_japan = st.text_input("Address in Japan (日本での住所)")

st.write("---")

# --- GENERATE PDF BUTTON ---
if st.button("Generate PDF / PDFを作成", type="primary"):
    # Compile all data into the dictionary format expected by the PDF function
    user_data = {
        "Issued Place (発行地)": issued_place,
        "Registration No. (登録番号)": reg_no,
        "Registration Date (登録日)": reg_date,
        "Full Name (氏名)": full_name,
        "Date of Birth (生年月日)": dob_date,
        "Gender (性別)": gender,
        "Permanent Address (永住住所)": address,
        "Birth Place (出生地)": birth_place,
        "Father's Name (父親の氏名)": f_name,
        "Father's ID/Passport (父親の身分証明書番号)": f_id,
        "Mother's Name (母親の氏名)": m_name,
        "Mother's ID/Passport (母親の身分証明書番号)": m_id,
        "Informant Name (情報提供者の氏名)": informant_name,
        "Informant ID/Passport (情報提供者の身分証明書番号)": informant_id,
        "Translator Name (翻訳者の氏名)": translator_name,
        "Address in Japan (日本での住所)": address_japan
    }

    client_name = full_name if full_name else "Client"
    file_name = f"Birth_Certificate_{client_name}.pdf"
    
    with st.spinner("Generating document... / ドキュメントを作成中..."):
        pdf_buffer = generate_pdf(user_data)
        
        st.success("Success! Click the button below to download your certificate. / 成功しました！下のボタンをクリックして証明書をダウンロードしてください。")
        
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=file_name,
            mime="application/pdf"
        )

