import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from fuzzy_washing import washing_sim 

# ==========================================
danh_sach_kich_ban = [
    {"ten": "TH1: Đồ cực bẩn (90%) và Khối lượng lớn (8kg)", "dirt_amount": 90, "cloth_amount": 8},
    {"ten": "TH2: Đồ ít bẩn (20%) và Khối lượng nhỏ (2kg)", "dirt_amount": 20, "cloth_amount": 2}
]

print("BẮT ĐẦU VẼ 3D: QUAN HỆ GIỮA LOẠI VẢI, DẦU MỠ VÀ TỐC ĐỘ VẮT...\n")

# Trục X: Loại vải (0 -> 10)
# Trục Y: Dầu mỡ (0 -> 100)
x, y = np.meshgrid(np.linspace(0, 10, 50), np.linspace(0, 100, 50))

for kb in danh_sach_kich_ban:
    print(f"Đang tính toán: {kb['ten']}...")
    z = np.zeros_like(x)
    
    for i in range(50):
        for j in range(50):
            washing_sim.input['cloth_sensitivity'] = x[i, j]
            washing_sim.input['dirt_type'] = y[i, j]
            
            washing_sim.input['dirt_amount'] = kb['dirt_amount']
            washing_sim.input['cloth_amount'] = kb['cloth_amount']
            
            try:
                washing_sim.compute()
                z[i, j] = washing_sim.output['spin_speed']
            except Exception:
                z[i, j] = np.nan 

    fig = plt.figure(figsize=(11, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(x, y, z, cmap='viridis', linewidth=0, antialiased=True)
    
    ax.set_xlabel('Độ nhạy vải (0=Dày, 10=Lụa)', fontweight='bold', labelpad=10)
    ax.set_ylabel('Mức dầu mỡ (%)', fontweight='bold', labelpad=10)
    ax.set_zlabel('Tốc độ vắt (vòng/phút)', fontweight='bold', labelpad=10)
    plt.title(f"Mặt Cong 3D: TỐC ĐỘ VẮT\n{kb['ten']}", fontsize=13, fontweight='bold')
    
    plt.show() 

print("\nĐã xem xong!")