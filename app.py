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
    
    /* Tùy chỉnh màu sắc nút bấm với dải màu Gradient Cam của DAB */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #FC5E15, #FF6E2B);
        color: white; 
        border-radius: 8px;
        padding: 10px 24px; 
        border: none; 
        width: 100%; 
        font-weight: bold; 
        font-size: 16px; 
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(252, 94, 21, 0.3);
    }
    div.stButton > button:first-child:hover { 
        background: linear-gradient(to right, #FF6E2B, #FC5E15);
        box-shadow: 0 6px 8px rgba(252, 94, 21, 0.5);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- HIỆU ỨNG 4 NGÔI SAO BAY LƠ LỬNG TỪ ĐẦU ---
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
    50% {{ transform: translateY(-20px) rotate(10deg); }}
    100% {{ transform: translateY(0px) rotate(0deg); }}
}}
@keyframes floatSideToSide {{
    0% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }}
    50% {{ transform: translateX(15px) translateY(-15px) rotate(-10deg); }}
    100% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }}
}}
.static-star {{
    position: fixed;
    width: 60px;
    height: 60px;
    background-size: contain;
    background-repeat: no-repeat;
    z-index: 9999;
    pointer-events: none;
    opacity: 0.8;
}}
.star-pos-1 {{ top: 15%; left: 10%; background-image: url('{star1}'); animation: floatUpAndDown 4s ease-in-out infinite; }}
.star-pos-2 {{ top: 20%; right: 12%; background-image: url('{star2}'); animation: floatSideToSide 5s ease-in-out infinite; }}
.star-pos-3 {{ bottom: 15%; left: 12%; background-image: url('{star3}'); animation: floatSideToSide 6s ease-in-out infinite; }}
.star-pos-4 {{ bottom: 20%; right: 10%; background-image: url('{star4}'); animation: floatUpAndDown 4.5s ease-in-out infinite; }}
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
st.markdown("<h1 style='text-align: center; color: #004E98; font-weight: 800;'>CỔNG CHECK-IN PHỎNG VẤN<br><span style='color: #FC5E15;'>BAN CHUYÊN MÔN DAB</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #333;'>Chào mừng bạn! Vui lòng điền thông tin bên dưới để lấy số thứ tự nhé.</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("checkin_form", clear_on_submit=True):
        st.markdown("<h3 style='color: #004E98;'>📝 Thông tin ứng viên</h3>", unsafe_allow_html=True)
        
        name = st.text_input("Họ và tên", placeholder="VD: Nguyễn Văn A")
        email = st.text_input("Email", placeholder="VD: nguyenvana@gmail.com")
        committee = st.text_input("Tiểu ban", placeholder="VD: BA / DA / Tester / PM")

        st.write("") 
        submitted = st.form_submit_button("Xác nhận Check-in")

        if submitted:
            if name.strip() and email.strip() and committee.strip():
                try:
                    # Ghi dữ liệu trực tiếp lên Google Sheets
                    row_to_insert = [name, email, committee]
                    sheet.append_row(row_to_insert)
                    
                    st.success("🎉 Check-in thành công!")
                    
                    # Section Số thứ tự với màu Vàng và Xanh của DAB
                    st.markdown(f"""
                        <div style="background-color: #FFE26E; padding: 25px; border-radius: 15px; border: 3px dashed #FC5E15; text-align: center; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <p style="font-size: 20px; color: #004E98; margin-bottom: 5px; font-weight: bold; text-transform: uppercase;">Số Thứ Tự Của Bạn</p>
                            <h1 style="font-size: 80px; color: #FF6E2B; margin: 0; padding: 0; text-shadow: 2px 2px 4px rgba(252, 94, 21, 0.3);">{stt_hien_tai}</h1>
                            <p style="font-size: 16px; color: #004E98; margin-top: 10px; font-weight: 500;">Vui lòng ghi nhớ hoặc chụp ảnh lại màn hình này nhé!</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Trả lại hiệu ứng bóng bay mặc định của Streamlit
                    st.balloons() 
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
