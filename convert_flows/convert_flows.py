#!/usr/bin/env python3
"""
将 mitmproxy 的二进制 .flows 文件转换为结构化 JSON Lines 和 Parquet。
用法: python convert_flows.py input.flows output_prefix
示例: python convert_flows.py mycapture.flows output
会生成 output.jsonl 和 output.parquet
"""

import sys
import json
import base64
from datetime import datetime
from mitmproxy import io
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def extract_flow_info(flow):
    """从 flow 对象中提取关键信息"""
    req = flow.request
    resp = flow.response

    # 基础信息
    info = {
        "flow_id": flow.id,
        "timestamp_start": flow.request.timestamp_start,
        "timestamp_end": flow.response.timestamp_end if flow.response else None,
        "client_conn": {
            "address": str(flow.client_conn.address) if flow.client_conn else None,
            "tls_version": flow.client_conn.tls_version if flow.client_conn else None,
        },
        "server_conn": {
            "address": str(flow.server_conn.address) if flow.server_conn else None,
        }
    }

    # 请求信息
    if req:
        # 处理请求体：如果是 JSON 就解析，否则存为字符串或 base64
        req_content = None
        if req.raw_content:
            try:
                # 尝试解码为文本（JSON 或其他）
                req_content = req.text
            except:
                # 二进制内容，转为 base64
                req_content = base64.b64encode(req.raw_content).decode('ascii')

        info["request"] = {
            "method": req.method,
            "scheme": req.scheme,
            "host": req.host,
            "port": req.port,
            "path": req.path,
            "http_version": req.http_version,
            "headers": dict(req.headers),
            "content": req_content,
            "content_length": len(req.raw_content) if req.raw_content else 0,
        }

        # 尝试解析 JSON-RPC
        if req.headers.get("content-type", "").startswith("application/json") and req_content:
            try:
                json_body = json.loads(req_content)
                if isinstance(json_body, dict) and json_body.get("jsonrpc") == "2.0":
                    info["rpc"] = {
                        "method": json_body.get("method"),
                        "params": json_body.get("params"),
                        "id": json_body.get("id"),
                    }
            except:
                pass

    # 响应信息
    if resp:
        resp_content = None
        if resp.raw_content:
            try:
                resp_content = resp.text
            except:
                resp_content = base64.b64encode(resp.raw_content).decode('ascii')

        info["response"] = {
            "status_code": resp.status_code,
            "reason": resp.reason,
            "http_version": resp.http_version,
            "headers": dict(resp.headers),
            "content": resp_content,
            "content_length": len(resp.raw_content) if resp.raw_content else 0,
        }

    return info

def main():
    if len(sys.argv) < 3:
        print("用法: python convert_flows.py <input.flows> <output_prefix>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_prefix = sys.argv[2]

    print(f"读取 {input_file} ...")
    flows = []
    with open(input_file, "rb") as f:
        reader = io.FlowReader(f)
        for flow in reader.stream():
            flows.append(extract_flow_info(flow))
            if len(flows) % 100 == 0:
                print(f"已处理 {len(flows)} 条流...")

    print(f"共处理 {len(flows)} 条流，开始写入文件...")

    # 写入 JSON Lines
    jsonl_file = f"{output_prefix}.jsonl"
    with open(jsonl_file, "w", encoding="utf-8") as f:
        for flow in flows:
            f.write(json.dumps(flow, ensure_ascii=False) + "\n")
    print(f"JSON Lines 已保存至 {jsonl_file}")

    # 转换为 Pandas DataFrame 并保存为 Parquet
    df = pd.DataFrame(flows)
    # 将复杂列转换为 JSON 字符串（Parquet 要求）
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)
    parquet_file = f"{output_prefix}.parquet"
    df.to_parquet(parquet_file, index=False)
    print(f"Parquet 已保存至 {parquet_file}")

if __name__ == "__main__":
    main()