import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
import os
import random
import time

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

# --- HÀM TẠO HIỆU ỨNG ẢNH BAY BAY ---
def throw_custom_stars():
    # Đọc và mã hóa 4 ảnh thành base64 để nhúng vào web
    image_files = ["star1.png", "star2.png", "star3.png", "star4.png"]
    encoded_images = []
    
    for img in image_files:
        if os.path.exists(img):
            with open(img, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                encoded_images.append(f"data:image/png;base64,{b64}")
                
    if not encoded_images:
        return # Nếu không tìm thấy ảnh nào thì bỏ qua hiệu ứng
        
    # Tạo CSS Animation cho các ảnh bay lên
    css_animation = """
    <style>
    @keyframes flyUpAndSpin {
        0% { transform: translateY(110vh) rotate(0deg) scale(0.5); opacity: 1; }
        100% { transform: translateY(-20vh) rotate(360deg) scale(1.2); opacity: 0; }
    }
    .custom-star {
        position: fixed;
        bottom: -10%;
        width: 60px;
        height: 60px;
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999999;
        pointer-events: none;
        animation: flyUpAndSpin 3.5s ease-out forwards;
    }
    </style>
    """
    
    # Tạo HTML để thả ngẫu nhiên nhiều sao từ 4 ảnh đã chọn
    stars_html = ""
    for i in range(25): # Thả 25 icon bay lên
        img_src = random.choice(encoded_images)
        left_pos = random.randint(5, 95) # Vị trí ngẫu nhiên theo chiều ngang
        delay = random.uniform(0, 1.5) # Độ trễ ngẫu nhiên
        stars_html += f'<div class="custom-star" style="background-image: url({img_src}); left: {left_pos}%; animation-delay: {delay}s;"></div>'
        
    # In ra màn hình
    placeholder = st.empty()
    placeholder.markdown(css_animation + stars_html, unsafe_allow_html=True)
    
    # Xóa element sau khi bay xong để không nặng web
    time.sleep(4)
    placeholder.empty()

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
data = sheet.get_all_records()
stt_hien_tai = len(data) + 1

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
                    
                    # Gọi hàm tung ảnh tùy chỉnh thay vì st.balloons()
                    throw_custom_stars() 
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
