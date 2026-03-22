import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. KHAI BÁO BIẾN VÀ CHIA TẬP MỜ
# ==========================================
dirt_amount = ctrl.Antecedent(np.arange(0, 101, 1), 'dirt_amount')
dirt_type = ctrl.Antecedent(np.arange(0, 101, 1), 'dirt_type')
cloth_sensitivity = ctrl.Antecedent(np.arange(0, 11, 1), 'cloth_sensitivity')
cloth_amount = ctrl.Antecedent(np.arange(0, 11, 1), 'cloth_amount')

wash_time = ctrl.Consequent(np.arange(0, 181, 1), 'wash_time')
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
# 2. TẬP LUẬT MỜ (13 LUẬT)
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
# 3. CHẠY TEST CSV & VẼ ĐỒ THỊ 2D
# ==========================================
if __name__ == "__main__":
    print("ĐANG ĐỌC FILE TEST VÀ CHẠY MÔ PHỎNG...\n")
    try:
        df = pd.read_csv('test_cases.csv')
        results = []
        for index, row in df.iterrows():
            
            res = predict_wash(row['Dirt_Amount'], row['Dirt_Type'], row['Sensitivity'], row['Cloth_Amount'])
            
            res_dict = {'Kịch bản': row['Ghi_chu'], 'Time (phút)': res['wash_time'], 'Spin (vòng/p)': res['spin_speed'], 'Nước (%)': res['water_amount'], 'Xà phòng (%)': res['detergent'], 'Nhiệt độ (C)': res['water_temp']}
            results.append(res_dict)
            
            print(f"[{row['ID']}] {row['Ghi_chu']}:")
            print(f"   -> Giặt: {res['wash_time']} phút | Vắt: {res['spin_speed']} rpm | Nước: {res['water_amount']}% | Xà phòng: {res['detergent']}% | Nhiệt: {res['water_temp']}°C")
            print("-" * 60)
        pd.DataFrame(results).to_csv('result.csv', index=False)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'test_cases.csv'.")

    print("\nĐANG VẼ TOÀN BỘ 9 BIỂU ĐỒ TRỰC QUAN...")
    dirt_amount.view(sim=washing_sim)
    dirt_type.view(sim=washing_sim)
    cloth_sensitivity.view(sim=washing_sim)
    cloth_amount.view(sim=washing_sim)
    wash_time.view(sim=washing_sim)
    spin_speed.view(sim=washing_sim)
    water_amount.view(sim=washing_sim)
    detergent.view(sim=washing_sim)
    water_temp.view(sim=washing_sim)
    plt.show()