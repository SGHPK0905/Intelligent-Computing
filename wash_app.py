import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from fuzzy_washing import predict_wash, washing_sim, wash_time, spin_speed, water_temp, water_amount, detergent

# ─────────────────────────────────────────
# CẤU HÌNH TRANG & CSS
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Máy Giặt Thông Minh — Logic Mờ",
    page_icon="🧼",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
.stProgress > div > div > div { border-radius: 8px; }
.advice { background:#e8f5e9; border-left:4px solid #2e7d32;
          border-radius:0 8px 8px 0; padding:12px 16px; margin:8px 0; }
.advice p { margin:4px 0; font-size:14px; color:#1b5e20; }
.cycle-badge { display:inline-block; background:#e1f5ee; color:#085041;
               border-radius:20px; padding:4px 14px;
               font-size:13px; font-weight:600; margin-left:8px; }
.spin-bar { display:flex; gap:5px; margin:8px 0; }
.spin-seg { flex:1; height:8px; border-radius:4px; background:#e0e0e0; }
.spin-on  { background:#1D9E75 !important; }
.spin-half{ background:#9FE1CB !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# DỮ LIỆU KỊCH BẢN PRESET
# ─────────────────────────────────────────
PRESETS = {
    "👕  Đồ thường ngày":     {"desc":"Cotton, thun mặc nhà",          "dirt":50,  "greasy":20, "fabric":"Vải thường (Cotton, Thun)", "weight":5.0, "cycle":"Mixed Fabric"},
    "👗  Đồ lụa / nhạy cảm": {"desc":"Voan, ren, lụa mỏng manh",      "dirt":20,  "greasy":10, "fabric":"Vải mỏng (Lụa, Voan)",     "weight":1.5, "cycle":"Delicates"},
    "🧸  Đồ trẻ em":          {"desc":"Mềm, cần diệt khuẩn nhẹ",       "dirt":85,  "greasy":30, "fabric":"Vải mỏng (Lụa, Voan)",     "weight":3.5, "cycle":"Baby Care"},
    "🏋️  Đồ bảo hộ / jeans": {"desc":"Cực bẩn, dày dặn, nhiều dầu",  "dirt":95,  "greasy":90, "fabric":"Vải dày (Jeans, Kaki)",    "weight":8.5, "cycle":"Heavy Duty"},
    "🛏️  Chăn mền lớn":       {"desc":"Tải nặng, cần nhiều nước",       "dirt":40,  "greasy":15, "fabric":"Vải thường (Cotton, Thun)", "weight":9.0, "cycle":"Duvet / Bedding"},
    "⚙️  Tùy chỉnh thủ công": {"desc":"Tự kéo các thanh trượt",         "dirt":50,  "greasy":50, "fabric":"Vải thường (Cotton, Thun)", "weight":5.0, "cycle":"Custom"},
}

FABRIC_TO_SENSITIVITY = {
    "Vải dày (Jeans, Kaki)":     1,
    "Vải thường (Cotton, Thun)": 5,
    "Vải mỏng (Lụa, Voan)":     9,
}


# ─────────────────────────────────────────
# HÀM TIỆN ÍCH
# ─────────────────────────────────────────
def label_spin(rpm):
    if rpm < 450:  return "Rất nhẹ — bảo vệ lụa"
    if rpm < 700:  return "Nhẹ"
    if rpm < 950:  return "Trung bình"
    if rpm < 1150: return "Cao"
    return "Rất cao — vắt kiệt"

def spin_level(rpm):
    if rpm < 400:  return 1
    if rpm < 650:  return 2
    if rpm < 900:  return 3
    if rpm < 1150: return 4
    return 5

def label_temp(t):
    if t < 35: return "Nước lạnh — bảo vệ màu vải"
    if t < 55: return "Ấm vừa — tối ưu xà phòng"
    return "Nước nóng — diệt khuẩn"

def label_dirt(d):
    if d < 35: return "Ít bẩn"
    if d < 65: return "Bẩn vừa"
    return "Rất bẩn"

def label_greasy(g):
    if g < 35: return "Chủ yếu bụi, mồ hôi"
    if g < 65: return "Hỗn hợp"
    return "Nhiều dầu mỡ"

def estimate_timeline(total_min):
    soak  = round(total_min * 0.18)
    wash_t= round(total_min * 0.44)
    rinse = round(total_min * 0.22)
    spin_t= round(total_min * 0.16)
    return soak, wash_t, rinse, spin_t

def generate_advice(res, fabric):
    tips = []
    if res['water_temp'] >= 55:
        tips.append("🌡️ Nước nóng giúp diệt khuẩn và phá vỡ liên kết dầu mỡ hiệu quả.")
    elif res['water_temp'] < 35:
        tips.append("❄️ Nước lạnh bảo vệ màu vải và sợi vải mỏng manh.")
    else:
        tips.append("♨️ Nhiệt độ 40°C là mức tối ưu để xà phòng hoạt động tốt nhất.")
    if res['spin_speed'] < 500:
        tips.append("🌀 Tốc độ vắt rất thấp — bảo vệ tối đa cho vải lụa, voan.")
    elif res['spin_speed'] > 1100:
        tips.append("💨 Tốc độ vắt cao giúp vắt kiệt nước, quần áo mau khô hơn.")
    if res['detergent'] > 65:
        tips.append("🫧 Lượng xà phòng cao — đảm bảo làm sạch sâu vết bẩn khó.")
    elif res['detergent'] < 35:
        tips.append("🫧 Lượng xà phòng ít — tiết kiệm, phù hợp đồ ít bẩn hoặc vải nhạy cảm.")
    if res['water_amount'] > 65:
        tips.append("💧 Nhiều nước giúp ngâm kỹ và xả sạch hoàn toàn.")
    if "Lụa" in fabric or "Voan" in fabric:
        tips.append("👗 Gợi ý: Thêm nước xả vải để giữ độ mềm mại cho lụa.")
    return tips


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if "preset" not in st.session_state:
    st.session_state.preset = "👕  Đồ thường ngày"

if "manual_dirt" not in st.session_state:
    st.session_state.manual_dirt = 50
    st.session_state.manual_greasy = 50
    st.session_state.manual_weight = 5.0
    st.session_state.manual_fabric = "Vải thường (Cotton, Thun)"
# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("## 🧼 Máy Giặt Thông Minh — Hệ Thống Logic Mờ")
st.caption("Hệ thống tự động xác định chu trình giặt tối ưu dựa trên đặc điểm đồ giặt.")
st.markdown("---")


# ─────────────────────────────────────────
# LAYOUT CHÍNH
# ─────────────────────────────────────────
col_input, col_output = st.columns([1, 1.7], gap="large")


# ══════════════════════════════════════
# CỘT TRÁI — ĐẦU VÀO
# ══════════════════════════════════════
with col_input:
    st.markdown("### 📥 Thông số đầu vào")
    st.markdown("**Chọn nhanh theo kịch bản:**")

    cols_preset = st.columns(2)
    for idx, key in enumerate(PRESETS.keys()):
        with cols_preset[idx % 2]:
            p = PRESETS[key]
            is_active = (st.session_state.preset == key)
            if st.button(
                f"{key}\n_{p['desc']}_",
                key=f"preset_{idx}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.preset = key
                st.rerun()

    st.markdown("---")
    
    manual  = (st.session_state.preset == "⚙️  Tùy chỉnh thủ công")
    st.markdown("**Điều chỉnh chi tiết:**")

    fabric_options   = list(FABRIC_TO_SENSITIVITY.keys())

    if manual:
        selected_fabric = st.selectbox("Loại vải", options=fabric_options, key="manual_fabric")
        dirt_amount = st.slider(f"Độ bẩn — *{label_dirt(st.session_state.manual_dirt)}*", 0, 100, format="%d%%", key="manual_dirt")
        dirt_type = st.slider(f"Mức dầu mỡ — *{label_greasy(st.session_state.manual_greasy)}*", 0, 100, format="%d%%", key="manual_greasy")
        cloth_amount = st.slider("Khối lượng quần áo (kg)", 0.0, 10.0, step=0.5, key="manual_weight")
        cloth_sensitivity = FABRIC_TO_SENSITIVITY[selected_fabric]
    else:
        current = PRESETS[st.session_state.preset]
        selected_fabric = st.selectbox("Loại vải", options=fabric_options, index=fabric_options.index(current["fabric"]), disabled=True, key="auto_fab")
        dirt_amount = st.slider(f"Độ bẩn — *{label_dirt(current['dirt'])}*", 0, 100, value=current["dirt"], format="%d%%", disabled=True, key="auto_dirt")
        dirt_type = st.slider(f"Mức dầu mỡ — *{label_greasy(current['greasy'])}*", 0, 100, value=current["greasy"], format="%d%%", disabled=True, key="auto_greasy")
        cloth_amount = st.slider("Khối lượng quần áo (kg)", 0.0, 10.0, value=current["weight"], step=0.5, disabled=True, key="auto_weight")
        cloth_sensitivity = FABRIC_TO_SENSITIVITY[current["fabric"]]

# ══════════════════════════════════════
# CỘT PHẢI — KẾT QUẢ
# ══════════════════════════════════════
with col_output:
    try:
        res        = predict_wash(dirt_amount, dirt_type, cloth_sensitivity, cloth_amount)
        cycle_name = PRESETS[st.session_state.preset]["cycle"]

        st.markdown(
            f"### 📤 Kết quả đề xuất "
            f"<span class='cycle-badge'>🔄 {cycle_name}</span>",
            unsafe_allow_html=True
        )

        # Metrics row
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("⏱️ Thời gian",   f"{res['wash_time']} phút")
        m2.metric("🌪️ Tốc độ vắt", f"{int(res['spin_speed'])} RPM")
        m3.metric("💧 Lượng nước",  f"{res['water_amount']} %")
        m4.metric("🫧 Xà phòng",    f"{res['detergent']} %")
        m5.metric("🌡️ Nhiệt độ",   f"{res['water_temp']} °C")
        st.markdown("---")

        tab_main, tab_compare, tab_fuzzy, tab_3d = st.tabs([
            "📊 Phân tích chi tiết",
            "🔄 So sánh 2 kịch bản",
            "📈 Đồ thị tập mờ",
            "🧊 Mặt cong 3D"
        ])

        # ── TAB 1: PHÂN TÍCH ─────────────────────
        with tab_main:
            # Timeline
            st.markdown("**🕐 Ước tính tiến trình chu trình**")
            soak, wash_t, rinse, spin_t = estimate_timeline(res['wash_time'])
            tl1, tl2, tl3, tl4 = st.columns(4)
            tl1.metric("🫧 Ngâm",  f"{soak} phút")
            tl2.metric("🔄 Giặt",  f"{wash_t} phút")
            tl3.metric("💦 Xả",    f"{rinse} phút")
            tl4.metric("💨 Vắt",   f"{spin_t} phút")

            total = res['wash_time']
            for lbl, dur in [("Ngâm", soak), ("Giặt", wash_t), ("Xả", rinse), ("Vắt", spin_t)]:
                st.markdown(f"<small style='color:gray'>{lbl} — {dur} phút</small>",
                            unsafe_allow_html=True)
                st.progress(int(dur / total * 100))

            st.markdown("---")

            # Spin visual
            st.markdown("**🌪️ Mức tốc độ vắt**")
            level = spin_level(res['spin_speed'])
            segs  = "".join(
                f'<div class="spin-seg {"spin-on" if i <= level else "spin-half" if i == level + 1 and level < 5 else ""}"></div>'
                for i in range(1, 6)
            )
            st.markdown(f"""
            <div class="spin-bar">{segs}</div>
            <div style="display:flex;justify-content:space-between;font-size:11px;color:gray;margin-bottom:6px">
                <span>Rất nhẹ (Lụa)</span><span>Trung bình</span><span>Tối đa (Jeans)</span>
            </div>
            <p style="font-size:13px;color:#0F6E56;font-weight:500">
                {label_spin(res['spin_speed'])} — {int(res['spin_speed'])} RPM
            </p>""", unsafe_allow_html=True)

            st.markdown("---")

            # Nhiệt độ visual
            st.markdown(f"**🌡️ Nhiệt độ nước** — *{label_temp(res['water_temp'])}*")
            st.progress(int(res['water_temp']))
            tc1, tc2, tc3 = st.columns(3)
            tc1.markdown("<small>❄️ Lạnh (20°C)</small>", unsafe_allow_html=True)
            tc2.markdown("<small style='text-align:center;display:block'>♨️ Ấm (40°C)</small>", unsafe_allow_html=True)
            tc3.markdown("<small style='text-align:right;display:block'>🔥 Nóng (95°C)</small>", unsafe_allow_html=True)

            st.markdown("---")

            # Advice
            st.markdown("**💡 Gợi ý từ hệ thống**")
            tips     = generate_advice(res, selected_fabric)
            tips_html= "".join(f"<p>• {t}</p>" for t in tips)
            st.markdown(f'<div class="advice">{tips_html}</div>', unsafe_allow_html=True)

        # ── TAB 2: SO SÁNH ───────────────────────
        with tab_compare:
            st.markdown("**So sánh hai kịch bản — hệ thống mờ nội suy khác nhau thế nào?**")
            st.caption("Điểm mạnh của Fuzzy Logic: thay đổi tham số → output thay đổi mượt mà, không nhảy cấp.")

            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**Kịch bản A**")
                ka = st.selectbox("Kịch bản A", list(PRESETS.keys()), index=0, key="ka")
            with cc2:
                st.markdown("**Kịch bản B**")
                kb = st.selectbox("Kịch bản B", list(PRESETS.keys()), index=3, key="kb")

            if st.button("⚡ So sánh ngay", type="primary", use_container_width=True):
                pa = PRESETS[ka].copy()
                pb = PRESETS[kb].copy()

                if ka == "⚙️  Tùy chỉnh thủ công":
                    pa["dirt"] = dirt_amount
                    pa["greasy"] = dirt_type
                    pa["weight"] = cloth_amount
                    pa["fabric"] = selected_fabric
                    
                if kb == "⚙️  Tùy chỉnh thủ công":
                    pb["dirt"] = dirt_amount
                    pb["greasy"] = dirt_type
                    pb["weight"] = cloth_amount
                    pb["fabric"] = selected_fabric

                sa = FABRIC_TO_SENSITIVITY[pa["fabric"]]
                sb = FABRIC_TO_SENSITIVITY[pb["fabric"]]
                
                ra = predict_wash(pa["dirt"], pa["greasy"], sa, pa["weight"])
                rb = predict_wash(pb["dirt"], pb["greasy"], sb, pb["weight"])

                st.markdown("---")
                h1, h2 = st.columns(2)
                h1.markdown(f"#### {ka}")
                h1.caption(pa["desc"])
                h2.markdown(f"#### {kb}")
                h2.caption(pb["desc"])

                MAX_VALS = {"wash_time":180, "spin_speed":1400,
                            "water_amount":100, "detergent":100, "water_temp":100}
                UNITS    = {"wash_time":"phút","spin_speed":"RPM",
                            "water_amount":"%","detergent":"%","water_temp":"°C"}
                LABELS   = {"wash_time":"⏱️ Thời gian","spin_speed":"🌪️ Tốc độ vắt",
                            "water_amount":"💧 Lượng nước","detergent":"🫧 Xà phòng","water_temp":"🌡️ Nhiệt độ"}

                for key in ["wash_time","spin_speed","water_amount","detergent","water_temp"]:
                    va, vb = ra[key], rb[key]
                    unit   = UNITS[key]
                    diff   = round(vb - va, 1)
                    delta_str = f"+{diff} {unit}" if diff > 0 else (f"{diff} {unit}" if diff != 0 else "Bằng nhau")
                    pct_a  = int(va / MAX_VALS[key] * 100)
                    pct_b  = int(vb / MAX_VALS[key] * 100)

                    st.markdown(f"**{LABELS[key]}**")
                    ca, cbar, cbr = st.columns([1, 2, 1])
                    ca.metric(f"A — {pa['cycle']}", f"{va} {unit}")
                    with cbar:
                        st.markdown(f"""
                        <div style="margin:8px 0 2px">
                          <div style="display:flex;gap:4px;align-items:center;margin-bottom:3px">
                            <span style="font-size:11px;color:#085041;width:14px">A</span>
                            <div style="flex:1;background:#e0e0e0;border-radius:4px;height:8px">
                              <div style="width:{pct_a}%;background:#1D9E75;height:8px;border-radius:4px"></div>
                            </div>
                          </div>
                          <div style="display:flex;gap:4px;align-items:center">
                            <span style="font-size:11px;color:#854F0B;width:14px">B</span>
                            <div style="flex:1;background:#e0e0e0;border-radius:4px;height:8px">
                              <div style="width:{pct_b}%;background:#EF9F27;height:8px;border-radius:4px"></div>
                            </div>
                          </div>
                        </div>""", unsafe_allow_html=True)
                    cbr.metric(f"B — {pb['cycle']}", f"{vb} {unit}", delta=delta_str)
                    st.markdown("<hr style='margin:8px 0;opacity:0.2'>", unsafe_allow_html=True)

                st.markdown("**🔍 Nhận xét của hệ thống:**")
                remarks = []
                if abs(ra['spin_speed'] - rb['spin_speed']) > 300:
                    faster = ka if ra['spin_speed'] > rb['spin_speed'] else kb
                    remarks.append(f"Tốc độ vắt chênh lệch lớn — kịch bản **{faster}** đòi hỏi vắt mạnh hơn đáng kể.")
                if abs(ra['water_temp'] - rb['water_temp']) > 15:
                    hotter = ka if ra['water_temp'] > rb['water_temp'] else kb
                    remarks.append(f"Nhiệt độ chênh rõ — hệ thống ưu tiên diệt khuẩn cho kịch bản **{hotter}**.")
                if abs(ra['wash_time'] - rb['wash_time']) > 30:
                    longer = ka if ra['wash_time'] > rb['wash_time'] else kb
                    remarks.append(f"Thời gian kịch bản **{longer}** dài hơn — đồ bẩn cần ngâm kỹ hơn.")
                if not remarks:
                    remarks.append("Hai kịch bản có đặc điểm tương đồng, hệ thống mờ đề xuất thông số khá gần nhau.")
                for r in remarks:
                    st.info(r)
                    
                predict_wash(dirt_amount, dirt_type, cloth_sensitivity, cloth_amount)

        # ── TAB 3: ĐỒ THỊ TẬP MỜ ────────────────
        with tab_fuzzy:
            st.markdown("**Trực quan hóa mức độ kích hoạt các tập mờ đầu ra**")
            st.caption("Đường đứt đoạn dọc = giá trị thực tế. Vùng tô màu = mức độ thuộc (membership).")

            f1, f2, f3 = st.columns(3)
            with f1:
                st.markdown("⏱️ **Thời gian giặt**")
                wash_time.view(sim=washing_sim)
                st.pyplot(plt.gcf()); plt.close()
            with f2:
                st.markdown("🌪️ **Tốc độ vắt**")
                spin_speed.view(sim=washing_sim)
                st.pyplot(plt.gcf()); plt.close()
            with f3:
                st.markdown("🌡️ **Nhiệt độ nước**")
                water_temp.view(sim=washing_sim)
                st.pyplot(plt.gcf()); plt.close()

            f4, f5 = st.columns(2)
            with f4:
                st.markdown("💧 **Lượng nước**")
                water_amount.view(sim=washing_sim)
                st.pyplot(plt.gcf()); plt.close()
            with f5:
                st.markdown("🫧 **Xà phòng**")
                detergent.view(sim=washing_sim)
                st.pyplot(plt.gcf()); plt.close()

        # ── TAB 4: MẶT CONG 3D ───────────────────
        with tab_3d:
            st.markdown("### Không gian điều khiển 3D")
            st.caption(
                "Mặt cong thể hiện Tốc độ vắt thay đổi theo Độ nhạy vải (trục X) "
                "và Mức dầu mỡ (trục Y). Các biến còn lại đóng băng theo kịch bản đang chọn."
            )

            if st.button("🚀 Render mặt cong 3D", type="primary"):
                with st.spinner("Đang tính toán 2500 điểm dữ liệu..."):
                    x_vals = np.linspace(0, 10,  50)
                    y_vals = np.linspace(0, 100, 50)
                    z_vals = np.zeros((50, 50))

                    for i in range(50):
                        for j in range(50):
                            washing_sim.input['cloth_sensitivity'] = x_vals[i]
                            washing_sim.input['dirt_type']         = y_vals[j]
                            washing_sim.input['dirt_amount']       = dirt_amount
                            washing_sim.input['cloth_amount']      = cloth_amount
                            try:
                                washing_sim.compute()
                                z_vals[j, i] = washing_sim.output['spin_speed']
                            except Exception:
                                z_vals[j, i] = 0

                    fig_3d = go.Figure(data=[go.Surface(
                        z=z_vals, x=x_vals, y=y_vals,
                        colorscale='Viridis',
                        colorbar=dict(title="RPM")
                    )])
                    # Đánh dấu điểm hiện tại
                    fig_3d.add_trace(go.Scatter3d(
                        x=[cloth_sensitivity], y=[dirt_type], z=[res['spin_speed']],
                        mode='markers',
                        marker=dict(size=8, color='red', symbol='diamond'),
                        name=f"Điểm hiện tại ({int(res['spin_speed'])} RPM)"
                    ))
                    fig_3d.update_layout(
                        title=f"Mặt cong Tốc Độ Vắt — Kịch bản: {cycle_name}",
                        scene=dict(
                            xaxis_title="Nhạy cảm vải (0=Jeans → 10=Lụa)",
                            yaxis_title="Mức dầu mỡ (0-100%)",
                            zaxis_title="Tốc độ vắt (RPM)"
                        ),
                        margin=dict(l=0, r=0, b=0, t=50),
                        height=550
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)
                    st.caption("🔴 Điểm đỏ = vị trí thông số hiện tại trên mặt cong.")

    except Exception as e:
        st.error(f"⚠️ Hệ thống gặp lỗi nội suy: `{e}`")
        st.info("Thông số đầu vào có thể rơi vào vùng chưa có luật mờ bao phủ (Fuzzy Holes). "
                "Hãy thử chọn một kịch bản preset có sẵn.")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.caption(
    "🔬 Mô phỏng máy giặt LG AI DD Inverter 10kg (FV1410S3B) bằng Fuzzy Logic. "
    "Môn Tính Toán Thông Minh — Xây dựng với `scikit-fuzzy` + `Streamlit`."
)