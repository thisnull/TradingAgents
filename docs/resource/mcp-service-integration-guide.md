# A-share Data MCP服务集成指南

## 🚀 服务概述

ashare-data MCP (Model Context Protocol) 服务是一个专业的中国股市数据分析平台，为AI Agent提供21个强大的金融数据工具。我们的服务采用SaaS模式部署，您无需自行搭建服务器，只需要连接我们提供的MCP端点即可获取全面的A股数据分析能力。

### 🌐 协议兼容性

**开放标准支持**：我们的MCP服务器完全基于 [Model Context Protocol](https://spec.modelcontextprotocol.io/) 开放标准构建，支持**任何兼容MCP协议的客户端**，包括但不限于：

- **Claude Desktop/Code** (Anthropic官方客户端)
- **Continue.dev** (开源AI代码助手)
- **Cody** (Sourcegraph AI助手)
- **Custom MCP Client** (自定义实现的MCP客户端)
- **其他第三方MCP兼容工具**

> 💡 **为什么重点介绍Claude？** 本文档详细介绍Claude Desktop和Claude Code配置，是因为它们目前是最成熟和广泛使用的MCP客户端，拥有最大的用户基础。但我们的服务器设计为协议无关，支持任何标准MCP实现。

### ✨ 核心价值

- **🎯 专业性**: 专注A股市场，数据覆盖全面且准确
- **⚡ 实时性**: T+1数据更新，确保信息时效性  
- **🔧 易用性**: 21个即用型工具，无需复杂配置
- **🤖 AI友好**: 原生支持MCP协议，完美集成各类AI Agent
- **📊 数据质量**: 99.9%准确率，多源验证确保数据可靠性

### 🛠️ 工具功能矩阵

| 功能模块 | 工具数量 | 主要能力 |
|---------|---------|----------|
| **股票基础数据** | 3个 | 股票信息查询、详情获取、市场筛选 |
| **市场行情** | 2个 | 日线行情、技术指标分析 |
| **财务分析** | 5个 | 财报查询、比率计算、趋势分析 |
| **指数数据** | 2个 | 指数信息、成分股查询 |
| **申万行业** | 4个 | 行业分类、成分股、层级查询、行业搜索 |
| **数据初始化** | 5个 | 数据同步、状态监控、批量处理 |

---

## 🎯 快速开始

### 第一步：获取连接信息

**服务端点信息**：
- **WebSocket URL**: `ws://your-server.com:8001`
- **协议版本**: MCP 2024-11-05
- **认证方式**: API Key (联系我们获取)

> 💡 **获取API Key**: 请发送邮件至 [contact@ashare-data.com](mailto:contact@ashare-data.com) 申请API访问权限

### 第二步：配置主流MCP客户端

#### Claude Desktop 配置

创建或编辑Claude Desktop配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ashare-data": {
      "command": "npx",
      "args": [
        "@anthropic-ai/mcp-client",
        "ws://your-server.com:8001"
      ],
      "env": {
        "ASHARE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Claude Code 配置

在您的项目根目录创建 `.claude_code_config.json`：

```json
{
  "mcp": {
    "servers": {
      "ashare-data": {
        "url": "ws://your-server.com:8001",
        "apiKey": "your-api-key-here",
        "timeout": 30000
      }
    }
  }
}
```

### 第三步：其他客户端配置

其他MCP兼容客户端的详细配置请参考下文 [其他MCP客户端集成](#🔧-其他mcp客户端集成) 部分。

### 第四步：验证连接

启动Claude Desktop或Claude Code后，尝试以下命令验证连接：

```
请帮我查询平安银行(000001)的基本信息
```

如果看到详细的股票信息返回，说明连接成功！

---

## 🔧 其他MCP客户端集成

### Continue.dev 集成

**Continue.dev** 是一个开源的AI代码助手，支持MCP协议。

在 `.continue/config.json` 中配置：

```json
{
  "models": [...],
  "contextProviders": [
    {
      "name": "mcp",
      "params": {
        "serverName": "ashare-data",
        "command": "npx",
        "args": [
          "@anthropic-ai/mcp-client",
          "ws://your-server.com:8001"
        ],
        "env": {
          "ASHARE_API_KEY": "your-api-key-here"
        }
      }
    }
  ]
}
```

### 自定义MCP客户端

对于自定义实现的MCP客户端，您需要：

**1. 建立WebSocket连接**：
```javascript
const ws = new WebSocket('ws://your-server.com:8001');
ws.onopen = () => {
  // 发送MCP初始化消息
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: {
        name: "custom-mcp-client",
        version: "1.0.0"
      }
    }
  }));
};
```

**2. 实现MCP协议**：
- 初始化握手
- 工具发现和调用
- 资源请求和响应
- 错误处理

**3. 认证配置**：
```javascript
// 在WebSocket头部或消息中包含API密钥
const authHeaders = {
  'Authorization': `Bearer ${process.env.ASHARE_API_KEY}`
};
```

### Cody (Sourcegraph) 集成

在 Cody 设置中添加 MCP 服务器：

```json
{
  "cody.experimental.mcp": {
    "servers": {
      "ashare-data": {
        "command": "npx",
        "args": [
          "@anthropic-ai/mcp-client", 
          "ws://your-server.com:8001"
        ],
        "env": {
          "ASHARE_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

### 通用连接参数

**所有MCP客户端都需要以下连接信息**：

| 参数 | 值 | 说明 |
|------|----|----- |
| **协议** | WebSocket | MCP标准传输协议 |
| **端点** | `ws://your-server.com:8001` | MCP服务器地址 |
| **协议版本** | `2024-11-05` | MCP协议版本 |
| **认证** | `ASHARE_API_KEY` | 环境变量或头部认证 |

**验证连接的标准方法**：

1. **初始化请求**：发送MCP `initialize` 方法
2. **工具列表**：调用 `tools/list` 获取可用工具  
3. **测试调用**：使用 `tools/call` 调用 `get_stock_detail` 工具

---

## 🔧 完整工具参考

### 📈 股票基础数据工具

#### 1. get_stocks - 股票列表查询
**功能**: 获取股票基础信息，支持筛选和分页

**参数**:
```json
{
  "symbols": ["000001", "000002"],     // 可选：股票代码列表
  "market": "main",                    // 可选：市场类型 (main/gem/star/bj)
  "status": "normal",                  // 可选：交易状态 (normal/suspend/delist)
  "limit": 10,                        // 可选：返回数量 (1-100)
  "offset": 0                         // 可选：分页偏移量
}
```

**使用示例**:
```
帮我查询创业板前20只股票的基本信息
```

#### 2. get_stock_detail - 股票详情查询
**功能**: 获取特定股票的详细信息

**参数**:
```json
{
  "symbol": "000001"                  // 必需：6位股票代码
}
```

**使用示例**:
```
查询平安银行(000001)的详细信息，包括上市时间、行业分类等
```

### 📊 市场行情工具

#### 3. get_daily_quotes - 日线行情查询
**功能**: 获取股票日线价格数据和估值指标

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "start_date": "2024-01-01",        // 可选：开始日期
  "end_date": "2024-12-31",          // 可选：结束日期
  "limit": 20,                       // 可选：返回数量 (1-500)
  "offset": 0                        // 可选：分页偏移量
}
```

**使用示例**:
```
获取贵州茅台(600519)最近30天的行情数据，包括PE、PB比率
```

#### 4. calculate_technical_indicators - 技术指标计算
**功能**: 计算各种技术分析指标

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "indicator": "ma",                  // 必需：指标类型 (ma/ema/rsi/macd/bollinger)
  "period": 20,                       // 可选：计算周期 (5-200)
  "start_date": "2024-01-01",        // 可选：开始日期
  "end_date": "2024-12-31"           // 可选：结束日期
}
```

**使用示例**:
```
计算比亚迪(002594)的20日移动平均线和MACD指标
```

### 💰 财务分析工具

#### 5. get_financial_reports - 财务报告查询
**功能**: 获取公司财务报表数据

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "report_type": "annual",            // 可选：报告类型 (annual/quarterly)
  "year": 2024,                       // 可选：报告年度
  "quarter": 3,                       // 可选：报告季度 (1-4)
  "limit": 5                          // 可选：返回数量 (1-20)
}
```

#### 6. get_latest_financial_reports - 最新财报查询
**功能**: 获取最新发布的财务报告

**参数**:
```json
{
  "symbols": ["000001", "000002"],    // 可选：股票代码列表
  "report_type": "A",                 // 可选：报告类型 (Q1/Q2/Q3/A)
  "limit": 20,                        // 可选：返回数量 (1-100)
  "offset": 0                         // 可选：分页偏移量
}
```

#### 7. get_financial_report_by_symbol - 特定财报查询
**功能**: 查询特定公司特定期间的财务报告

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "report_date": "2024-09-30",       // 必需：报告日期
  "report_type": "A"                  // 可选：报告类型 (Q1/Q2/Q3/A)
}
```

#### 8. get_financial_summary - 财务摘要
**功能**: 获取财务比率和关键指标摘要

**参数**:
```json
{
  "symbols": ["000001", "000002"],    // 可选：股票代码列表
  "report_date": "2024-09-30",       // 可选：报告日期
  "limit": 20,                        // 可选：返回数量 (1-100)
  "offset": 0                         // 可选：分页偏移量
}
```

#### 9. calculate_financial_ratios - 财务比率计算
**功能**: 计算各种财务分析比率

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "year": 2024,                       // 可选：计算年度
  "ratios": ["pe", "pb", "roe"]       // 可选：指定比率类型
}
```

### 📈 指数数据工具

#### 10. get_indices - 指数信息查询
**功能**: 获取股票指数基础信息

**参数**:
```json
{
  "index_codes": ["000001", "000300"], // 可选：指数代码列表
  "market_type": "主板",               // 可选：市场类型筛选
  "limit": 10,                         // 可选：返回数量 (1-50)
  "offset": 0                          // 可选：分页偏移量
}
```

#### 11. get_index_constituents - 指数成分股查询
**功能**: 获取指数的成分股列表

**参数**:
```json
{
  "index_code": "000300",             // 必需：指数代码
  "limit": 50,                        // 可选：返回数量 (1-1000)
  "offset": 0                         // 可选：分页偏移量
}
```

### 🏭 申万行业数据工具

#### 18. get_sw_industry_info - 申万行业信息查询
**功能**: 获取申万行业分类信息（支持一、二、三级）

**参数**:
```json
{
  "level": 1,                         // 必需：行业级别 (1/2/3)
  "industry_codes": ["801010"],       // 可选：行业代码列表
  "parent_codes": ["801010"],         // 可选：父级行业代码列表（二三级查询用）
  "status": "active",                 // 可选：状态筛选 (active/inactive)
  "limit": 50,                        // 可选：返回数量 (1-1000)
  "offset": 0                         // 可选：分页偏移量
}
```

**使用示例**:
```
查询申万一级行业中的金融相关行业分类
```

#### 19. get_sw_industry_constituents - 申万行业成分股查询
**功能**: 获取指定申万行业的成分股列表

**参数**:
```json
{
  "industry_codes": ["801010"],       // 必需：行业代码列表
  "levels": [1, 2],                   // 可选：行业级别筛选
  "status": "active",                 // 可选：成分股状态 (active/inactive)
  "limit": 100,                       // 可选：返回数量 (1-1000)
  "offset": 0                         // 可选：分页偏移量
}
```

**使用示例**:
```
获取申万银行业一级行业的所有成分股票
```

#### 20. get_stock_industry_hierarchy - 股票行业层级查询
**功能**: 查询特定股票在申万行业分类中的完整层级信息

**参数**:
```json
{
  "symbol": "000001"                  // 必需：6位股票代码
}
```

**使用示例**:
```
查询平安银行(000001)在申万行业分类中的一、二、三级行业归属
```

#### 21. analyze_industry_constituents - 行业成分股分析
**功能**: 分析申万行业成分股的统计信息和分布情况

**参数**:
```json
{
  "industry_codes": ["801010"],       // 可选：行业代码列表
  "levels": [1, 2, 3],                // 可选：分析的行业级别
  "analysis_type": "summary",         // 可选：分析类型 (summary/detailed)
  "include_inactive": false           // 可选：是否包含已退市股票
}
```

**使用示例**:
```
分析申万一级行业的成分股分布，包括各行业成分股数量、市值分布等统计信息
```

### 🔄 数据初始化工具

#### 22. initialize_stock_data - 单只股票数据初始化
**功能**: 初始化特定股票的全面数据

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码
  "start_date": "2024-01-01",        // 可选：开始日期
  "end_date": "2024-12-31",          // 可选：结束日期
  "force_update": false               // 可选：强制更新
}
```

