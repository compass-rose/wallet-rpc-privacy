# Getting Started & Deployment Guide

## English Version

### 1. Prerequisites
* **Python**: 3.10 or higher.
* **Environment**: A terminal with `pip` access.

### 2. Installation
```bash
# Install required libraries
pip install fastapi uvicorn pydantic
3. Running the Engine
Execute the following command to start the FastAPI server:

Bash
uvicorn app.main:app --reload --port 8778
4. Processing Output.json
Navigate to http://localhost:8778/docs.

Use the POST /api/v1/upload endpoint to upload your output.json file.

The engine will automatically handle nested fields and return a severity_score along with an anonymized report.

启动与部署指南
中文版
1. 前提条件
Python: 3.10 或更高版本。

环境: 具备 pip 权限的终端。

2. 安装步骤
Bash
# 安装所需库
pip install fastapi uvicorn pydantic
3. 运行引擎
执行以下命令启动 FastAPI 服务器：

Bash
uvicorn app.main:app --reload --port 8778
4. 处理 Output.json
访问 http://localhost:8778/docs。

使用 POST /api/v1/upload 接口上传您的 output.json 文件。

引擎将自动处理嵌套字段，并返回“严重性得分”以及匿名化后的报告。


---

### 📊 汇总说明 (Final Summary)



| 文件名 | 内容描述 | 目标读者 |
| :--- | :--- | :--- |
| **README.md** | 项目整体介绍、核心功能及 10 条检测规则概览。 | 所有人员 |
| **TECHNICAL_SPEC.md** | 详细说明 M2 评分公式、递归解析原理及 PR-2 匿名化算法。 | 评审与技术人员 |
| **GETTING_STARTED.md** | 包含环境配置、安装命令及 API 调用流程。 | 部署与测试人员