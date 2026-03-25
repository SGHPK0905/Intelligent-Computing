import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from fuzzy_washing import washing_sim
import os

# ==========================================
# KHAI BÁO CÁC KỊCH BẢN ĐÓNG BĂNG
# ==========================================
danh_sach_kich_ban = [
    {
        "ten":         "TH1: Đồ cực bẩn (90%) và Khối lượng lớn (8kg)",
        "dirt_amount": 90,
        "cloth_amount": 8,
        "filename":    "3d_spin_heavy_duty.png"
    },
    {
        "ten":         "TH2: Đồ ít bẩn (20%) và Khối lượng nhỏ (2kg)",
        "dirt_amount": 20,
        "cloth_amount": 2,
        "filename":    "3d_spin_delicates.png"
    }
]

output_plot_dir = os.path.join("Output", "plot")
os.makedirs(output_plot_dir, exist_ok=True)

print("--- QUY TRÌNH TỰ ĐỘNG VẼ VÀ LƯU MẶT CONG 3D (TỐC ĐỘ VẮT) ---")
print("💡 LƯU Ý: Python sẽ tính toán, lưu ảnh, rồi mới hiện popup.\n")

# Trục X: Độ nhạy vải (0 -> 10)
# Trục Y: Mức dầu mỡ  (0 -> 100)
x, y = np.meshgrid(np.linspace(0, 10, 50), np.linspace(0, 100, 50))

for kb in danh_sach_kich_ban:
    print(f"-> Đang tính toán ma trận 2500 điểm cho: {kb['filename']}...")
    z = np.zeros_like(x)

    for i in range(50):
        for j in range(50):
            washing_sim.input['cloth_sensitivity'] = x[i, j]
            washing_sim.input['dirt_type']         = y[i, j]
            washing_sim.input['dirt_amount']       = kb['dirt_amount']
            washing_sim.input['cloth_amount']      = kb['cloth_amount']

            try:
                washing_sim.compute()
                z[i, j] = washing_sim.output['spin_speed']
            except Exception:
                z[i, j] = np.nan

    # Cấu hình vẽ 3D
    fig = plt.figure(figsize=(12, 8))
    ax  = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x, y, z, cmap='viridis', linewidth=0, antialiased=True, alpha=0.9)
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.2)
    cbar.set_label('Đơn vị: RPM (vòng/phút)', fontweight='bold', rotation=270, labelpad=25)
    cbar.ax.tick_params(labelsize=10)   

    ax.set_xlabel('Độ nhạy vải (0=Dày, 10=Lụa)', fontweight='bold', labelpad=15)
    ax.set_ylabel('Mức dầu mỡ (%)',               fontweight='bold', labelpad=15)
    ax.set_zlabel('Tốc độ vắt (vòng/phút)',        fontweight='bold', labelpad=15)
    plt.title(f"Mặt Cong 3D: TỐC ĐỘ VẮT\n{kb['ten']}", fontsize=15, fontweight='bold', pad=30)

    save_path = os.path.join(output_plot_dir, kb['filename'])
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    print(f"   -> Đã lưu ảnh tại: {save_path}")

    print(f"   -> Đang hiện popup cho: {kb['ten']}. Hãy xoay để xem rồi tắt để tiếp tục...")
    plt.show()

    plt.close()

print(f"\n--- HOÀN TẤT! Hãy mở thư mục '{output_plot_dir}' để xem các ảnh .png đã tạo. ---")