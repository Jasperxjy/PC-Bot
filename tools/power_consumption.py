def calculate_power_consumption(config_list):
    """
    计算整机功耗并推荐电源功率

    参数:
    config_list: 包含所有选定部件的列表，每个部件是查询返回的字典

    返回:
    dict: 包含总功耗估算和推荐电源功率
    """
    # 组件基础功耗估算表 (单位: 瓦特)
    # 这些是基于行业标准的估算值，可以根据实际数据调整
    COMPONENT_POWER_ESTIMATES = {
        "motherboard": 30,  # 主板基础功耗
        "ram": 5,  # 每根内存条
        "ssd": 5,  # 每个SATA/NVMe SSD
        "hdd": 10,  # 每个机械硬盘
        "cooling": 10,  # 每个风扇或水冷泵
        "other": 30,  # 其他组件（RGB灯效、PCIe设备等）
    }

    total_power = 0
    component_breakdown = {}  # 记录各组件功耗明细

    # 统计各类型组件数量
    component_counts = {}
    for component in config_list:
        comp_type = component['category']
        component_counts[comp_type] = component_counts.get(comp_type, 0) + 1

    # 计算CPU功耗
    cpu_components = [c for c in config_list if c['category'] == 'cpu']
    if cpu_components:
        cpu = cpu_components[0]  # 假设只有一个CPU
        cpu_tdp = cpu['specs'].get('tdp', 65)  # 默认65W
        # CPU实际功耗可能高于TDP（特别是超频或boost时）
        cpu_power = cpu_tdp * 1.2  # 增加20%余量
        total_power += cpu_power
        component_breakdown['cpu'] = cpu_power

    # 计算GPU功耗
    gpu_components = [c for c in config_list if c['category'] == 'gpu']
    for gpu in gpu_components:
        # 优先使用TDP数据
        if 'tdp' in gpu['specs']:
            gpu_power = gpu['specs']['tdp']
        # 如果没有TDP，尝试从推荐PSU反向估算
        elif 'recommended_psu' in gpu['specs']:
            # 假设GPU功耗约占整机功耗的40-50%，据此反向估算
            recommended_psu = gpu['specs']['recommended_psu']
            # 从字符串中提取数字（例如："650W" -> 650）
            import re
            match = re.search(r'(\d+)', str(recommended_psu))
            if match:
                psu_wattage = int(match.group(1))
                gpu_power = psu_wattage * 0.4  # 保守估算为推荐PSU的40%
            else:
                gpu_power = 150  # 默认值
        else:
            # 根据GPU型号和级别估算
            gpu_model = gpu['model'].lower()
            if 'rtx 4090' in gpu_model or 'rx 7900 xtx' in gpu_model:
                gpu_power = 450
            elif 'rtx 4080' in gpu_model or 'rx 7900 xt' in gpu_model:
                gpu_power = 320
            elif 'rtx 4070' in gpu_model or 'rx 7800 xt' in gpu_model:
                gpu_power = 200
            elif 'rtx 4060' in gpu_model or 'rx 7700 xt' in gpu_model:
                gpu_power = 160
            else:
                gpu_power = 150  # 默认值

        # 增加15%余量考虑峰值功耗
        gpu_power *= 1.15
        total_power += gpu_power
        component_breakdown[f"gpu_{gpu['model']}"] = gpu_power

    # 计算其他组件功耗
    for comp_type, estimate in COMPONENT_POWER_ESTIMATES.items():
        if comp_type in component_counts:
            count = component_counts[comp_type]
            power = estimate * count
            total_power += power
            component_breakdown[comp_type] = power

    # 计算推荐电源功率（增加20-30%余量）
    # 更高端的配置需要更多余量
    if total_power > 600:
        safety_margin = 1.3  # 30%余量
    else:
        safety_margin = 1.2  # 20%余量

    recommended_psu = round(total_power * safety_margin)

    # 取整到常见的电源规格（550W, 650W, 750W, 850W等）
    common_psu_wattages = [450, 550, 650, 750, 850, 1000, 1200, 1500]
    for wattage in common_psu_wattages:
        if wattage >= recommended_psu:
            recommended_psu = wattage
            break
    else:
        # 如果超出了常见规格，取最接近的100的倍数
        recommended_psu = round(recommended_psu / 100) * 100

    return {
        "total_power_estimate": round(total_power),
        "recommended_psu_wattage": recommended_psu,
        "component_breakdown": component_breakdown
    }


# 示例使用
if __name__ == "__main__":
    # 模拟一个配置列表
    sample_config = [
        {
            "name": "Intel Core i5-13400F",
            "category": "cpu",
            "specs": {"tdp": 65}
        },
        {
            "name": "NVIDIA GeForce RTX 4060",
            "category": "gpu",
            "specs": {"recommended_psu": "550W"}
        },
        {
            "name": "ASUS TUF Gaming B760-PLUS",
            "category": "motherboard",
            "specs": {}
        },
        {
            "name": "Corsair Vengeance 16GB DDR5",
            "category": "ram",
            "specs": {}
        },
        {
            "name": "Samsung 980 Pro 1TB",
            "category": "ssd",
            "specs": {}
        }
    ]

    result = calculate_power_consumption(sample_config)
    print(f"总功耗估算: {result['total_power_estimate']}W")
    print(f"推荐电源: {result['recommended_psu_wattage']}W")
    print("各组件功耗明细:")
    for component, power in result['component_breakdown'].items():
        print(f"  {component}: {power}W")