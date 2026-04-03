import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Check-in DAB", page_icon="⭐", layout="wide")

# ==========================================
# CẤU HÌNH LIÊN KẾT TẠI ĐÂY
# ==========================================
LINK_MEET_1 = "https://meet.google.com/xye-mima-icg" # <--- Nhớ dán link Meet phòng 1 của Ngọc vào đây
LINK_MEET_2 = "https://meet.google.com/bjc-ucnq-apu" # <--- Nhớ dán link Meet phòng 2 của Ngọc vào đây

LINK_CALENDAR_1 = "https://calendar.app.google/qb4NowMZsKmgGNJy5" # Lịch Phòng 1
LINK_CALENDAR_2 = "https://calendar.app.google/tY5VW4eSLtYEF9Zt8" # Lịch Phòng 2
# ==========================================

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

# --- HIỆU ỨNG NGÔI SAO TƯƠNG TÁC (KÉO THẢ + LẤP LÁNH) ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"

star1, star2, star3, star4 = get_base64_image("star1.png"), get_base64_image("star2.png"), get_base64_image("star3.png"), get_base64_image("star4.png")

interactive_stars_css_html = f"""
<style>
@keyframes floatUpAndDown {{ 0% {{ transform: translateY(0px) rotate(0deg); }} 50% {{ transform: translateY(-25px) rotate(12deg); }} 100% {{ transform: translateY(0px) rotate(0deg); }} }}
@keyframes floatSideToSide {{ 0% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }} 50% {{ transform: translateX(20px) translateY(-15px) rotate(-12deg); }} 100% {{ transform: translateX(0px) translateY(0px) rotate(0deg); }} }}
.interactive-star {{ position: fixed; width: 110px; height: 110px; background-size: contain; background-repeat: no-repeat; z-index: 999999; cursor: grab; pointer-events: auto; transition: filter 0.3s ease, transform 0.3s ease; }}
.interactive-star:active {{ cursor: grabbing; }}
.sparkle-particle {{ position: fixed; width: 8px; height: 8px; background-color: #FFE26E; border-radius: 50%; z-index: 999998; pointer-events: none; box-shadow: 0 0 10px #FFE26E, 0 0 20px #FC5E15; animation: sparkle-fade-up 0.8s ease-out forwards; }}
@keyframes sparkle-fade-up {{ 0% {{ transform: translateY(0) scale(1); opacity: 1; }} 100% {{ transform: translateY(-30px) scale(0); opacity: 0; }} }}
.star-pos-1 {{ top: 12%; left: 8%; background-image: url('{star1}'); animation: floatUpAndDown 4s ease-in-out infinite; }}
.star-pos-2 {{ top: 18%; right: 8%; background-image: url('{star2}'); animation: floatSideToSide 5s ease-in-out infinite; }}
.star-pos-3 {{ bottom: 12%; left: 8%; background-image: url('{star3}'); animation: floatSideToSide 6s ease-in-out infinite; }}
.star-pos-4 {{ bottom: 15%; right: 8%; background-image: url('{star4}'); animation: floatUpAndDown 4.5s ease-in-out infinite; }}
</style>
<div class="interactive-star star-pos-1" id="star-1"></div><div class="interactive-star star-pos-2" id="star-2"></div><div class="interactive-star star-pos-3" id="star-3"></div><div class="interactive-star star-pos-4" id="star-4"></div>
"""
st.markdown(interactive_stars_css_html, unsafe_allow_html=True)

