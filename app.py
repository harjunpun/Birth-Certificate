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
st.set_page_config(page_title="Namaste Translate Certificate Generator", page_icon="📄", layout="centered")

# 2. SECURITY LOCK
if st.query_params.get("access") != "namaste":
    st.error("🔒 Access Denied / アクセス拒否")
    st.warning("Please use the official link provided to access this tool. / このツールにアクセスするには、提供された公式リンクを使用してください。")
    st.stop()
    # --- HIDE STREAMLIT MENU & GITHUB ICON ---
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

# Define the input fields 
INPUT_FIELDS = [
    "Issued Place (発行地)", "Registration No. (登録番号)", "Registration Date (登録日)", 
    "Full Name (氏名)", "Date of Birth (生年月日)", "Gender (性別)", 
    "Permanent Address (永住住所)", "Birth Place (出生地)", 
    "Father's Name (父親の氏名)", "Father's ID/Passport (父親の身分証明書番号)", 
    "Mother's Name (母親の氏名)", "Mother's ID/Passport (母親の身分証明書番号)", 
    "Informant Name (情報提供者の氏名)", "Informant ID/Passport (情報提供者の身分証明書番号)", 
    "Translator Name (翻訳者の氏名)", "Address in Japan (日本での住所)"
]

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

# --- DYNAMIC WEB UI ---
user_data = {}

for field in INPUT_FIELDS:
    if field == "Gender (性別)":
        user_data[field] = st.selectbox(field, ["Male (男性)", "Female (女性)", "Third Gender (その他)"])
        
    elif field == "Translator Name (翻訳者の氏名)":
        # Check what the user typed in the "Full Name" box
        full_name_entered = user_data.get("Full Name (氏名)", "").strip()
        
        # Give them the choice between the auto-filled name or "Other"
        display_name = full_name_entered if full_name_entered else "Same as Full Name (氏名と同じ)"
        translator_choice = st.selectbox(field, [display_name, "Other (手動入力)"])
        
        # If they pick "Other", show a new text box so they can type the spouse's name
        if translator_choice == "Other (手動入力)":
            user_data[field] = st.text_input("Enter the Translator's Full Name / 翻訳者の氏名を入力してください")
        else:
            user_data[field] = full_name_entered
            
    else:
        user_data[field] = st.text_input(field)

st.write("---")

# Only generate the PDF when they are completely ready
if st.button("Generate PDF / PDFを作成", type="primary"):
    client_name = user_data["Full Name (氏名)"]
    if not client_name:
        client_name = "Client"

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

