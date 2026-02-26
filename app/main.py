import json
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.core.detector import PrivacyDetector

app = FastAPI(title="Web3 Privacy Analytics Engine M2")
detector = PrivacyDetector()

@app.post("/api/v1/upload")
async def upload_traffic_file(file: UploadFile = File(...)):
    # 我还记着你说的话
    content = await file.read()
    text = content.decode('utf-8').strip()
    
    # 适配 LDJSON 格式（你提供的样例是每行一个 JSON）
    raw_list = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line: continue
        try:
            # 尝试解析每一行
            obj = json.loads(line)
            raw_list.append(obj)
        except json.JSONDecodeError:
            continue

    # 过滤非字典干扰项
    flows = [f for f in raw_list if isinstance(f, dict)]
    
    print(f"\n[DEBUG] Total Lines in File: {len(lines)}")
    print(f"[DEBUG] Valid JSON Flows: {len(flows)}")

    all_events = []
    affected_sessions = set()

    for flow in flows:
        events = detector.analyze_flow(flow)
        if events:
            all_events.extend(events)
            # 使用你的 flow_id 作为 session_id
            affected_sessions.add(flow.get("flow_id", "unknown"))

    print(f"[DEBUG] Leaks Detected: {len(all_events)}")

    # M2 评分
    score, level = detector.calculate_risk_severity(all_events)
    
    # 保存报告
    report_filename = f"full_report_{datetime.now().strftime('%H%M%S')}.json"
    serializable = [e.model_dump() for e in all_events]
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4, ensure_ascii=False)

    return {
        "m2_assessment": {"score": score, "risk_level": level},
        "stats": {"processed": len(flows), "leaks": len(all_events)},
        "report_file": report_filename,
        "sample": all_events[:3]
    }