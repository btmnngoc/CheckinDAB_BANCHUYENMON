import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Check-in Phỏng vấn", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #2563EB; color: white; border-radius: 8px;
        padding: 10px 24px; border: none; width: 100%; font-weight: bold; font-size: 16px; transition: 0.3s;
    }
    div.stButton > button:first-child:hover { background-color: #1D4ED8; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- KẾT NỐI GOOGLE SHEETS ---
# Đổi tên này thành đúng tên file Google Sheets của Ngọc
SHEET_NAME = "Check-in DAB" 

@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Lấy chìa khóa từ Streamlit Secrets
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    return client

client = init_connection()

# Mở Sheet1 của file
sheet = client.open(SHEET_NAME).sheet1
# Lấy toàn bộ data hiện tại để đếm số thứ tự
data = sheet.get_all_records()
stt_hien_tai = len(data) + 1

# --- GIAO DIỆN CHÍNH ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏢 Cổng Check-in Phỏng vấn Ban Chuyên môn DAB</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Chào mừng bạn! Vui lòng điền thông tin bên dưới để lấy số thứ tự nhé.</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Thông tin ứng viên")
        
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
                    
                    st.markdown(f"""
                        <div style="background-color: #EFF6FF; padding: 25px; border-radius: 12px; border: 2px dashed #3B82F6; text-align: center; margin-top: 15px; margin-bottom: 15px;">
                            <p style="font-size: 18px; color: #1E3A8A; margin-bottom: 5px; font-weight: bold;">SỐ THỨ TỰ CỦA BẠN</p>
                            <h1 style="font-size: 70px; color: #DC2626; margin: 0; padding: 0;">{stt_hien_tai}</h1>
                            <p style="font-size: 15px; color: #4B5563; margin-top: 10px;">Vui lòng ghi nhớ hoặc chụp ảnh lại màn hình này nhé!</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons() 
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