#### 23. batch_initialize_stocks - 批量股票数据初始化
**功能**: 批量初始化多只股票数据

**参数**:
```json
{
  "symbols": ["000001", "000002"],    // 必需：股票代码列表 (最多10只)
  "start_date": "2024-01-01",        // 可选：开始日期
  "end_date": "2024-12-31",          // 可选：结束日期
  "force_update": false               // 可选：强制更新
}
```

#### 24. get_initialization_status - 初始化状态查询
**功能**: 查询数据初始化任务的进度

**参数**:
```json
{
  "request_id": "req_123456789"       // 必需：初始化请求ID
}
```

#### 25. check_rate_limit - 速率限制检查
**功能**: 检查特定股票的数据请求限制状态

**参数**:
```json
{
  "symbol": "000001"                  // 必需：股票代码
}
```

#### 26. cleanup_old_records - 清理旧记录
**功能**: 清理过期的初始化记录和速率限制数据

**参数**:
```json
{
  "hours_to_keep": 24,                // 可选：保留记录小时数 (1-168)
  "days_to_keep": 30                  // 可选：保留限制记录天数 (1-365)
}
```

### 📋 市场分析工具

#### 27. analyze_market_trend - 市场趋势分析
**功能**: 分析股票或指数的市场趋势

**参数**:
```json
{
  "symbol": "000001",                 // 必需：股票代码或指数代码
  "period": "1m",                     // 可选：分析周期 (1d/5d/1m/3m/6m/1y)
  "indicators": ["trend", "volatility"] // 可选：分析维度
}
```

