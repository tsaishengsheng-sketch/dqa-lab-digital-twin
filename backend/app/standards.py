"""
环境测试标准定义
参考: EN50155, IEC60068, NEMA 等
"""

# EN50155 - 铁路设备
EN50155_HIGH_TEMP = {
    "standard": "EN50155",
    "test_name": "High Temperature Storage",
    "target_temp": 70,  # °C
    "duration_hours": 16,
    "ramp_rate_max": 5.0,  # °C/min
    "stabilization_time": 2,  # 小时
    "power_cycling": False,
    "humidity_control": False
}

EN50155_LOW_TEMP = {
    "standard": "EN50155",
    "test_name": "Low Temperature Storage",
    "target_temp": -40,
    "duration_hours": 16,
    "ramp_rate_max": 5.0,
    "stabilization_time": 2,
    "power_cycling": False,
    "humidity_control": False
}

# IEC 60068-2-14 - 温度循环
IEC60068_TEMP_CYCLE = {
    "standard": "IEC60068-2-14",
    "test_name": "Temperature Cycling",
    "cycles": 5,
    "low_temp": -40,
    "high_temp": 85,
    "dwell_time_hours": 1,  # 每个温度停留
    "ramp_rate": 2.0,  # °C/min
    "transition_time_minutes": (85 - (-40)) / 2.0  # 计算出的转换时间
}

# IEC 60068-2-30 - 湿热循环
IEC60068_DAMP_HEAT = {
    "standard": "IEC60068-2-30",
    "test_name": "Damp Heat Cyclic",
    "cycles": 6,
    "low_temp": 25,
    "high_temp": 55,
    "humidity_rh": 95,
    "cycle_duration_hours": 24
}

# 标准列表
STANDARDS = {
    "EN50155_HIGH": EN50155_HIGH_TEMP,
    "EN50155_LOW": EN50155_LOW_TEMP,
    "IEC60068_CYCLE": IEC60068_TEMP_CYCLE,
    "IEC60068_DAMP": IEC60068_DAMP_HEAT,
}