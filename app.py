import streamlit as st
import pandas as pd
import os

# 1. Cấu hình trang (Hiển thị icon và tiêu đề trên tab trình duyệt)
st.set_page_config(
    page_title="Check-in Phỏng vấn",
    page_icon="💼",
    layout="wide"
)

# 2. Thêm CSS tùy chỉnh để làm đẹp nút bấm và căn giữa văn bản
st.markdown("""
    <style>
    /* Tùy chỉnh màu sắc và kích thước nút Check-in */
    div.stButton > button:first-child {
        background-color: #2563EB; /* Màu xanh biển đậm */
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        width: 100%;
        font-weight: bold;
        font-size: 16px;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8; /* Đổi màu khi di chuột vào */
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

FILE = "data.csv"

# 3. Tiêu đề và lời chào được căn giữa
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏢 Cổng Check-in Phỏng vấn</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Chào mừng bạn! Vui lòng điền thông tin bên dưới để lấy số thứ tự nhé.</p>", unsafe_allow_html=True)
st.divider()

# 4. Sử dụng columns để ép form vào giữa màn hình (giúp form không bị quá to trên máy tính)
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("checkin_form", clear_on_submit=True):
        st.subheader("📝 Thông tin ứng viên")
        
        # Thêm placeholder để hướng dẫn người dùng nhập liệu
        name = st.text_input("Họ và tên", placeholder="VD: Nguyễn Văn A")
        phone = st.text_input("Số điện thoại", placeholder="VD: 0987654321")
        position = st.text_input("Vị trí ứng tuyển", placeholder="VD: Chuyên viên Marketing")

        st.write("") # Tạo một chút khoảng trống cho thoáng
        submitted = st.form_submit_button("Xác nhận Check-in")

        if submitted:
            if name.strip() and phone.strip() and position.strip():
                if os.path.exists(FILE):
                    df = pd.read_csv(FILE)
                else:
                    df = pd.DataFrame(columns=["name", "phone", "position"])

                stt = len(df) + 1

                new_row = pd.DataFrame([[name, phone, position]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE, index=False)

                # Hiển thị thông báo thành công bự hơn và thêm hiệu ứng bóng bay
                st.success(f"🎉 **Check-in thành công!** Số thứ tự của bạn là: **{stt}**")
                st.balloons() 
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
