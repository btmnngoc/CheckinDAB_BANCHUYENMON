import streamlit as st
import pandas as pd
import os

FILE = "data.csv"

st.title("Check-in Phỏng vấn")

# Sử dụng st.form để quản lý trạng thái nhập liệu
# clear_on_submit=True sẽ tự động xóa trắng form sau khi submit thành công
with st.form("checkin_form", clear_on_submit=True):
    name = st.text_input("Họ tên")
    phone = st.text_input("Email")
    position = st.text_input("Tiểu ban")

    # Nút submit đặt bên trong form
    submitted = st.form_submit_button("Check-in")

    if submitted:
        # Kiểm tra xem các trường có bị bỏ trống hay không
        if name.strip() and phone.strip() and position.strip():
            if os.path.exists(FILE):
                df = pd.read_csv(FILE)
            else:
                df = pd.DataFrame(columns=["name", "phone", "position"])

            stt = len(df) + 1

            new_row = pd.DataFrame([[name, phone, position]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(FILE, index=False)

            st.success(f"Check-in thành công! Số thứ tự của bạn là: {stt}")
        else:
            st.error("Vui lòng điền đầy đủ thông tin trước khi Check-in.")
