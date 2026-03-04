"""
環境測試標準定義
依據以下公開法規整理：
- IEC 60068-2-14: 溫度循環測試
- IEC 60068-2-30: 濕熱循環測試
- EN 50155:2017:  歐洲鐵路電子設備
- IEC 61850-3:    變電站通訊自動化設備
- DNV 2.4:       船舶設備環境認證
- KEMA/CENELEC:  荷蘭/歐洲電力設備認證
- NMEA 0183/2000: 航海電子通訊設備 (IEC 61162)
"""

STANDARDS_AND_SOPS = {
    # ─────────────────────────────────────────
    # ✅ IEC 60068-2-14 溫度循環
    # ─────────────────────────────────────────
    "IEC60068_CYCLE": {
        "sop_id": "temp_cycle_test",
        "name": "溫度循環測試",
        "test_type": "IEC 60068-2-14 Temperature Cycling",
        "version": "v2.1",
        "high_temperature": 85.0,
        "low_temperature": -40.0,
        "ramp_rate": 2.0,  # °C/min，IEC 60068-2-14 規定
        "dwell_time": 60,  # 分鐘，每溫度停留時間
        "cycles": 5,
        "humidity": None,  # 溫度循環不控制濕度
        "temp_tolerance": 2.0,  # ±2°C，IEC 60068 標準容差
        "humi_tolerance": 5.0,
        "reference": "IEC 60068-2-14:2009",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認高溫 85°C / 低溫 -40°C / 速率 2°C/min / 5 循環",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控升降溫曲線，確認符合 IEC 60068-2-14",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與溫度數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # ✅ EN 50155 高溫儲存
    # ─────────────────────────────────────────
    "EN50155_HIGH": {
        "sop_id": "en50155_high_temp",
        "name": "EN50155 高溫儲存測試",
        "test_type": "EN 50155:2017 High Temperature Storage",
        "version": "v1.3",
        "high_temperature": 70.0,
        "low_temperature": None,
        "target_temperature": 70.0,
        "ramp_rate": 5.0,  # °C/min，EN 50155 規定上限
        "dwell_time": 960,  # 16 小時
        "cycles": 1,
        "humidity": None,
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "EN 50155:2017 Clause 12.2.4",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認目標溫度 70°C / 速率 ≤5°C/min / 持續 16 小時",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控升溫過程，確認符合 EN 50155:2017",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與溫度數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # ✅ EN 50155 低溫儲存
    # ─────────────────────────────────────────
    "EN50155_LOW": {
        "sop_id": "en50155_low_temp",
        "name": "EN50155 低溫儲存測試",
        "test_type": "EN 50155:2017 Low Temperature Storage",
        "version": "v1.3",
        "high_temperature": None,
        "low_temperature": -40.0,
        "target_temperature": -40.0,
        "ramp_rate": 5.0,
        "dwell_time": 960,  # 16 小時
        "cycles": 1,
        "humidity": None,
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "EN 50155:2017 Clause 12.2.4",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認目標溫度 -40°C / 速率 ≤5°C/min / 持續 16 小時",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控降溫過程，確認符合 EN 50155:2017",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與溫度數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # ✅ IEC 60068-2-30 濕熱循環
    # ─────────────────────────────────────────
    "IEC60068_DAMP": {
        "sop_id": "damp_heat_cycle",
        "name": "濕熱循環測試",
        "test_type": "IEC 60068-2-30 Damp Heat Cycling",
        "version": "v1.0",
        "high_temperature": 55.0,
        "low_temperature": 25.0,
        "target_temperature": 55.0,
        "ramp_rate": 2.0,
        "dwell_time": 720,  # 12 小時（每循環 24 小時）
        "cycles": 6,
        "humidity": 95.0,  # 95% RH
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "IEC 60068-2-30:2005",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱加水至正常水位",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認溫度 25~55°C / 濕度 95%RH / 6 循環",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控溫濕度循環曲線，確認符合 IEC 60068-2-30",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與溫濕度數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # 🆕 IEC 61850-3 變電站通訊設備
    # 依據：IEC 61850-3:2013，溫度 -10~+55°C（標準），延伸 -40~+70°C
    # ─────────────────────────────────────────
    "IEC61850_3": {
        "sop_id": "iec61850_3_env",
        "name": "IEC 61850-3 變電站設備環境測試",
        "test_type": "IEC 61850-3 Substation Environmental Test",
        "version": "v1.0",
        "high_temperature": 70.0,  # 延伸溫度範圍上限
        "low_temperature": -40.0,  # 延伸溫度範圍下限
        "target_temperature": 70.0,
        "ramp_rate": 2.0,  # 遵照 IEC 60068-2-14
        "dwell_time": 60,
        "cycles": 3,
        "humidity": 95.0,  # 95% RH，24小時平均
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "IEC 61850-3:2013 + IEC 60068-2-14",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認溫度 -40~+70°C / 濕度 95%RH / 3 循環",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控測試曲線，確認符合 IEC 61850-3:2013",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # 🆕 DNV 2.4 船舶設備認證
    # 依據：DNV Standard for Certification No. 2.4
    # 溫度容差 ±2°C，濕度容差 ±10%RH（一般）/ +2%/-3%（精密）
    # ─────────────────────────────────────────
    "DNV_2_4": {
        "sop_id": "dnv_2_4_env",
        "name": "DNV 2.4 船舶設備環境測試",
        "test_type": "DNV Standard for Certification 2.4",
        "version": "v1.0",
        "high_temperature": 70.0,  # DNV Class C/D 上限
        "low_temperature": -25.0,  # DNV 低溫儲存
        "target_temperature": 70.0,
        "ramp_rate": 3.0,  # DNV 2.4 規定升溫速率
        "dwell_time": 120,  # 2 小時穩定時間
        "cycles": 2,  # DNV 要求 2 循環
        "humidity": 95.0,  # 95% RH
        "temp_tolerance": 2.0,  # DNV 2.4 ±2°C
        "humi_tolerance": 10.0,  # DNV 2.4 ±10%RH（一般容差）
        "reference": "DNV Standard for Certification No. 2.4",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認溫度 -25~+70°C / 濕度 95%RH / 2 循環 / DNV 2.4",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控測試曲線，確認符合 DNV Standard 2.4",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # 🆕 KEMA / CENELEC 電力設備認證
    # 依據：KEMA KEUR，基於 IEC/CENELEC 標準
    # KEMA Labs 為 ISO/IEC 17025 認可實驗室
    # ─────────────────────────────────────────
    "KEMA": {
        "sop_id": "kema_env",
        "name": "KEMA 電力設備環境測試",
        "test_type": "KEMA / CENELEC Environmental Certification",
        "version": "v1.0",
        "high_temperature": 70.0,
        "low_temperature": -25.0,
        "target_temperature": 70.0,
        "ramp_rate": 2.0,  # 遵照 IEC/CENELEC
        "dwell_time": 120,
        "cycles": 2,
        "humidity": 93.0,  # 93% RH（KEMA 電力設備標準）
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "KEMA KEUR + IEC 60068 + CENELEC",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認溫度 -25~+70°C / 濕度 93%RH / KEMA 規格",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控測試曲線，確認符合 KEMA / CENELEC 要求",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與數據",
            },
        ],
    },
    # ─────────────────────────────────────────
    # 🆕 NMEA 0183 / NMEA 2000 航海電子設備
    # 依據：IEC 61162-1 (NMEA 0183) / IEC 61162-3 (NMEA 2000)
    # 海洋環境：鹽霧、高濕、寬溫度範圍
    # ─────────────────────────────────────────
    "NMEA_MARINE": {
        "sop_id": "nmea_marine_env",
        "name": "NMEA 航海電子設備環境測試",
        "test_type": "NMEA 0183/2000 Marine Environmental Test (IEC 61162)",
        "version": "v1.0",
        "high_temperature": 55.0,
        "low_temperature": -15.0,
        "target_temperature": 55.0,
        "ramp_rate": 2.0,
        "dwell_time": 60,
        "cycles": 3,
        "humidity": 95.0,  # 海洋環境高濕度
        "temp_tolerance": 2.0,
        "humi_tolerance": 5.0,
        "reference": "IEC 61162-1 (NMEA 0183) / IEC 61162-3 (NMEA 2000)",
        "steps": [
            {
                "step_id": 1,
                "name": "設備開機與檢查",
                "description": "確認電源、保險絲、水箱、連接狀態正常",
            },
            {
                "step_id": 2,
                "name": "確認測試參數",
                "description": "確認溫度 -15~+55°C / 濕度 95%RH / IEC 61162",
            },
            {
                "step_id": 3,
                "name": "監控測試過程",
                "description": "監控測試曲線，確認符合 NMEA / IEC 61162 要求",
            },
            {
                "step_id": 4,
                "name": "儲存測試紀錄",
                "description": "測試完成後儲存執行紀錄與數據",
            },
        ],
    },
}


def get_standard(standard_id: str) -> dict:
    """取得指定標準的完整參數"""
    return STANDARDS_AND_SOPS.get(standard_id, {})


def get_ramp_rate(standard_id: str) -> float:
    """取得指定標準的升降溫速率（°C/min）"""
    return STANDARDS_AND_SOPS.get(standard_id, {}).get("ramp_rate", 2.0)


def get_all_standards() -> list:
    """取得所有標準 ID 列表"""
    return list(STANDARDS_AND_SOPS.keys())


def get_sop_by_standard(standard_id: str) -> dict:
    """依標準 ID 取得 SOP 資料"""
    return STANDARDS_AND_SOPS.get(standard_id, {})
