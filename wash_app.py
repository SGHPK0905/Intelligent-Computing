import streamlit as st
from fuzzy_washing import predict_wash

st.set_page_config(page_title="Mô Phỏng Máy Giặt Mờ", layout="wide")
st.title("🧼 Bảng Điều Khiển Máy Giặt Bằng Logic Mờ (Fuzzy Logic)")
st.markdown("Kéo các thanh trượt bên dưới để hệ thống tự động tính toán thông số giặt theo thời gian thực.")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Cảm Biến Đầu Vào (Inputs)")
    st.markdown("---")
    dirt_amount = st.slider("Độ bẩn của quần áo (%)", 0, 100, 50)
    dirt_type = st.slider("Mức độ dầu mỡ (%)", 0, 100, 20)
    cloth_sensitivity = st.slider("Độ nhạy cảm vải (0: Rất Dày -> 10: Lụa mỏng)", 0, 10, 5)
    cloth_amount = st.slider("Khối lượng quần áo (kg)", 0, 10, 5)

# Xử lý tính toán
try:
    ket_qua = predict_wash(dirt_amount, dirt_type, cloth_sensitivity, cloth_amount)
    
    with col2:
        st.header("📤 Thông Số Đề Xuất (Outputs)")
        st.markdown("---")
        st.metric(label="⏱️ Thời gian giặt (phút)", value=f"{ket_qua['wash_time']} phút")
        st.metric(label="🌪️ Tốc độ vắt (vòng/phút)", value=f"{ket_qua['spin_speed']} RPM")
        st.metric(label="💧 Lượng nước cấp (%)", value=f"{ket_qua['water_amount']} %")
        st.metric(label="🫧 Lượng xà phòng (%)", value=f"{ket_qua['detergent']} %")
        st.metric(label="🌡️ Nhiệt độ nước (°C)", value=f"{ket_qua['water_temp']} °C")
        
        st.success("Hệ thống đã giải mờ thành công dựa trên 13 Luật (Rules)!")
except Exception as e:
    st.error("Hệ thống gặp lỗi nội suy do thông số chưa được bao phủ bởi Luật mờ.")