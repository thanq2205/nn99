import streamlit as st

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="School Escape 3D - Pro Edition",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS để tối ưu hóa giao diện Streamlit ---
st.markdown("""
    <style>
    /* Ẩn Header và Footer mặc định */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mở rộng không gian hiển thị */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Style cho tiêu đề bên ngoài game */
    .stApp h1 {
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align