---

## 💡 使用场景和示例

### 场景1：股票基本面分析

**目标**: 对某只股票进行全面的基本面分析

```
我想分析比亚迪(002594)的投资价值，请帮我：
1. 获取公司基本信息和行业分类
2. 查看最近一年的财务报表
3. 计算主要财务比率(PE、PB、ROE、负债率)
4. 分析最近3个月的股价走势
```

**AI Agent工作流**:
1. 调用 `get_stock_detail` 获取基本信息
2. 调用 `get_latest_financial_reports` 获取最新财报
3. 调用 `calculate_financial_ratios` 计算财务比率
4. 调用 `get_daily_quotes` 获取股价数据
5. 调用 `analyze_market_trend` 分析趋势

### 场景2：行业对比分析

**目标**: 对比同行业不同公司的财务表现

```
请帮我对比银行业三大巨头的财务表现：
平安银行(000001)、招商银行(600036)、中国银行(601988)
包括营收、净利润、ROE、不良贷款率等关键指标
```

**AI Agent工作流**:
1. 调用 `get_financial_summary` 批量获取财务摘要
2. 调用 `calculate_financial_ratios` 计算各项比率
3. 进行数据对比和分析

### 场景3：投资组合监控

**目标**: 监控投资组合中各股票的表现

```
我的投资组合包含以下股票，请帮我监控它们的表现：
贵州茅台(600519)、比亚迪(002594)、宁德时代(300750)
需要最新的股价、技术指标和财务状况
```

