import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. KHAI BÁO BIẾN VÀ CHIA TẬP MỜ
# ==========================================
dirt_amount = ctrl.Antecedent(np.arange(0, 101, 1), 'dirt_amount')
dirt_type = ctrl.Antecedent(np.arange(0, 101, 1), 'dirt_type')
cloth_sensitivity = ctrl.Antecedent(np.arange(0, 11, 1), 'cloth_sensitivity')
cloth_amount = ctrl.Antecedent(np.arange(0, 11, 1), 'cloth_amount')

wash_time = ctrl.Consequent(np.arange(0, 181, 1), 'wash_time') # Đã sửa thành 180 phút
spin_speed = ctrl.Consequent(np.arange(0, 1401, 1), 'spin_speed')
water_amount = ctrl.Consequent(np.arange(0, 101, 1), 'water_amount')
detergent = ctrl.Consequent(np.arange(0, 101, 1), 'detergent')
water_temp = ctrl.Consequent(np.arange(0, 81, 1), 'water_temp')

dirt_amount.automf(3, names=['small', 'medium', 'large'])
dirt_type.automf(3, names=['not_greasy', 'medium', 'greasy'])
cloth_sensitivity.automf(3, names=['less_sensitive', 'normal_sensitive', 'very_sensitive'])
cloth_amount.automf(3, names=['small', 'medium', 'large'])

water_amount.automf(3, names=['little', 'normal', 'many'])
detergent.automf(3, names=['little', 'normal', 'many'])
water_temp.automf(3, names=['low', 'normal', 'high'])
wash_time.automf(5, names=['very_short', 'short', 'medium', 'long', 'very_long'])
spin_speed.automf(5, names=['very_low', 'low', 'medium', 'high', 'very_high'])

# ==========================================
# 2. TẬP LUẬT MỜ
# ==========================================
rule1 = ctrl.Rule(dirt_amount['large'] & dirt_type['greasy'] & cloth_sensitivity['less_sensitive'] & cloth_amount['large'], (wash_time['very_long'], spin_speed['very_high'], water_amount['many'], detergent['many'], water_temp['high']))
rule2 = ctrl.Rule(dirt_amount['small'] & dirt_type['not_greasy'] & cloth_sensitivity['very_sensitive'] & cloth_amount['small'], (wash_time['very_short'], spin_speed['very_low'], water_amount['little'], detergent['little'], water_temp['low']))
rule3 = ctrl.Rule(dirt_amount['medium'] & dirt_type['medium'] & cloth_sensitivity['normal_sensitive'] & cloth_amount['medium'], (wash_time['medium'], spin_speed['medium'], water_amount['normal'], detergent['normal'], water_temp['normal']))
rule4 = ctrl.Rule(dirt_amount['large'] & dirt_type['medium'] & cloth_sensitivity['very_sensitive'], (wash_time['long'], spin_speed['low'], water_temp['high'], detergent['normal']))
rule5 = ctrl.Rule(dirt_amount['medium'] & dirt_type['not_greasy'] & cloth_sensitivity['normal_sensitive'] & cloth_amount['large'], (wash_time['long'], spin_speed['high'], water_amount['many'], detergent['normal'], water_temp['normal']))
rule6 = ctrl.Rule(cloth_amount['small'], (water_amount['little'], detergent['little']))
rule7 = ctrl.Rule(cloth_amount['large'], (water_amount['many'], detergent['many']))
rule8 = ctrl.Rule(dirt_type['greasy'], (water_temp['high'], detergent['many']))
rule9 = ctrl.Rule(cloth_sensitivity['very_sensitive'], (wash_time['short'], spin_speed['low']))
rule10 = ctrl.Rule(cloth_sensitivity['less_sensitive'] & dirt_amount['large'], (wash_time['long'], spin_speed['high']))
rule11 = ctrl.Rule(dirt_amount['small'], wash_time['short'])
rule12 = ctrl.Rule(dirt_amount['medium'], wash_time['medium'])
rule13 = ctrl.Rule(dirt_amount['large'], wash_time['long'])

washing_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13])
washing_sim = ctrl.ControlSystemSimulation(washing_ctrl)

# ==========================================
# 3. HÀM DÀNH CHO GIAO DIỆN WEB
# ==========================================
def predict_wash(dirt_amt, dirt_typ, cloth_sens, cloth_amt):
    """Hàm này nhận 4 thông số, giải mờ và trả về 5 kết quả"""
    washing_sim.input['dirt_amount'] = dirt_amt
    washing_sim.input['dirt_type'] = dirt_typ
    washing_sim.input['cloth_sensitivity'] = cloth_sens
    washing_sim.input['cloth_amount'] = cloth_amt
    washing_sim.compute()
    
    return {
        'wash_time': round(washing_sim.output['wash_time'], 1),
        'spin_speed': round(washing_sim.output['spin_speed'], 0),
        'water_amount': round(washing_sim.output['water_amount'], 1),
        'detergent': round(washing_sim.output['detergent'], 1),
        'water_temp': round(washing_sim.output['water_temp'], 1)
    }

