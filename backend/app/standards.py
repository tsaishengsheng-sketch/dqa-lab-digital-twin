"""
環境測試標準定義 + SOP 整合
參考: EN50155, IEC60068, IEC60954, IEC61850, KEMA, NEMA
"""

from typing import Dict, List, Any, Optional
# ============================================================================
# 標準定義 + SOP 步驟整合
# ============================================================================
STANDARDS_AND_SOPS: Dict[str, Dict[str, Any]]  = {
    "IEC60068_CYCLE": {
        "standard_id": "IEC60068-2-14",
        "sop_id": "temp_cycle_test",
        "name": "溫度循環測試",
        "test_type": "chamber",
        "version": "1.0",
        "description": "IEC 60068-2-14 溫度循環環境測試",
        
        # 標準參數
        "number_of_cycles": 5,
        "low_temperature": -40,
        "high_temperature": 85,
        "dwell_time_hours": 1,
        "ramp_rate": 2.0,  # °C/分鐘
        "stabilization_time_hours": 0.5,
        "power_on": False,
        "humidity_control": False,
        
        # SOP 步驟
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱水位正常。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 2,
                "name": "設定循環參數",
                "description": "設定低溫 -40°C，高溫 85°C，5 個循環，每個循環 3 小時",
                "requires_photo": False,
                "requires_parameters": True,
                "optional": False,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "low_temp": {"type": "number", "title": "低溫 (°C)", "default": -40},
                        "high_temp": {"type": "number", "title": "高溫 (°C)", "default": 85},
                        "cycles": {"type": "integer", "title": "循環次數", "default": 5},
                        "dwell_time": {"type": "integer", "title": "停留時間 (小時)", "default": 1},
                        "ramp_rate": {"type": "number", "title": "升降溫速率 (°C/min)", "default": 2.0}
                    },
                    "required": ["low_temp", "high_temp", "cycles"]
                }
            },
            {
                "step_id": 3,
                "name": "啟動測試",
                "description": "按下 RUN 鍵，確認測試啟動。",
                "requires_photo": False,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 4,
                "name": "監控測試過程",
                "description": "定時檢查溫度曲線是否正常。",
                "requires_photo": False,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 5,
                "name": "儲存測試紀錄",
                "description": "測試完成後，儲存 CSV 檔案。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            }
        ]
    },
    
    "EN50155_HIGH": {
        "standard_id": "EN50155",
        "sop_id": "en50155_high_temp",
        "name": "EN50155 高溫儲存測試",
        "test_type": "chamber",
        "version": "1.0",
        "description": "歐洲鐵路設備高溫環境測試",
        
        "target_temperature": 70,
        "duration_hours": 16,
        "ramp_rate_max": 5.0,
        "stabilization_time_hours": 2,
        "power_on": False,
        "humidity_control": False,
        
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱水位正常。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 2,
                "name": "設定高溫參數",
                "description": "設定溫度 70°C，持續 16 小時，升溫速率不超過 5°C/分鐘",
                "requires_photo": False,
                "requires_parameters": True,
                "optional": False,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number", "title": "測試溫度 (°C)", "default": 70},
                        "duration": {"type": "integer", "title": "測試時間 (小時)", "default": 16},
                        "ramp_rate_max": {"type": "number", "title": "最大升溫速率 (°C/min)", "default": 5.0}
                    },
                    "required": ["temperature", "duration"]
                }
            },
            {
                "step_id": 3,
                "name": "啟動測試",
                "description": "按下 RUN 鍵，確認測試啟動。",
                "requires_photo": False,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後，儲存 CSV 檔案。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            }
        ]
    },
    
    "EN50155_LOW": {
        "standard_id": "EN50155",
        "sop_id": "en50155_low_temp",
        "name": "EN50155 低溫儲存測試",
        "test_type": "chamber",
        "version": "1.0",
        "description": "歐洲鐵路設備低溫環境測試",
        
        "target_temperature": -40,
        "duration_hours": 16,
        "ramp_rate_max": 5.0,
        "stabilization_time_hours": 2,
        "power_on": False,
        "humidity_control": False,
        
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱水位正常。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 2,
                "name": "設定低溫參數",
                "description": "設定溫度 -40°C，持續 16 小時，降溫速率不超過 5°C/分鐘",
                "requires_photo": False,
                "requires_parameters": True,
                "optional": False,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number", "title": "測試溫度 (°C)", "default": -40},
                        "duration": {"type": "integer", "title": "測試時間 (小時)", "default": 16},
                        "ramp_rate_max": {"type": "number", "title": "最大降溫速率 (°C/min)", "default": 5.0}
                    },
                    "required": ["temperature", "duration"]
                }
            },
            {
                "step_id": 3,
                "name": "啟動測試",
                "description": "按下 RUN 鍵，確認測試啟動。",
                "requires_photo": False,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後，儲存 CSV 檔案。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            }
        ]
    },
    
    "IEC60068_DAMP": {
        "standard_id": "IEC60068-2-30",
        "sop_id": "damp_heat_cyclic_test",
        "name": "濕熱循環測試",
        "test_type": "chamber",
        "version": "1.0",
        "description": "IEC 60068-2-30 濕熱循環環境測試",
        
        "number_of_cycles": 6,
        "low_temperature": 25,
        "high_temperature": 55,
        "humidity_rh_percent": 95,
        "cycle_duration_hours": 24,
        "ramp_rate": 2.0,
        "power_on": False,
        "humidity_control": True,
        
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱水位正常。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 2,
                "name": "設定濕熱循環",
                "description": "設定 25°C→55°C，93% RH，6 個循環，每循環 24 小時",
                "requires_photo": False,
                "requires_parameters": True,
                "optional": False,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "low_temp": {"type": "number", "title": "低溫 (°C)", "default": 25},
                        "high_temp": {"type": "number", "title": "高溫 (°C)", "default": 55},
                        "humidity": {"type": "number", "title": "濕度 (%)", "default": 95},
                        "cycles": {"type": "integer", "title": "循環次數", "default": 6},
                        "cycle_duration": {"type": "integer", "title": "每循環時間 (小時)", "default": 24}
                    },
                    "required": ["low_temp", "high_temp", "humidity", "cycles"]
                }
            },
            {
                "step_id": 3,
                "name": "啟動測試",
                "description": "按下 RUN 鍵，確認測試啟動。",
                "requires_photo": False,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後，儲存 CSV 檔案。",
                "requires_photo": True,
                "requires_parameters": False,
                "optional": False,
                "parameters_schema": None
            }
        ]
    }
}

# ============================================================================
# 輔助函數
# ============================================================================

def get_standard(standard_id):
    """根據標準 ID 獲取標準定義"""
    return STANDARDS_AND_SOPS.get(standard_id)

def get_ramp_rate(standard_id):
    """獲取升溫速率限制"""
    standard = get_standard(standard_id)
    if standard:
        return standard.get("ramp_rate_max") or standard.get("ramp_rate", 3.0)
    return 3.0

def get_all_standards():
    """獲取所有標準列表"""
    return list(STANDARDS_AND_SOPS.keys())

def get_sop_by_standard(standard_id):
    """根據標準 ID 獲取完整的 SOP 定義"""
    standard = get_standard(standard_id)
    if standard:
        return {
            "sop_id": standard.get("sop_id"),
            "name": standard.get("name"),
            "test_type": standard.get("test_type"),
            "version": standard.get("version"),
            "description": standard.get("description"),
            "steps": standard.get("steps", [])
        }
    return None