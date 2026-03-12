# 系统使用步骤（Dashboard 操作）

在后端服务已经运行的情况下，可以通过前端 Dashboard 进行系统监测与分析。

---

## 一、启动前端

进入 frontend 目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

浏览器打开：

```
http://localhost:5173
```

进入系统 Dashboard 页面。

---

## 二、查看系统状态

Dashboard 顶部会显示系统统计信息：

- **Active Sessions**：当前正在运行的检测会话  
- **Total Sessions**：历史检测会话总数  
- **Today's Packets**：今日捕获的网络数据包数量  
- **Today's Leaks**：今日检测到的隐私泄露事件数量  

这些数据由后端接口自动更新。

---

## 三、查看系统监控状态

在 **Current Monitor Status** 模块可以查看：

- **Capturing**：当前是否正在捕获流量  
- **Capture Rate**：当前流量捕获速度  
- **Last Capture Time**：最近一次捕获时间  
- **Metadata Time**：风险评估更新时间  

---

## 四、查看风险评估

在 **Risk Metrics** 模块可以查看系统风险分析结果：

- **Current Risk**：当前系统风险等级  
- **Average Risk Score**：平均风险评分  
- **High Risk Sessions**：高风险会话数量  
- **Trend**：风险变化趋势  

---

## 五、查看实时隐私泄露事件

在 **Real-time Leak Stream** 模块可以看到系统检测到的隐私泄露事件，例如：

- 身份泄露（Identity Leak）  
- 地址关联分析  
- 网络指纹识别  

每条记录包含：

- 泄露类型  
- RPC 方法  
- 置信度  
- 检测规则说明  
- 事件时间  

---

## 六、查看时间线分析

在 **Timeline Report** 模块可以查看系统事件时间线，包括：

- session 创建  
- RPC 调用行为  
- 隐私泄露检测  
- 风险评估事件  

该模块可以帮助分析用户行为模式。

---

## 七、查看热力图分析

在 **Heatmap Report** 模块可以查看 RPC 使用模式。

可以通过顶部下拉菜单选择不同分析方式：

- **timeofday**：不同时间段请求分布  
- **method_frequency**：RPC 方法调用频率  
- **dayofweek**：不同星期的调用情况  

---

## 八、查看统计图表

Dashboard 提供多种统计图：

### Privacy Leak Events Over Time

展示隐私泄露事件随时间变化趋势。

### Risk Level Distribution

展示不同风险等级的分布比例。

### Network Traffic Volume

展示网络请求数量统计。

### RPC Response Time Latency

展示 RPC 请求响应时间变化。

---

## 九、生成分析报告

点击页面右上角：

```
Generate Report
```

系统会生成 **Comprehensive Report**。

报告内容包括：

- 流量统计  
- 隐私泄露检测结果  
- 风险评估分析  

---

## 十、刷新数据

点击：

```
Refresh
```

可以重新从后端加载最新数据。
