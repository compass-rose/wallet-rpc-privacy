from mitmproxy import http
import json

def response(flow: http.HTTPFlow):
    if "infura.io" in flow.request.pretty_host or "sepolia-faucet" in flow.request.pretty_host:
        with open("captured.jsonl", "a") as f:
            f.write(json.dumps({
                "method": flow.request.method,
                "url": flow.request.url,
                "request_body": flow.request.text,
                "response_body": flow.response.text if flow.response else None,
                "timestamp": flow.request.timestamp_start
            }) + "\n")