**AI Agent工作流**:
1. 调用 `batch_initialize_stocks` 确保数据最新
2. 调用 `get_daily_quotes` 获取最新行情
3. 调用 `calculate_technical_indicators` 计算技术指标
4. 调用 `get_latest_financial_reports` 获取财务更新

### 场景4：指数成分股分析

**目标**: 分析沪深300指数的成分股分布

```
请帮我分析沪深300指数(000300)：
1. 获取所有成分股列表
2. 按权重排序前20名成分股
3. 分析行业分布情况
```

**AI Agent工作流**:
1. 调用 `get_index_constituents` 获取成分股
2. 调用 `get_stocks` 批量获取股票信息
3. 进行数据分析和可视化

### 场景5：申万行业分析

**目标**: 深度分析申万行业分类和成分股分布

```
我想了解申万行业分类体系，请帮我：
1. 获取所有一级行业的分类和名称
2. 分析银行业的完整层级结构（一、二、三级）
3. 获取银行业所有成分股并按市值排序
4. 对比银行业与保险业的成分股数量和特征
```

**AI Agent工作流**:
1. 调用 `get_sw_industry_info` 获取一级行业列表
2. 调用 `get_sw_industry_info` 获取银行业各级分类
3. 调用 `get_sw_industry_constituents` 获取银行业成分股
4. 调用 `analyze_industry_constituents` 进行行业对比分析

