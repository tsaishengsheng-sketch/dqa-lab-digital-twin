import requests
import json

url = "http://127.0.0.1:8000/api/sop/"

# 测试方法库：基于 IEC 60068、EN 50155 等规范
test_methods = [
    {
        "sop_id": "low_temp_test_v1",
        "name": "低温测试 (IEC 60068-2-1)",
        "test_type": "chamber",
        "version": "1.0",
        "steps": [
            {"step_id": 1, "name": "设备开机与检查", "description": "确认电源、保险丝、水箱水位正常。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 2, "name": "设置测试参数", "description": "设定低温测试条件", "requires_photo": False, "requires_parameters": True, "optional": False, "parameters_schema": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "title": "测试温度 (°C)", "default": -40},
                    "duration": {"type": "integer", "title": "持续时间 (小时)", "default": 48},
                    "power_on_time": {"type": "integer", "title": "开机时间 (分钟)", "default": 5},
                    "power_off_time": {"type": "integer", "title": "关机时间 (分钟)", "default": 2},
                    "cycles": {"type": "integer", "title": "循环次数", "default": 300}
                },
                "required": ["temperature", "duration", "cycles"]
            }},
            {"step_id": 3, "name": "启动测试", "description": "按下 RUN 键，确认测试启动。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 4, "name": "监控测试过程", "description": "定时检查温度曲线是否正常。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 5, "name": "存储测试记录", "description": "测试完成后，存储 CSV 文件。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None}
        ]
    },
    {
        "sop_id": "high_temp_test_v1",
        "name": "高温测试 (IEC 60068-2-2)",
        "test_type": "chamber",
        "version": "1.0",
        "steps": [
            {"step_id": 1, "name": "设备开机与检查", "description": "确认电源、保险丝、水箱水位正常。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 2, "name": "设置测试参数", "description": "设定高温测试条件", "requires_photo": False, "requires_parameters": True, "optional": False, "parameters_schema": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "title": "测试温度 (°C)", "default": 85},
                    "humidity": {"type": "number", "title": "湿度 (%)", "default": 40},
                    "duration": {"type": "integer", "title": "持续时间 (小时)", "default": 16}
                },
                "required": ["temperature", "duration"]
            }},
            {"step_id": 3, "name": "启动测试", "description": "按下 RUN 键，确认测试启动。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 4, "name": "监控测试过程", "description": "定时检查温度曲线是否正常。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 5, "name": "存储测试记录", "description": "测试完成后，存储 CSV 文件。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None}
        ]
    },
    {
        "sop_id": "temp_cycle_test_v1",
        "name": "温度循环测试 (IEC 60068-2-14)",
        "test_type": "chamber",
        "version": "1.0",
        "steps": [
            {"step_id": 1, "name": "设备开机与检查", "description": "确认电源、保险丝、水箱水位正常。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 2, "name": "设置循环参数", "description": "设定温度循环条件", "requires_photo": False, "requires_parameters": True, "optional": False, "parameters_schema": {
                "type": "object",
                "properties": {
                    "low_temp": {"type": "number", "title": "低温 (°C)", "default": -40},
                    "high_temp": {"type": "number", "title": "高温 (°C)", "default": 85},
                    "cycles": {"type": "integer", "title": "循环次数", "default": 5},
                    "dwell_time": {"type": "integer", "title": "停留时间 (小时)", "default": 3},
                    "ramp_rate": {"type": "number", "title": "升降速率 (°C/min)", "default": 1}
                },
                "required": ["low_temp", "high_temp", "cycles"]
            }},
            {"step_id": 3, "name": "启动测试", "description": "按下 RUN 键，确认测试启动。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 4, "name": "监控测试过程", "description": "定时检查温度曲线是否正常。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 5, "name": "存储测试记录", "description": "测试完成后，存储 CSV 文件。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None}
        ]
    },
    {
        "sop_id": "damp_heat_cyclic_test_v1",
        "name": "湿热循环测试 (IEC 60068-2-30)",
        "test_type": "chamber",
        "version": "1.0",
        "steps": [
            {"step_id": 1, "name": "设备开机与检查", "description": "确认电源、保险丝、水箱水位正常。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 2, "name": "设置湿热循环参数", "description": "设定湿热循环条件", "requires_photo": False, "requires_parameters": True, "optional": False, "parameters_schema": {
                "type": "object",
                "properties": {
                    "low_temp": {"type": "number", "title": "低温 (°C)", "default": 25},
                    "high_temp": {"type": "number", "title": "高温 (°C)", "default": 55},
                    "humidity": {"type": "number", "title": "湿度 (%)", "default": 93},
                    "cycles": {"type": "integer", "title": "循环次数", "default": 6},
                    "cycle_duration": {"type": "integer", "title": "每循环时间 (小时)", "default": 24}
                },
                "required": ["low_temp", "high_temp", "humidity", "cycles"]
            }},
            {"step_id": 3, "name": "启动测试", "description": "按下 RUN 键，确认测试启动。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 4, "name": "监控测试过程", "description": "定时检查温度曲线是否正常。", "requires_photo": False, "requires_parameters": False, "optional": False, "parameters_schema": None},
            {"step_id": 5, "name": "存储测试记录", "description": "测试完成后，存储 CSV 文件。", "requires_photo": True, "requires_parameters": False, "optional": False, "parameters_schema": None}
        ]
    }
]

for sop in test_methods:
    response = requests.post(url, json=sop)
    if response.status_code == 200:
        print(f"✅ 成功新增: {sop['name']}")
    else:
        print(f"❌ 失败 {sop['name']}: {response.status_code} - {response.text}")