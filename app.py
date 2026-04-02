import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
import os

st.set_page_config(page_title="Check-in DAB", page_icon="⭐", layout="wide")

# --- MÀU SẮC CHỦ ĐẠO CỦA DAB ---
# 004E98 (Xanh đậm), FC5E15 (Cam sáng), FFE26E (Vàng nhạt), FF6E2B (Cam đậm)

st.markdown("""
    <style>
    /* Nền trang web */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Làm đẹp Form nhập liệu */
    [data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
    }

    /* Tùy chỉnh màu sắc nút bấm với dải màu Gradient Cam của DAB */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #FC5E15, #FF6E2B);
        color: white; 
        border-radius: 10px;
        padding: 12px 24px; 
        border: none; 
        width: 100%; 
        font-weight: 800; 
        font-size: 16px; 
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 6px 12px rgba(252, 94, 21, 0.25);
        margin-top: 10px;
    }
    div.stButton > button:first-child:hover { 
        background: linear-gradient(135deg, #FF6E2B, #FC5E15);
        box-shadow: 0 8px 16px rgba(252, 94, 21, 0.4);
        transform: translateY(-3px);
    }
    </style>
""", unsafe_allow_html=True)

# --- HIỆU ỨNG 4 NGÔI SAO BAY LƠ LỬNG TỪ ĐẦU (ĐÃ PHÓNG TO) ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    # Fallback dùng emoji nếu thiếu ảnh
    return "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"

# Tải 4 ảnh (hoặc ảnh fallback)
star1 = get_base64_image("star1.png")
star2 = get_base64_image("star2.png")
star3 = get_base64_image("star3.png")
star4 = get_base64_image("star4.png")

floating_stars_css = f"""
<style>
@keyframes floatUpAndDown {{
    0% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-25px) rotate(12deg); }}
    100% {{ transform: translateY(0px) rotate(0deg); }}
}}
@keyframes floatSideToSide {{
    0% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }}
    50% {{ transform: translateX(20px) translateY(-15px) rotate(-12deg); }}
    100% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }}
}}
.static-star {{
    position: fixed;
    width: 220px;  /* Đã tăng kích thước sao to hơn */
    height: 220px; /* Đã tăng kích thước sao to hơn */
    background-size: contain;
    background-repeat: no-repeat;
    z-index: 9999;
    pointer-events: none;
    opacity: 0.85;
}}
/* Điều chỉnh lại vị trí một chút để sao to không che mất nội dung */
.star-pos-1 {{ top: 12%; left: 8%; background-image: url('{star1}'); animation: floatUpAndDown 4s ease-in-out infinite; }}
.star-pos-2 {{ top: 18%; right: 8%; background-image: url('{star2}'); animation: floatSideToSide 5s ease-in-out infinite; }}
.star-pos-3 {{ bottom: 12%; left: 8%; background-image: url('{star3}'); animation: floatSideToSide 6s ease-in-out infinite; }}
.star-pos-4 {{ bottom: 15%; right: 8%; background-image: url('{star4}'); animation: floatUpAndDown 4.5s ease-in-out infinite; }}
</style>
<div class="static-star star-pos-1"></div>
<div class="static-star star-pos-2"></div>
<div class="static-star star-pos-3"></div>
<div class="static-star star-pos-4"></div>
"""
st.markdown(floating_stars_css, unsafe_allow_html=True)


# --- KẾT NỐI GOOGLE SHEETS ---
SHEET_NAME = "Check-in DAB" 

@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    return client

client = init_connection()
sheet = client.open(SHEET_NAME).sheet1
# Dùng get_all_values() sẽ an toàn hơn, không bị lỗi dù sheet trống
data = sheet.get_all_values()
# Nếu sheet đã có dòng tiêu đề, số thứ tự sẽ bằng đúng số lượng dòng hiện tại
stt_hien_tai = len(data) if len(data) > 0 else 1


# --- GIAO DIỆN CHÍNH ---
st.write("") # Spacer
st.markdown("<h1 style='text-align: center; color: #004E98; font-weight: 900; letter-spacing: -0.5px;'>CỔNG CHECK-IN PHỎNG VẤN<br><span style='color: #FC5E15;'>BAN CHUYÊN MÔN DAB</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 17px; color: #64748b; margin-bottom: 30px;'>Chào mừng bạn! Vui lòng điền thông tin bên dưới để lấy số thứ tự nhé.</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("checkin_form", clear_on_submit=True):
        st.markdown("<h3 style='color: #004E98; margin-bottom: 20px; font-size: 22px;'>Thông tin ứng viên</h3>", unsafe_allow_html=True)
        
        name = st.text_input("Họ và tên", placeholder="VD: Nguyễn Văn A")
        email = st.text_input("Email", placeholder="VD: nguyenvana@gmail.com")
        committee = st.text_input("Tiểu ban", placeholder="VD: BA / DA / Tester / PM")

        st.write("") 
        submitted = st.form_submit_button("XÁC NHẬN CHECK-IN")

        if submitted:
            if name.strip() and email.strip() and committee.strip():
                try:
                   # Ghi dữ liệu trực tiếp lên Google Sheets
                    row_to_insert = [name, email, committee]
                    sheet.append_row(row_to_insert)
                    
                    # Đã nối toàn bộ thành 1 dòng duy nhất để Streamlit không bị lỗi Markdown
                    ticket_html = f"""<div style="margin: 30px auto 10px auto; max-width: 380px; background: white; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; position: relative; overflow: hidden;"><div style="background-color: #004E98; color: white; padding: 20px; text-align: center;"><h2 style="margin: 0; font-size: 20px; font-weight: 800; letter-spacing: 2px;">VÉ CHỜ PHỎNG VẤN</h2><p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.8;">BAN CHUYÊN MÔN - DAB</p></div><div style="position: relative; height: 0; border-top: 3px dashed #FC5E15; margin-top: 0px;"><div style="position: absolute; top: -15px; left: -15px; width: 30px; height: 30px; background-color: #F8FAFC; border-radius: 50%; box-shadow: inset -3px 0 5px rgba(0,0,0,0.05);"></div><div style="position: absolute; top: -15px; right: -15px; width: 30px; height: 30px; background-color: #F8FAFC; border-radius: 50%; box-shadow: inset 3px 0 5px rgba(0,0,0,0.05);"></div></div><div style="background-color: #FFE26E; padding: 40px 20px; text-align: center;"><p style="margin: 0; font-size: 15px; color: #004E98; font-weight: 700; text-transform: uppercase;">Số Thứ Tự Của Bạn</p><h1 style="margin: 10px 0; font-size: 90px; color: #FF6E2B; line-height: 1; font-weight: 900; text-shadow: 3px 3px 0px rgba(255,255,255,0.9);">{stt_hien_tai}</h1></div><div style="padding: 20px; text-align: center; background-color: white;"><h3 style="margin: 0; color: #004E98; font-size: 18px; text-transform: uppercase;">{name}</h3><p style="margin: 5px 0 0 0; color: #64748b; font-size: 15px;">Tiểu ban: <span style="font-weight: 800; color: #FC5E15;">{committee}</span></p><hr style="border: none; border-top: 1px solid #e2e8f0; margin: 15px 0;"><p style="margin: 0; font-size: 13px; color: #94a3b8; font-style: italic;">Hãy ghi nhớ số vé của mình nhé!</p></div></div>"""
                    
                    st.markdown(ticket_html, unsafe_allow_html=True)
                    
                    # Trả lại hiệu ứng bóng bay mặc định của Streamlit
                    st.balloons()
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