### 场景6：股票行业归属分析

**目标**: 分析特定股票的行业归属和同业对比

```
请帮我分析以下几只股票的行业分类：
平安银行(000001)、招商银行(600036)、宁德时代(300750)
包括它们的申万行业三级分类和同行业其他股票
```

**AI Agent工作流**:
1. 调用 `get_stock_industry_hierarchy` 获取各股票行业层级
2. 调用 `get_sw_industry_constituents` 获取同行业股票
3. 进行行业集中度和竞争格局分析

---

## 📊 最佳实践

### 🚀 性能优化

1. **批量查询优化**
   ```
   # 优化前：逐一查询
   查询平安银行的信息
   查询招商银行的信息
   查询中国银行的信息
   
   # 优化后：批量查询
   批量查询银行股票：平安银行(000001)、招商银行(600036)、中国银行(601988)
   ```

2. **申万行业查询优化**
   ```
   # 推荐：先查询行业分类，再获取成分股
   查询申万银行业的行业代码和分类信息
   然后获取该行业下的所有成分股票
   
   # 推荐：使用层级查询了解股票行业归属
   查询平安银行(000001)的申万行业三级分类层级
   ```

3. **缓存策略**
   - 基础信息（股票列表、公司信息）：1小时缓存
   - 日线行情：30分钟缓存
   - 财务报表：1天缓存
   - 申万行业分类：24小时缓存（较稳定的分类数据）
   - 行业成分股：6小时缓存（定期调整的成分股）

4. **分页处理**
   ```
   # 大数据量查询使用分页
   获取A股所有股票，每页100条，显示前500条
   ```

### 🔍 数据质量保证

1. **数据验证**
   ```
   在分析茅台(600519)数据前，请先检查数据初始化状态和质量评分
   ```

2. **多源验证**
   ```
   对比不同时间段的财务数据，确保数据一致性
   ```

3. **异常处理**
   ```
   如果数据获取失败，请检查股票代码是否正确，或尝试重新初始化数据
   ```

4. **申万行业数据质量**
   ```
   检查申万行业分类的完整性，确认行业代码和名称匹配正确
   验证股票在各级行业中的归属一致性
   ```

### 📈 分析方法论

1. **趋势分析**
   ```
   分析股票时请结合多个时间维度：短期(1个月)、中期(3个月)、长期(1年)
   ```

2. **基本面分析**
   ```
   财务分析要包含盈利能力、偿债能力、营运能力、成长能力四个维度
   ```

3. **技术分析**
   ```
   技术指标建议组合使用：趋势指标(MA) + 震荡指标(RSI) + 成交量指标
   ```

4. **行业对比分析**
   ```
   使用申万行业分类进行同行业对比，分析公司在行业中的地位
   结合一、二、三级行业分类，进行多层次对比分析
   ```

---

## 🔧 故障排除

### 常见连接问题

#### 问题1：连接超时
**症状**: WebSocket连接建立失败
**解决方案**:
1. 检查网络连接
2. 验证服务端点URL是否正确
3. 确认防火墙没有阻止WebSocket连接
4. 联系技术支持检查服务状态

#### 问题2：认证失败
**症状**: 收到"认证失败"错误消息
**解决方案**:
1. 检查API Key是否正确配置
2. 确认API Key是否已过期
3. 验证环境变量设置是否正确

#### 问题3：工具调用失败
**症状**: 特定工具返回错误
**解决方案**:
1. 检查参数格式是否正确
2. 验证股票代码格式(6位数字)
3. 确认日期格式(YYYY-MM-DD)
4. 检查数值范围是否在允许范围内

### 错误代码说明