# ==========================================
# 4. CHẠY TEST CSV & VẼ ĐỒ THỊ 2D
# ==========================================
if __name__ == "__main__":
    output_base_dir = "Output"
    output_result_dir = os.path.join(output_base_dir, "result")
    output_plot_dir = os.path.join(output_base_dir, "plot")

    os.makedirs(output_result_dir, exist_ok=True)
    os.makedirs(output_plot_dir, exist_ok=True)

    input_csv_path = os.path.join("Input", "test_cases.csv")
    output_csv_path = os.path.join(output_result_dir, "result.csv")

    print("--- QUY TRÌNH MÔ PHỎNG MÁY GIẶT BẮT ĐẦU ---")
    print(f"-> Đang đọc file Test Case từ: {input_csv_path}")

    try:
        df = pd.read_csv(input_csv_path)
        results = []
        for index, row in df.iterrows():
            res = predict_wash(row['Dirt_Amount'], row['Dirt_Type'], row['Sensitivity'], row['Cloth_Amount'])
            
            res_dict = {
                'ID': row['ID'],
                'Gịch bản': row['Ghi_chu'], 
                'Dirt (%)': row['Dirt_Amount'],
                'Greasy (%)': row['Dirt_Type'],
                'Sensitivity (0-10)': row['Sensitivity'],
                'Cloth (kg)': row['Cloth_Amount'],
                'Output - Time (phút)': res['wash_time'], 
                'Output - Spin (rpm)': res['spin_speed'], 
                'Output - Water (%)': res['water_amount'], 
                'Output - Detergent (%)': res['detergent'], 
                'Output - Temp (C)': res['water_temp']
            }
            results.append(res_dict)
            
            print(f"[{row['ID']}] Chạy thành công {row['Ghi_chu']}:")
            print(f"   -> Giặt: {res['wash_time']} phút | Vắt: {res['spin_speed']} RPM | Nước: {res['water_amount']}% | Xà phòng: {res['detergent']}% | Nhiệt: {res['water_temp']}°C")
            print("-" * 60)

        pd.DataFrame(results).to_csv(output_csv_path, index=False)
        print(f"\n-> Đã xuất file kết quả CSV thành công tại: {output_csv_path}")

    except FileNotFoundError:
        print(f"\n❌ Lỗi: Không tìm thấy file 'test_cases.csv' trong thư mục 'Input'.")
        exit()

    # TỰ ĐỘNG VẼ VÀ LƯU ẢNH TẬP MỜ 2D
    print("\n--- BẮT ĐẦU QUÁ TRÌNH TỰ ĐỘNG VẼ VÀ LƯU ẢNH TẬP MỜ (2D) ---")
    print("💡 LƯU Ý: Python sẽ vẽ và lưu 9 biểu đồ mà không bật cửa sổ lên làm phiền bạn.\n")

    variables_to_plot = [
        (dirt_amount, "Input - Độ bẩn", "input_dirt_amount.png"),
        (dirt_type, "Input - Mức dầu mỡ", "input_dirt_type.png"),
        (cloth_sensitivity, "Input - Độ nhạy vải", "input_cloth_sensitivity.png"),
        (cloth_amount, "Input - Khối lượng đồ", "input_cloth_amount.png"),
        (wash_time, "Output - Thời gian giặt", "output_wash_time.png"),
        (spin_speed, "Output - Tốc độ vắt", "output_spin_speed.png"),
        (water_amount, "Output - Lượng nước", "output_water_amount.png"),
        (detergent, "Output - Xà phòng", "output_detergent.png"),
        (water_temp, "Output - Nhiệt độ nước", "output_water_temp.png")
    ]


    for var, title, filename in variables_to_plot:
        print(f"-> Đang vẽ và lưu biểu đồ: {filename}")
        
        var.view(sim=washing_sim)
        
        fig = plt.gcf()
        
        plt.title(title, fontsize=14, fontweight='bold')
        
        #plt.show() (Dùng để dừng lại cho xem rồi mới lưu, có thể dùng hoặc không)
        
        save_path = os.path.join(output_plot_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close(fig)

    print(f"\n--- HOÀN TẤT! Hãy mở thư mục '{output_plot_dir}' để xem 9 biểu đồ .png đã được tạo. ---")