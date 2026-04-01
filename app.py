import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Check-in Phỏng vấn", page_icon="💼", layout="wide")

# CSS làm đẹp giao diện
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #2563EB; color: white; border-radius: 8px;
        padding: 10px 24px; border: none; width: 100%; font-weight: bold; font-size: 16px; transition: 0.3s;
    }
    div.stButton > button:first-child:hover { background-color: #1D4ED8; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# Khai báo tên file
FILE = "data.csv"

# Tiêu đề
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏢 Cổng Check-in Phỏng vấn</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Chào mừng bạn! Vui lòng điền thông tin bên dưới để lấy số thứ tự nhé.</p>", unsafe_allow_html=True)
st.divider()

# Căn giữa form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Thông tin ứng viên")
        
        # ĐÃ SỬA: Form nhập liệu khớp với 3 cột của Ngọc
        name = st.text_input("Họ và tên", placeholder="VD: Nguyễn Văn A")
        email = st.text_input("Email", placeholder="VD: nguyenvana@gmail.com")
        committee = st.text_input("Tiểu ban", placeholder="VD: Chuyên môn / Truyền thông")

        st.write("") 
        submitted = st.form_submit_button("Xác nhận Check-in")

        if submitted:
            # Kiểm tra xem có ô nào bị bỏ trống không
            if name.strip() and email.strip() and committee.strip():
                
                # Đọc file cũ nếu có, không thì tạo DataFrame mới với đúng 3 cột của Ngọc
                if os.path.exists(FILE):
                    df = pd.read_csv(FILE)
                else:
                    df = pd.DataFrame(columns=["Name", "Email", "Tiểu ban"])

                stt = len(df) + 1

                # ĐÃ SỬA: Tạo dòng dữ liệu mới với key khớp CHÍNH XÁC tên cột trong file CSV
                new_row = pd.DataFrame([{
                    "Name": name, 
                    "Email": email, 
                    "Tiểu ban": committee
                }])
                
                # Nối dữ liệu và lưu lại
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE, index=False)

                st.success(f"🎉 **Check-in thành công!** Số thứ tự của bạn là: **{stt}**")
                st.balloons() 
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
