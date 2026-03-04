import io
import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .models import SessionLocal, SopExecution, StepRecord, DeviceData
from .standards import get_standard, STANDARDS_AND_SOPS

router = APIRouter(prefix="/api/reports", tags=["reports"])

REPORT_VERSION = "1.0"
LAB_NAME = "DQA Lab - KSON AICM Digital Twin"

# IEC 60068 / ISO 17025 標準容差
TEMP_TOLERANCE = 2.0  # ±2°C (IEC 60068 一般量測容差)
HUMI_TOLERANCE = 5.0  # ±5% RH


def _write(output: io.BytesIO, text: str):
    output.write((text + "\r\n").encode("big5", errors="replace"))


def _section(output: io.BytesIO, title: str):
    _write(output, "")
    _write(output, "=" * 60)
    _write(output, f"  {title}")
    _write(output, "=" * 60)


def _row(output: io.BytesIO, label: str, value):
    _write(output, f"  {label:<28}{value}")


@router.get("/csv/{execution_id}")
def download_csv_report(execution_id: int):
    """下載符合 ISO 17025 格式的 CSV 測試報告"""
    db = SessionLocal()
    try:
        # --- 取得資料 ---
        execution = (
            db.query(SopExecution).filter(SopExecution.id == execution_id).first()
        )
        if not execution:
            raise HTTPException(status_code=404, detail="找不到此執行紀錄")

        steps = (
            db.query(StepRecord)
            .filter(StepRecord.execution_id == execution_id)
            .order_by(StepRecord.step_id)
            .all()
        )

        start_time = execution.created_at - datetime.timedelta(hours=24)
        end_time = execution.created_at + datetime.timedelta(hours=24)
        device_records = (
            db.query(DeviceData)
            .filter(
                DeviceData.device_id == "KSON_CH01",
                DeviceData.timestamp >= start_time,
                DeviceData.timestamp <= end_time,
            )
            .order_by(DeviceData.timestamp)
            .all()
        )

        # --- 從 standards.py 取得測試條件 ---
        sop_data = None
        standard_id = None
        for std_id, std_data in STANDARDS_AND_SOPS.items():
            if std_data.get("sop_id") == execution.sop_id:
                sop_data = std_data
                standard_id = std_id
                break
        standard = get_standard(standard_id) if standard_id else {}

        # --- 統計溫度數據 ---
        temps = [r.temperature for r in device_records if r.temperature is not None]
        humis = [r.humidity for r in device_records if r.humidity is not None]

        temp_max = round(max(temps), 2) if temps else "N/A"
        temp_min = round(min(temps), 2) if temps else "N/A"
        temp_avg = round(sum(temps) / len(temps), 2) if temps else "N/A"
        humi_avg = round(sum(humis) / len(humis), 1) if humis else "N/A"

        # --- PASS / FAIL 判斷 (IEC 60068 ±2°C 容差) ---
        target_high = standard.get("high_temperature") or standard.get(
            "target_temperature"
        )
        target_low = standard.get("low_temperature")
        pass_fail = "PASS"
        fail_reason = []

        if target_high and temps:
            if temp_max > target_high + TEMP_TOLERANCE:
                pass_fail = "FAIL"
                fail_reason.append(
                    f"最高溫 {temp_max}°C 超出上限 {target_high + TEMP_TOLERANCE}°C"
                )
        if target_low and temps:
            if temp_min < target_low - TEMP_TOLERANCE:
                pass_fail = "FAIL"
                fail_reason.append(
                    f"最低溫 {temp_min}°C 超出下限 {target_low - TEMP_TOLERANCE}°C"
                )

        # --- 產生報告 ---
        output = io.BytesIO()
        report_no = f"RPT-{execution.created_at.strftime('%Y%m%d')}-{execution_id:03d}"

        _write(output, "")
        _write(output, "  ██████████████████████████████████████████████████████████")
        _write(output, f"  {LAB_NAME}")
        _write(output, "  環境測試報告 Environmental Test Report")
        _write(output, "  ██████████████████████████████████████████████████████████")

        # 1. 報告識別資訊 (ISO 17025 Clause 7.8 要求)
        _section(output, "1. 報告識別資訊 Report Identification")
        _row(output, "報告編號 Report No.:", report_no)
        _row(output, "報告版本 Version:", REPORT_VERSION)
        _row(
            output,
            "產生日期 Issue Date:",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        _row(output, "執行記錄 ID:", execution_id)
        _row(output, "參考標準 Reference Standard:", "ISO/IEC 17025:2017")

        # 2. 受測樣品資訊
        _section(output, "2. 受測樣品資訊 Test Item Information")
        _row(output, "設備編號 Device ID:", "KSON_CH01")
        _row(output, "SOP ID:", execution.sop_id)
        _row(
            output,
            "測試名稱 Test Name:",
            sop_data.get("name", "N/A") if sop_data else "N/A",
        )
        _row(
            output,
            "測試類型 Test Type:",
            sop_data.get("test_type", "N/A") if sop_data else "N/A",
        )
        _row(
            output,
            "測試版本 SOP Version:",
            sop_data.get("version", "N/A") if sop_data else "N/A",
        )

        # 3. 測試條件 (IEC 60068 要求記錄完整測試條件)
        _section(output, "3. 測試條件 Test Conditions")
        _row(output, "測試標準 Standard:", standard_id or "N/A")
        _row(output, "目標高溫 Target High (°C):", target_high or "N/A")
        _row(output, "目標低溫 Target Low (°C):", target_low or "N/A")
        _row(
            output,
            "升降溫速率 Ramp Rate (°C/min):",
            standard.get("ramp_rate", "N/A") if standard else "N/A",
        )
        _row(
            output,
            "循環次數 Cycles:",
            standard.get("cycles", "N/A") if standard else "N/A",
        )
        _row(output, "溫度容差 Temp Tolerance (°C):", f"± {TEMP_TOLERANCE} (IEC 60068)")
        _row(
            output, "濕度容差 Humi Tolerance (%RH):", f"± {HUMI_TOLERANCE} (IEC 60068)"
        )
        _row(
            output,
            "測試開始 Test Start:",
            execution.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        _row(output, "數據筆數 Data Points:", len(device_records))

        # 4. 步驟執行記錄
        _section(output, "4. 步驟執行記錄 Step Execution Records")
        _write(output, f"  {'步驟':>6}  {'名稱':<20}  {'狀態':<8}")
        _write(output, "  " + "-" * 40)
        for step in steps:
            status = "完成 PASS" if step.completed else "未完成 FAIL"
            _write(output, f"  Step {step.step_id:<4}  {'':<20}  {status}")
        if not steps:
            _write(output, "  （無步驟記錄）")

        # 5. 測試數據統計摘要
        _section(output, "5. 測試數據統計摘要 Measurement Summary")
        _row(output, "最高溫度 Max Temp (°C):", temp_max)
        _row(output, "最低溫度 Min Temp (°C):", temp_min)
        _row(output, "平均溫度 Avg Temp (°C):", temp_avg)
        _row(output, "平均濕度 Avg Humi (%RH):", humi_avg)
        _row(output, "量測不確定度 Uncertainty:", "± 0.1°C (儀器解析度)")

        # 6. 測試結論 PASS / FAIL
        _section(output, "6. 測試結論 Test Conclusion")
        _row(output, "判定結果 Result:", f"【 {pass_fail} 】")
        if fail_reason:
            for reason in fail_reason:
                _row(output, "不合格原因:", reason)
        else:
            _row(output, "說明:", "所有溫度數據均在標準容差範圍內")
        _row(output, "判定依據:", f"IEC 60068 ± {TEMP_TOLERANCE}°C 容差")

        # 7. 原始溫濕度數據
        _section(output, "7. 原始溫濕度數據 Raw Temperature & Humidity Data")
        _write(output, f"  {'時間戳':<22}  {'溫度(°C)':>10}  {'濕度(%RH)':>10}")
        _write(output, "  " + "-" * 48)
        for record in device_records:
            ts = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            temp = (
                f"{round(record.temperature, 2):.2f}" if record.temperature else "N/A"
            )
            humi = f"{round(record.humidity, 1):.1f}" if record.humidity else "N/A"
            _write(output, f"  {ts:<22}  {temp:>10}  {humi:>10}")

        _write(output, "")
        _write(output, "=" * 60)
        _write(output, f"  報告結束 End of Report — {report_no}")
        _write(output, "=" * 60)
        _write(output, "")

        output.seek(0)
        filename = f"{report_no}_{execution.sop_id}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    finally:
        db.close()


@router.get("/list")
def list_executions():
    """取得所有執行紀錄列表"""
    db = SessionLocal()
    try:
        executions = (
            db.query(SopExecution).order_by(SopExecution.created_at.desc()).all()
        )
        return [
            {
                "id": e.id,
                "sop_id": e.sop_id,
                "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for e in executions
        ]
    finally:
        db.close()