drag_drop_js = """
<script>
    const parentDoc = window.parent.document;
    let sparkleInterval;
    function createSparkle(x, y) {
        const sparkle = parentDoc.createElement('div');
        sparkle.className = 'sparkle-particle';
        sparkle.style.left = (x - 4) + 'px'; sparkle.style.top = (y - 4) + 'px';
        parentDoc.body.appendChild(sparkle);
        setTimeout(() => sparkle.remove(), 800);
    }
    function makeInteractive(el) {
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;
        const dragStart = (e) => {
            e.preventDefault(); isDragging = true;
            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            startX = clientX; startY = clientY;
            const rect = el.getBoundingClientRect();
            initialLeft = rect.left; initialTop = rect.top;
            el.style.animation = 'none'; el.style.transition = 'none'; 
            sparkleInterval = setInterval(() => {
                const currentRect = el.getBoundingClientRect();
                const sparkleX = currentRect.left + Math.random() * currentRect.width;
                const sparkleY = currentRect.top + Math.random() * currentRect.height;
                createSparkle(sparkleX, sparkleY);
            }, 50); 
            parentDoc.addEventListener('mousemove', dragMove); parentDoc.addEventListener('mouseup', dragEnd);
            parentDoc.addEventListener('touchmove', dragMove, {passive: false}); parentDoc.addEventListener('touchend', dragEnd);
        };
        const dragMove = (e) => {
            const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            const dx = clientX - startX; const dy = clientY - startY;
            if (isDragging) { e.preventDefault(); el.style.left = initialLeft + dx + 'px'; el.style.top = initialTop + dy + 'px'; el.style.right = 'auto'; el.style.bottom = 'auto'; }
        };
        const dragEnd = (e) => {
            parentDoc.removeEventListener('mousemove', dragMove); parentDoc.removeEventListener('mouseup', dragEnd);
            parentDoc.removeEventListener('touchmove', dragMove); parentDoc.removeEventListener('touchend', dragEnd);
            el.style.transition = 'filter 0.3s ease, transform 0.3s ease'; isDragging = false; clearInterval(sparkleInterval);
        };
        el.addEventListener('mousedown', dragStart); el.addEventListener('touchstart', dragStart, {passive: false});
    }
    const stars = parentDoc.querySelectorAll('.interactive-star');
    stars.forEach(star => { if (!star.dataset.interactive) { makeInteractive(star); star.dataset.interactive = 'true'; } });
</script>
"""
components.html(drag_drop_js, height=0, width=0)

# --- KẾT NỐI GOOGLE SHEETS ---
SHEET_NAME = "Check-in DAB" 
@st.cache_resource
def init_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    return client

client = init_connection()
sheet = client.open(SHEET_NAME).sheet1
data = sheet.get_all_values()
stt_hien_tai = len(data) if len(data) > 0 else 1

