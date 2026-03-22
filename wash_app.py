import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from fuzzy_washing import predict_wash, washing_sim, wash_time, spin_speed, water_temp

st.set_page_config(page_title="Mô Phỏng Máy Giặt Mờ", page_icon="🧼", layout="wide")
st.title("🧼 Bảng Điều Khiển Máy Giặt AI - Logic Mờ")
st.markdown("Kéo thanh trượt để hệ thống nội suy thời gian thực.")
st.markdown("---")

col1, col2 = st.columns([1, 1.8])

with col1:
    st.header("📥 Cảm Biến Đầu Vào")
    dirt_amount = st.slider("Độ bẩn của quần áo (%)", 0, 100, 50, format="%d%%")
    dirt_type = st.slider("Mức độ dầu mỡ (%)", 0, 100, 20, format="%d%%")
    cloth_sensitivity = st.slider("Độ nhạy cảm vải (0: Dày -> 10: Lụa mỏng)", 0, 10, 5)
    cloth_amount = st.slider("Khối lượng quần áo (kg)", 0.0, 10.0, 5.0, step=0.5)

try:
    ket_qua = predict_wash(dirt_amount, dirt_type, cloth_sensitivity, cloth_amount)
    
    with col2:
        st.header("📤 Thông Số Đề Xuất")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric(label="⏱️ Thời gian", value=f"{ket_qua['wash_time']} p")
        m2.metric(label="🌪️ Tốc độ vắt", value=f"{ket_qua['spin_speed']} RPM")
        m3.metric(label="💧 Nước", value=f"{ket_qua['water_amount']} %")
        m4.metric(label="🫧 Xà phòng", value=f"{ket_qua['detergent']} %")
        m5.metric(label="🌡️ Nhiệt độ", value=f"{ket_qua['water_temp']} °C")
        
        tab1, tab2, tab3, tab4 = st.tabs(["⏱️ Thời gian", "🌪️ Tốc độ vắt", "🌡️ Nhiệt độ", "🧊 Mặt Cong 3D (Tương tác)"])
        
        with tab1:
            wash_time.view(sim=washing_sim)
            st.pyplot(plt.gcf())
            plt.close()
            
        with tab2:
            spin_speed.view(sim=washing_sim)
            st.pyplot(plt.gcf())
            plt.close()
            
        with tab3:
            water_temp.view(sim=washing_sim)
            st.pyplot(plt.gcf())
            plt.close()
            
        with tab4:
            st.markdown("### Mô phỏng Không gian điều khiển 3D")
            st.caption("Góc nhìn: Tốc độ vắt phụ thuộc vào Độ nhạy vải và Mức dầu mỡ (Các biến khác đóng băng theo Slider bên trái).")
            
            if st.button("🚀 Nhấn vào đây để render biểu đồ 3D", type="primary"):
                with st.spinner('Đang tính toán ma trận 2500 điểm dữ liệu...'):
                    x_vals = np.linspace(0, 10, 50) 
                    y_vals = np.linspace(0, 100, 50) 
                    z_vals = np.zeros((50, 50))
                    
                    for i in range(50):
                        for j in range(50):
                            washing_sim.input['cloth_sensitivity'] = x_vals[i]
                            washing_sim.input['dirt_type'] = y_vals[j]
                            washing_sim.input['dirt_amount'] = dirt_amount
                            washing_sim.input['cloth_amount'] = cloth_amount
                            try:
                                washing_sim.compute()
                                z_vals[j, i] = washing_sim.output['spin_speed']
                            except:
                                z_vals[j, i] = 0
                    
                    fig_3d = go.Figure(data=[go.Surface(z=z_vals, x=x_vals, y=y_vals, colorscale='Viridis')])
                    fig_3d.update_layout(
                        title='Mặt cong: Tốc Độ Vắt (Spin Speed)',
                        scene=dict(
                            xaxis_title='Nhạy cảm vải (0-10)',
                            yaxis_title='Dầu mỡ (0-100%)',
                            zaxis_title='Tốc độ vắt (RPM)'
                        ),
                        margin=dict(l=0, r=0, b=0, t=40)
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)

except Exception as e:
    st.error("Hệ thống gặp lỗi nội suy do thông số rơi vào Điểm mù (Fuzzy Holes). Vui lòng kiểm tra lại Tập Luật!")