| 错误代码 | 错误类型 | 说明 | 解决方案 |
|---------|---------|------|----------|
| 1001 | 参数错误 | 请求参数格式不正确 | 检查参数格式和必需字段 |
| 1002 | 认证失败 | API Key无效或过期 | 更新API Key |
| 1003 | 数据不存在 | 请求的数据不存在 | 确认股票代码或日期范围 |
| 1004 | 速率限制 | 请求频率过高 | 降低请求频率或等待重试 |
| 1005 | 服务不可用 | 数据源暂时不可用 | 稍后重试或联系技术支持 |

### 性能监控

**服务状态检查**:
```
请检查当前ashare-data MCP服务的状态和可用工具列表
```

**数据质量监控**:
```
检查平安银行(000001)的数据质量评分和最后更新时间
```

---

## 📞 技术支持

### 联系方式

- **技术支持邮箱**: [support@ashare-data.com](mailto:support@ashare-data.com)
- **商务合作邮箱**: [business@ashare-data.com](mailto:business@ashare-data.com)
- **文档反馈**: [docs@ashare-data.com](mailto:docs@ashare-data.com)

### 支持时间

- **工作日**: 9:00 - 18:00 (北京时间)
- **紧急支持**: 24/7 (仅限生产环境问题)
- **响应时间**: 
  - 一般问题：4小时内回复
  - 紧急问题：1小时内回复

### 常用资源

- **API文档**: [https://docs.ashare-data.com/api](https://docs.ashare-data.com/api)
- **示例代码**: [https://github.com/ashare-data/examples](https://github.com/ashare-data/examples)
- **状态页面**: [https://status.ashare-data.com](https://status.ashare-data.com)
- **更新日志**: [https://changelog.ashare-data.com](https://changelog.ashare-data.com)

---

## 📋 附录

### MCP协议版本兼容性

| MCP版本 | 支持状态 | 最后支持版本 |
|---------|---------|-------------|
| 2024-11-05 | ✅ 完全支持 | 当前版本 |
| 2024-10-07 | ⚠️ 有限支持 | v1.2.0 |
| 2024-09-25 | ❌ 不支持 | v1.0.0 |

### 客户端兼容性说明

**✅ 完全兼容的MCP客户端**：
- Claude Desktop (Anthropic)
- Claude Code (Anthropic) 
- Continue.dev (开源AI代码助手)
- 自定义MCP实现

**🔄 理论兼容的客户端**（需要测试验证）：
- Cody (Sourcegraph)
- 其他实现MCP 2024-11-05标准的客户端

**📋 兼容性要求**：
任何客户端只要满足以下条件即可连接我们的MCP服务器：
1. 实现MCP协议2024-11-05版本
2. 支持WebSocket传输协议
3. 支持JSON-RPC 2.0消息格式
4. 能够处理工具调用和资源请求

> 💡 **开发者注意**：如果您正在开发新的MCP客户端或集成现有工具，请参考 [MCP官方规范](https://spec.modelcontextprotocol.io/) 来确保兼容性。如有集成问题，欢迎联系我们的技术支持。

### 数据更新时间表

| 数据类型 | 更新频率 | 更新时间 | 可用性SLA |
|---------|---------|----------|-----------|
| 股票基础信息 | 每日 | 6:00 AM | 99.9% |
| 日线行情 | 每日 | 7:00 AM | 99.9% |
| 财务报表 | 实时 | 发布后2小时内 | 99.5% |
| 指数数据 | 每日 | 7:30 AM | 99.9% |
| 技术指标 | 实时计算 | 请求时 | 99.9% |

### 服务等级协议(SLA)

- **可用性**: 99.9%月度可用性保证
- **响应时间**: 
  - P95响应时间 < 500ms
  - P99响应时间 < 1000ms
- **数据准确性**: 99.9%数据准确率保证
- **服务支持**: 工作日8小时技术支持
- **客户端兼容性**: 支持所有符合MCP标准的客户端

---

*文档版本: v2.2.0*  
*最后更新: 2025-08-15*  
*适用于: ashare-data MCP服务 v1.2.0+*  
*客户端支持: 所有MCP 2024-11-05兼容客户端*  
*新增功能: 申万行业数据分析工具 (4个工具)*