# --- GIAO DIỆN CHÍNH ---
st.write("") 
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
                    # Tự động gán Phòng, Link Meet và Link Calendar dựa trên Số Thứ Tự
                    if stt_hien_tai % 2 != 0:
                        phong_phong_van = "Phòng 1"
                        link_duoc_giao = LINK_MEET_1
                        link_calendar_duoc_giao = LINK_CALENDAR_1
                    else:
                        phong_phong_van = "Phòng 2"
                        link_duoc_giao = LINK_MEET_2
                        link_calendar_duoc_giao = LINK_CALENDAR_2
                        
                    pair_index = (stt_hien_tai - 1) // 2 
                    total_minutes = pair_index * 7
                    gio, phut = 21 + (total_minutes // 60), total_minutes % 60
                    thoi_gian_duoc_giao = f"{gio:02d}:{phut:02d}"
                    
                    sheet.append_row([name, email, committee, thoi_gian_duoc_giao, phong_phong_van])
                    
                    # TẤM VÉ CẬP NHẬT THÊM NÚT CALENDAR TƯƠNG ỨNG TỪNG PHÒNG
                    ticket_html = (
                        f'<div style="margin: 30px auto 10px auto; max-width: 400px; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); border: 2px solid #ffffff; position: relative; overflow: hidden; transform: perspective(1000px) translateZ(0);">'
                        f'<div style="background: linear-gradient(135deg, #004E98, #002B5E); color: white; padding: 25px 20px; text-align: center; position: relative;">'
                        f'<div style="position: absolute; top: 10px; right: 15px; opacity: 0.15; font-size: 40px;">⭐</div>'
                        f'<h2 style="margin: 0; font-size: 22px; font-weight: 900; letter-spacing: 3px; text-transform: uppercase;">VÉ CHỜ PHỎNG VẤN</h2>'
                        f'<p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9; font-weight: 500; letter-spacing: 1px;">DAB CLUB</p></div>'
                        f'<div style="position: relative; height: 0; border-top: 4px dashed #e2e8f0; margin-top: 0px; background: white;">'
                        f'<div style="position: absolute; top: -15px; left: -15px; width: 30px; height: 30px; background-color: #F8FAFC; border-radius: 50%; box-shadow: inset -4px 0 6px rgba(0,0,0,0.08);"></div>'
                        f'<div style="position: absolute; top: -15px; right: -15px; width: 30px; height: 30px; background-color: #F8FAFC; border-radius: 50%; box-shadow: inset 4px 0 6px rgba(0,0,0,0.08);"></div></div>'
                        f'<div style="background: linear-gradient(180deg, #FAFAFA 0%, #FFFFFF 100%); padding: 25px 20px; text-align: center; border-bottom: 2px dashed #f1f5f9;">'
                        f'<p style="margin: 0; font-size: 14px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;">Số Thứ Tự</p>'
                        f'<h1 style="margin: 15px 0 5px 0; font-size: 100px; color: #FF6E2B; line-height: 1; font-weight: 900; text-shadow: 4px 4px 0px #FFE26E, 8px 8px 0px rgba(252, 94, 21, 0.15);">{stt_hien_tai}</h1>'
                        f'<h3 style="margin: 0; color: #004E98; font-size: 22px; font-weight: 800; text-transform: uppercase;">{name}</h3>'
                        f'<div style="display: inline-block; background: #FFF3EB; padding: 6px 16px; border-radius: 20px; border: 1px solid #FFD8C4; margin-top: 10px;">'
                        f'<p style="margin: 0; color: #64748b; font-size: 14px; font-weight: 600;">Tiểu ban: <span style="font-weight: 900; color: #FC5E15; font-size: 15px;">{committee}</span></p></div>'
                        f'<div style="background: #F8FAFC; padding: 15px; border-radius: 12px; margin-top: 20px; border: 1px dashed #cbd5e1; text-align: left;">'
                        f'<p style="margin: 0 0 8px 0; font-size: 15px; color: #004E98; font-weight: 600;">⏰ Thời gian dự kiến: <strong style="color: #FC5E15; font-size: 18px;">{thoi_gian_duoc_giao}</strong></p>'
                        f'<p style="margin: 0; font-size: 15px; color: #004E98; font-weight: 600;">🚪 Phòng: <strong style="color: #FC5E15; font-size: 16px;">{phong_phong_van}</strong></p>'
                        f'<a href="{link_duoc_giao}" target="_blank" style="display: block; margin-top: 12px; background: linear-gradient(to right, #0ea5e9, #0284c7); color: white; padding: 10px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: bold; text-align: center; box-shadow: 0 4px 6px rgba(2, 132, 199, 0.3);">👉 BẤM VÀO ĐÂY ĐỂ VÀO MEET</a>'
                        f'<a href="{link_calendar_duoc_giao}" target="_blank" style="display: block; margin-top: 8px; background: white; color: #004E98; padding: 9px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; text-align: center; border: 2px solid #0ea5e9;">📅 LƯU LỊCH PHỎNG VẤN</a>'
                        f'</div></div>'
                        f'<div style="padding: 15px 20px; text-align: center; background-color: white;">'
                        f'<div style="margin: 5px auto 15px auto; height: 35px; width: 80%; background: repeating-linear-gradient(to right, #004E98, #004E98 4px, transparent 4px, transparent 8px, #004E98 8px, #004E98 10px, transparent 10px, transparent 14px, #004E98 14px, #004E98 20px, transparent 20px, transparent 22px); opacity: 0.7; border-radius: 2px;"></div>'
                        f'<p style="margin: 0; font-size: 13px; color: #94a3b8; font-style: italic; font-weight: 500;">📸 Chụp màn hình để không quên giờ nhé!</p></div></div>'
                    )
                    st.markdown(ticket_html, unsafe_allow_html=True)
                    st.balloons() 
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin để tiếp tục.")
