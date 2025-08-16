# A股数据同步服务 API 用户指南

## 概述

A股数据同步服务 API 是一个企业级的金融数据 RESTful API 服务，提供全面的A股市场数据查询功能，支持AI Agent集成。基于 FastAPI 框架构建，提供高性能、稳定可靠的金融数据访问接口。

### 服务特性

- **企业级架构**：高可用、高性能的微服务架构
- **RESTful 设计**：遵循 REST 原则，接口设计规范统一
- **数据完整性**：涵盖股票基础信息、行情数据、财务报表、指数数据等
- **实时缓存**：多级缓存策略，确保响应速度
- **质量保证**：内置数据质量监控和验证机制
- **AI 友好**：支持 MCP (Model Context Protocol) 集成

### API 版本信息

- **当前版本**：v1.1.0
- **基础 URL**：`http://localhost:8000/api/v1`
- **协议**：HTTP/HTTPS
- **数据格式**：JSON
- **字符编码**：UTF-8

## 快速开始

### 环境要求

- 服务运行环境：Python 3.12+
- 客户端：支持 HTTP 请求的任何编程语言或工具
- 推荐工具：curl、Postman、HTTPie 等

### 基础配置

#### 服务启动

```bash
# 使用 uv 启动开发服务器
uv run python -m ashare_data.cli.main server --env=development

# 或使用 Docker Compose
docker compose up -d

# 服务默认运行在 http://localhost:8000
```

#### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/

# 检查 API 状态
curl http://localhost:8000/api/v1/health
```

## 认证和授权

### 当前版本认证

当前 v1.0.0 版本为开发测试版本，**暂未启用认证机制**。所有 API 端点均可直接访问。

### 未来版本认证（规划中）

```http
# JWT Token 认证（未来版本）
Authorization: Bearer <your-jwt-token>

# API Key 认证（未来版本）
X-API-Key: <your-api-key>
```

## API 端点详细说明

### 1. 系统管理端点

#### 1.1 根路径健康检查

**端点**：`GET /`

**描述**：检查服务整体运行状态

**示例请求**：
```bash
curl -X GET "http://localhost:8000/"
```

**响应示例**：
```json
{
  "service": "A-share Data API",
  "version": "1.0.0",
  "status": "healthy",
  "message": "A股数据同步服务API正常运行"
}
```

#### 1.2 API 健康检查

**端点**：`GET /api/v1/health`

**描述**：检查 API v1 版本运行状态

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**响应示例**：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "A-share Data API v1"
}
```

### 2. 市场数据端点 (Market Data)

#### 2.1 获取股票基础信息列表

**端点**：`GET /api/v1/market/basic`

**描述**：获取股票基础信息，支持多种筛选条件

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | string | 否 | - | 股票代码列表，逗号分隔 | `000001,000002` |
| `market` | string | 否 | - | 市场类型：main/gem/star/bj | `main` |
| `status` | string | 否 | `normal` | 交易状态：normal/suspend/delist | `normal` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `50` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取前50只主板正常交易股票
curl -X GET "http://localhost:8000/api/v1/market/basic?market=main&status=normal&limit=50"

# 查询特定股票
curl -X GET "http://localhost:8000/api/v1/market/basic?symbols=000001,000002,600000"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Stocks retrieved successfully",
  "data": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "market": "main",
      "exchange": "SZE",
      "industry": "J 金融业",
      "industry_code": "None",
      "listing_date": "1991-04-03",
      "delist_date": null,
      "is_st": false,
      "total_shares": 19405918198,
      "float_shares": 19405600653,
      "free_shares": null,
      "status": "normal",
      "data_source": "akshare",
      "created_at": "2025-08-07T11:13:46.937331",
      "updated_at": "2025-08-12T11:03:59.487309",
      "last_sync": "2025-08-12T11:03:58.788729"
    }
  ],
  "pagination": {
    "total": 5423,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 2.2 获取单只股票详情

**端点**：`GET /api/v1/market/{symbol}`

**描述**：根据股票代码获取单只股票的详细信息

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/market/000001"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Stock retrieved successfully",
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "market": "main",
    "exchange": "SZE",
    "industry": "J 金融业",
    "industry_code": "None",
    "listing_date": "1991-04-03",
    "delist_date": null,
    "is_st": false,
    "total_shares": 19405918198,
    "float_shares": 19405600653,
    "free_shares": null,
    "status": "normal",
    "data_source": "akshare",
    "created_at": "2025-08-07T11:13:46.937331",
    "updated_at": "2025-08-12T11:03:59.487309",
    "last_sync": "2025-08-12T11:03:58.788729"
  }
}
```

#### 2.3 获取日线行情数据

**端点**：`GET /api/v1/market/quotes/daily`

**描述**：获取股票日线行情数据，支持按股票代码和日期范围筛选

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | string | 否 | - | 股票代码列表，逗号分隔 | `000001,000002` |
| `start_date` | string | 否 | - | 开始日期 (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | string | 否 | - | 结束日期 (YYYY-MM-DD) | `2024-12-31` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取平安银行最近100个交易日行情
curl -X GET "http://localhost:8000/api/v1/market/quotes/daily?symbols=000001&limit=100"

# 获取特定日期范围的行情数据
curl -X GET "http://localhost:8000/api/v1/market/quotes/daily?symbols=000001&start_date=2024-01-01&end_date=2024-03-31"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Daily quotes retrieved successfully",
  "data": [],
  "pagination": {
    "total": 0,
    "limit": 100,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

> 📝 **数据说明**: 当前系统中日线行情数据为空，但端点功能正常。在有数据时，响应格式将包含完整的OHLCV数据、技术指标和市场指标。

#### 2.4 获取指数基础信息

**端点**：`GET /api/v1/market/indices`

**描述**：获取指数基础信息列表，支持通过指数代码、市场类型等条件筛选

> ✅ **状态更新**: 此端点现已正常工作，之前提到的路由优先级问题已解决。

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `index_codes` | string | 否 | - | 指数代码列表，逗号分隔 | `000001,000300` |
| `market` | string | 否 | - | 市场类型：SSE/SZE/CSI/OTHER | `SSE` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取上交所活跃指数
curl -X GET "http://localhost:8000/api/v1/market/indices?market=SSE&status=active"

# 查询特定指数
curl -X GET "http://localhost:8000/api/v1/market/indices?index_codes=000001,000300,000905"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Indices retrieved successfully",
  "data": [
    {
      "index_code": "000001",
      "index_name": "上证指数",
      "market": "SSE",
      "status": "active",
      "avg_daily_turnover": "713569731141.50",
      "market_rank": 130,
      "activity_level": "high",
      "is_broad_based": true,
      "is_sector_specific": false,
      "is_size_based": false,
      "data_source": "akshare",
      "created_at": "2025-08-09T09:42:01.526931",
      "updated_at": "2025-08-09T16:46:32.644358",
      "last_sync": "2025-08-09T16:46:32.588389"
    }
  ],
  "pagination": {
    "total": 268,
    "limit": 100,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 2.5 获取指数成分股

**端点**：`GET /api/v1/market/indices/{index_code}/constituents`

**描述**：获取指定指数的成分股列表

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `index_code` | string | 是 | 指数代码 | `000300` |

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `effective_date` | string | 否 | - | 生效日期 (YYYY-MM-DD) | `2024-08-12` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取沪深300指数成分股
curl -X GET "http://localhost:8000/api/v1/market/indices/000300/constituents"

# 获取特定日期的成分股构成
curl -X GET "http://localhost:8000/api/v1/market/indices/000300/constituents?effective_date=2024-06-30"
```

#### 2.6 批量获取指数成分股

**端点**：`GET /api/v1/market/indices/constituents`

**描述**：批量获取多个指数的成分股列表

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `index_codes` | string | 是 | - | 指数代码列表，逗号分隔 | `000300,000905` |
| `effective_date` | string | 否 | - | 生效日期 (YYYY-MM-DD) | `2024-08-12` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 批量获取多个指数成分股
curl -X GET "http://localhost:8000/api/v1/market/indices/constituents?index_codes=000300,000905,000821"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Index 000300 constituents retrieved successfully",
  "data": [],
  "pagination": {
    "total": 0,
    "limit": 100,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

> 📝 **数据说明**: 当前系统中指数成分股数据为空，但端点功能正常。在有数据时，响应将包含成分股代码、权重、股数等完整信息。

### 5. 申万行业数据端点 (SW Industries)

#### 5.1 获取一级行业信息

**端点**：`GET /api/v1/sw-industries/first`

**描述**：获取申万一级行业分类信息列表

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `industry_codes` | string | 否 | - | 行业代码列表，逗号分隔 | `801010,801020` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取所有一级行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/first"

# 查询特定行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/first?industry_codes=801010,801020"
```

**响应示例**：
```json
{
  "success": true,
  "message": "SW first-level industries retrieved successfully",
  "data": [
    {
      "industry_code": "801010",
      "industry_name": "农林牧渔",
      "level": 1,
      "parent_code": null,
      "status": "active",
      "is_active": true,
      "data_source": "akshare",
      "created_at": "2025-08-15T08:30:00Z",
      "updated_at": "2025-08-15T08:30:00Z",
      "last_sync": "2025-08-15T08:30:00Z"
    }
  ],
  "pagination": {
    "total": 31,
    "limit": 100,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

#### 5.2 获取二级行业信息

**端点**：`GET /api/v1/sw-industries/second`

**描述**：获取申万二级行业分类信息列表

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `industry_codes` | string | 否 | - | 行业代码列表，逗号分隔 | `801011,801012` |
| `parent_codes` | string | 否 | - | 一级行业代码列表，逗号分隔 | `801010,801020` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取所有二级行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/second"

# 获取农林牧渔下的二级行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/second?parent_codes=801010"
```

#### 5.3 获取三级行业信息

**端点**：`GET /api/v1/sw-industries/third`

**描述**：获取申万三级行业分类信息列表

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `industry_codes` | string | 否 | - | 行业代码列表，逗号分隔 | `801011001,801011002` |
| `parent_codes` | string | 否 | - | 二级行业代码列表，逗号分隔 | `801011,801012` |
| `status` | string | 否 | `active` | 状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取所有三级行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/third"

# 获取特定二级行业下的三级行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/third?parent_codes=801011"
```

#### 5.4 获取特定行业成分股

**端点**：`GET /api/v1/sw-industries/{industry_code}/constituents`

**描述**：获取指定申万行业的成分股列表

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `industry_code` | string | 是 | 申万行业代码 | `801010` |

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `status` | string | 否 | `active` | 成分股状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取农林牧渔行业成分股
curl -X GET "http://localhost:8000/api/v1/sw-industries/801010/constituents"

# 获取特定状态的成分股
curl -X GET "http://localhost:8000/api/v1/sw-industries/801010/constituents?status=active&limit=50"
```

**响应示例**：
```json
{
  "success": true,
  "message": "SW industry constituents retrieved successfully",
  "data": [
    {
      "symbol": "000061",
      "industry_code": "801010",
      "industry_name": "农林牧渔",
      "level": 1,
      "status": "active",
      "is_active": true,
      "data_source": "akshare",
      "created_at": "2025-08-15T08:30:00Z",
      "updated_at": "2025-08-15T08:30:00Z",
      "last_sync": "2025-08-15T08:30:00Z"
    }
  ],
  "pagination": {
    "total": 87,
    "limit": 100,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

#### 5.5 批量获取行业成分股

**端点**：`GET /api/v1/sw-industries/constituents`

**描述**：批量获取多个申万行业的成分股列表

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `industry_codes` | string | 是 | - | 行业代码列表，逗号分隔 | `801010,801020` |
| `levels` | string | 否 | - | 行业级别列表，逗号分隔 | `1,2,3` |
| `status` | string | 否 | `active` | 成分股状态：active/inactive | `active` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 批量获取多个行业成分股
curl -X GET "http://localhost:8000/api/v1/sw-industries/constituents?industry_codes=801010,801020"

# 获取一级行业成分股
curl -X GET "http://localhost:8000/api/v1/sw-industries/constituents?industry_codes=801010,801020&levels=1"
```

#### 5.6 行业成分股分析

**端点**：`GET /api/v1/sw-industries/constituents/analysis`

**描述**：对申万行业成分股进行统计分析，包括市值分布、成分股数量等

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `industry_codes` | string | 否 | - | 行业代码列表，逗号分隔 | `801010,801020` |
| `levels` | string | 否 | `1,2,3` | 行业级别列表，逗号分隔 | `1,2` |
| `analysis_type` | string | 否 | `summary` | 分析类型：summary/detailed | `summary` |

**示例请求**：
```bash
# 分析所有行业成分股分布
curl -X GET "http://localhost:8000/api/v1/sw-industries/constituents/analysis"

# 分析特定行业成分股
curl -X GET "http://localhost:8000/api/v1/sw-industries/constituents/analysis?industry_codes=801010&analysis_type=detailed"
```

**响应示例**：
```json
{
  "success": true,
  "message": "SW industry constituents analysis completed",
  "data": {
    "total_industries": 2,
    "total_constituents": 156,
    "analysis_date": "2025-08-15",
    "industry_breakdown": [
      {
        "industry_code": "801010",
        "industry_name": "农林牧渔",
        "level": 1,
        "constituent_count": 87,
        "active_count": 85,
        "inactive_count": 2
      }
    ],
    "summary_statistics": {
      "avg_constituents_per_industry": 78.0,
      "max_constituents": 87,
      "min_constituents": 69,
      "active_rate": 0.987
    }
  }
}
```

#### 5.7 股票行业层级查询

**端点**：`GET /api/v1/sw-industries/hierarchy/{symbol}`

**描述**：查询特定股票在申万行业分类中的完整层级信息

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**示例请求**：
```bash
# 查询平安银行的行业层级
curl -X GET "http://localhost:8000/api/v1/sw-industries/hierarchy/000001"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Stock industry hierarchy retrieved successfully",
  "data": {
    "symbol": "000001",
    "hierarchy": {
      "level_1": {
        "industry_code": "801780",
        "industry_name": "银行",
        "level": 1
      },
      "level_2": {
        "industry_code": "801780",
        "industry_name": "银行",
        "level": 2,
        "parent_code": "801780"
      },
      "level_3": {
        "industry_code": "801780001",
        "industry_name": "银行",
        "level": 3,
        "parent_code": "801780"
      }
    },
    "data_source": "akshare",
    "last_sync": "2025-08-15T08:30:00Z"
  }
}
```

#### 5.8 行业代码/名称搜索

**端点**：`GET /api/v1/sw-industries/search`

**描述**：根据关键词搜索申万行业代码和名称

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `keyword` | string | 是 | - | 搜索关键词（行业名称或代码） | `银行` |
| `levels` | string | 否 | `1,2,3` | 搜索的行业级别 | `1,2` |
| `exact_match` | boolean | 否 | `false` | 是否精确匹配 | `false` |
| `limit` | integer | 否 | `20` | 每页大小 (1-100) | `20` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 搜索银行相关行业
curl -X GET "http://localhost:8000/api/v1/sw-industries/search?keyword=银行"

# 精确匹配搜索
curl -X GET "http://localhost:8000/api/v1/sw-industries/search?keyword=801780&exact_match=true"

# 按级别搜索
curl -X GET "http://localhost:8000/api/v1/sw-industries/search?keyword=金融&levels=1,2"
```

**响应示例**：
```json
{
  "success": true,
  "message": "SW industries search completed",
  "data": [
    {
      "industry_code": "801780",
      "industry_name": "银行",
      "level": 1,
      "parent_code": null,
      "status": "active",
      "is_active": true,
      "match_score": 1.0,
      "match_field": "industry_name"
    }
  ],
  "search_info": {
    "keyword": "银行",
    "total_matches": 3,
    "search_time_ms": 15
  },
  "pagination": {
    "total": 3,
    "limit": 20,
    "offset": 0,
    "has_next": false,
    "has_prev": false
  }
}
```

### 3. 股票数据初始化端点 (Stock Data Initialization)

#### 3.1 初始化股票数据

**端点**：`POST /api/v1/initialization/stocks/{symbol}/initialize`

**描述**：为指定股票初始化所有相关数据表，支持异步处理和速率限制

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**请求体**：
```json
{
  "symbol": "000001",
  "start_date": "1970-01-01",
  "end_date": "2025-08-14",
  "force_update": false
}
```

**请求参数说明**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbol` | string | 是 | - | 股票代码（需与路径参数一致） | `000001` |
| `start_date` | string | 否 | `1970-01-01` | 开始日期 (YYYY-MM-DD) | `2020-01-01` |
| `end_date` | string | 否 | 今天 | 结束日期 (YYYY-MM-DD) | `2024-12-31` |
| `force_update` | boolean | 否 | `false` | 是否忽略速率限制 | `true` |

**示例请求**：
```bash
curl -X POST "http://localhost:8000/api/v1/initialization/stocks/000001/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "force_update": false
  }'
```

**响应示例**：
```json
{
  "success": true,
  "message": "股票数据初始化请求已接受",
  "request_id": "req_20250814_123456_000001",
  "symbol": "000001",
  "overall_status": "pending",
  "estimated_completion_time": "2025-08-14T12:45:00Z",
  "data_types": [
    "daily_quotes",
    "financial_reports", 
    "money_flow",
    "management_stock_changes",
    "shareholder_stock_changes"
  ],
  "rate_limit_info": {
    "is_rate_limited": false,
    "next_allowed_time": null,
    "remaining_hours": 0
  }
}
```

#### 3.2 查询初始化状态

**端点**：`GET /api/v1/initialization/status/{request_id}`

**描述**：查询股票数据初始化的实时状态和进度

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `request_id` | string | 是 | 初始化请求ID | `req_20250814_123456_000001` |

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/initialization/status/req_20250814_123456_000001"
```

**响应示例**：
```json
{
  "success": true,
  "request_id": "req_20250814_123456_000001",
  "symbol": "000001",
  "overall_status": "processing",
  "progress_percentage": 65.0,
  "estimated_completion_time": "2025-08-14T12:45:00Z",
  "started_at": "2025-08-14T12:30:00Z",
  "data_type_status": {
    "daily_quotes": {
      "status": "completed",
      "records_processed": 4352,
      "records_stored": 4352,
      "data_quality_score": 98.5,
      "completion_time": "2025-08-14T12:35:00Z"
    },
    "financial_reports": {
      "status": "processing",
      "records_processed": 89,
      "records_stored": 87,
      "data_quality_score": 95.2,
      "completion_time": null
    }
  }
}
```

#### 3.3 查询速率限制状态

**端点**：`GET /api/v1/initialization/stocks/{symbol}/rate-limit`

**描述**：查询指定股票的速率限制状态

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/initialization/stocks/000001/rate-limit"
```

**响应示例**：
```json
{
  "symbol": "000001",
  "last_update_time": "2025-08-14T04:30:00Z",
  "next_allowed_time": "2025-08-14T12:30:00Z",
  "is_rate_limited": true,
  "remaining_hours": 7.5
}
```

#### 3.4 批量初始化股票数据

**端点**：`POST /api/v1/initialization/stocks/batch/initialize`

**描述**：批量初始化多个股票的数据，最多同时处理10个股票

**请求体**：
```json
{
  "symbols": ["000001", "000002", "600000"],
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "force_update": false
}
```

**请求参数说明**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | array | 是 | - | 股票代码列表（最多10个） | `["000001","000002"]` |
| `start_date` | string | 否 | `1970-01-01` | 开始日期 | `2020-01-01` |
| `end_date` | string | 否 | 今天 | 结束日期 | `2024-12-31` |
| `force_update` | boolean | 否 | `false` | 是否忽略速率限制 | `false` |

**示例请求**：
```bash
curl -X POST "http://localhost:8000/api/v1/initialization/stocks/batch/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["000001", "000002", "600000"],
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "force_update": false
  }'
```

**响应示例**：
```json
{
  "success": true,
  "batch_id": "batch_2_1_20250814_123456",
  "total_symbols": 3,
  "accepted_symbols": ["000001", "600000"],
  "rejected_symbols": {
    "000002": "受到速率限制，剩余 7.5 小时"
  },
  "individual_requests": {
    "000001": "req_20250814_123456_000001",
    "600000": "req_20250814_123457_600000"
  },
  "message": "批量请求处理完成：2 个接受，1 个拒绝"
}
```

#### 3.5 清理过期记录

**端点**：`DELETE /api/v1/initialization/cleanup`

**描述**：清理过期的初始化记录和速率限制缓存

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `hours_to_keep` | integer | 否 | `24` | 保留多少小时的初始化记录 | `48` |
| `days_to_keep` | integer | 否 | `30` | 保留多少天的速率限制记录 | `7` |

**示例请求**：
```bash
curl -X DELETE "http://localhost:8000/api/v1/initialization/cleanup?hours_to_keep=48&days_to_keep=7"
```

**响应示例**：
```json
{
  "cleaned_requests": 15,
  "cleaned_rate_limits": 8,
  "total_cleaned": 23
}
```

### 4. 申万行业数据使用说明

#### 数据特点

**申万行业分类体系**：
- **一级行业**：31个大类，如农林牧渔、采掘、钢铁等
- **二级行业**：104个中类，在一级行业基础上细分
- **三级行业**：227个小类，最详细的行业分类
- **成分股数据**：每个行业包含的股票列表，支持动态更新

**错误处理说明**：

| 错误场景 | HTTP状态码 | 错误信息 | 解决方案 |
|---------|-----------|----------|----------|
| 行业代码不存在 | 404 | Industry code not found | 检查行业代码格式和有效性 |
| 股票代码格式错误 | 400 | Invalid stock symbol format | 使用6位数字股票代码 |
| 参数验证失败 | 422 | Validation error | 检查参数类型和值范围 |
| 无权限访问 | 403 | Access denied | 检查API认证信息 |

**最佳实践建议**：

1. **层级查询策略**
   ```bash
   # 推荐：先查询上级行业，再查询下级
   curl -X GET "http://localhost:8000/api/v1/sw-industries/first?industry_codes=801010"
   curl -X GET "http://localhost:8000/api/v1/sw-industries/second?parent_codes=801010"
   ```

2. **批量查询优化**
   ```bash
   # 优化：一次请求多个行业的成分股
   curl -X GET "http://localhost:8000/api/v1/sw-industries/constituents?industry_codes=801010,801020,801030"
   ```

3. **搜索功能使用**
   ```bash
   # 模糊搜索：找到相关行业
   curl -X GET "http://localhost:8000/api/v1/sw-industries/search?keyword=新能源"
   
   # 精确搜索：确认具体行业代码
   curl -X GET "http://localhost:8000/api/v1/sw-industries/search?keyword=801010&exact_match=true"
   ```

### 6. 财务数据端点 (Financial Data)

#### 6.1 获取财务报表数据

**端点**：`GET /api/v1/financial/reports`

**描述**：获取财务报表数据列表，支持多种筛选条件

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | string | 否 | - | 股票代码列表，逗号分隔 | `000001,000002` |
| `report_type` | string | 否 | - | 报告类型：Q1/Q2/Q3/A | `A` |
| `start_date` | string | 否 | - | 报告期开始日期 (YYYY-MM-DD) | `2023-01-01` |
| `end_date` | string | 否 | - | 报告期结束日期 (YYYY-MM-DD) | `2023-12-31` |
| `announce_start_date` | string | 否 | - | 公告开始日期 (YYYY-MM-DD) | `2024-01-01` |
| `announce_end_date` | string | 否 | - | 公告结束日期 (YYYY-MM-DD) | `2024-04-30` |
| `min_revenue` | decimal | 否 | - | 最小营业收入（万元） | `1000000` |
| `max_revenue` | decimal | 否 | - | 最大营业收入（万元） | `10000000` |
| `min_net_profit` | decimal | 否 | - | 最小净利润（万元） | `100000` |
| `max_net_profit` | decimal | 否 | - | 最大净利润（万元） | `1000000` |
| `min_roe` | decimal | 否 | - | 最小净资产收益率（%） | `5.0` |
| `max_roe` | decimal | 否 | - | 最大净资产收益率（%） | `30.0` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取平安银行2023年年报
curl -X GET "http://localhost:8000/api/v1/financial/reports?symbols=000001&report_type=A&start_date=2023-01-01&end_date=2023-12-31"

# 筛选高ROE企业年报
curl -X GET "http://localhost:8000/api/v1/financial/reports?report_type=A&min_roe=15.0&start_date=2023-01-01&end_date=2023-12-31"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Financial reports retrieved successfully",
  "data": [
    {
      "id": 3203,
      "symbol": "000001",
      "report_date": "2025-03-31",
      "report_type": "Q1",
      "announce_date": null,
      "total_revenue": "33709000000.00",
      "operating_revenue": "33709000000.00",
      "total_cost": null,
      "operating_cost": "9369000000.00",
      "gross_profit": "24339999756.15",
      "operating_profit": "16909999845.96",
      "total_profit": null,
      "net_profit": "14096000000.00",
      "net_profit_attributable": "14096000000.00",
      "net_profit_after_nrgal": "14043000000.00",
      "total_assets": "6787200804864.00",
      "total_current_assets": "3393600402432.00",
      "total_non_current_assets": "3393600402432.00",
      "total_liabilities": "6281088804864.00",
      "total_current_liabilities": "2512435521945.60",
      "total_non_current_liabilities": "3768653282918.40",
      "total_equity": "506112000000.00",
      "net_cash_flow_from_operating": "162946000000.00",
      "net_cash_flow_from_investing": "-40736500000.00",
      "net_cash_flow_from_financing": "8147300000.00",
      "net_cash_flow": "130356800000.00",
      "gross_profit_margin": "0.7221",
      "net_profit_margin": "0.4182",
      "roa": "0.2077",
      "roe": "0.0280",
      "debt_to_asset_ratio": "0.9124",
      "current_ratio": "1.3507",
      "quick_ratio": null,
      "conservative_quick_ratio": null,
      "eps": "0.6200",
      "bps": "22.4755",
      "udpps": "13.1723",
      "ocfps": "8.3967",
      "data_source": "akshare",
      "data_quality": "enhanced",
      "created_at": "2025-08-08T12:45:56.174586",
      "updated_at": "2025-08-08T12:45:56.255687",
      "last_sync": "2025-08-08T12:45:56.138849"
    }
  ],
  "pagination": {
    "total": 189,
    "limit": 100,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 6.2 获取单只股票财务报表

**端点**：`GET /api/v1/financial/reports/{symbol}`

**描述**：根据股票代码和报告期获取单个财务报表的详细信息

> ⚠️ **注意**: 此端点目前存在数据库查询问题（日期字段类型匹配错误），建议使用上述列表查询端点进行筛选。

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `report_date` | string | 是 | - | 报告期 (YYYY-MM-DD) | `2023-12-31` |
| `report_type` | string | 否 | `A` | 报告类型：Q1/Q2/Q3/A | `A` |

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/financial/reports/000001?report_date=2023-12-31&report_type=A"
```

#### 6.3 获取最新财务报表

**端点**：`GET /api/v1/financial/reports/latest`

**描述**：获取股票的最新财务报表数据

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | string | 否 | - | 股票代码列表，逗号分隔 | `000001,000002` |
| `report_type` | string | 否 | `A` | 报告类型：Q1/Q2/Q3/A | `A` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取平安银行最新年报
curl -X GET "http://localhost:8000/api/v1/financial/reports/latest?symbols=000001&report_type=A"

# 获取所有股票最新季报（前100条）
curl -X GET "http://localhost:8000/api/v1/financial/reports/latest?report_type=Q3&limit=100"
```

#### 6.4 获取财务比率数据

**端点**：`GET /api/v1/financial/ratios`

**描述**：获取财务比率数据，包含盈利能力、偿债能力、每股指标等

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `symbols` | string | 否 | - | 股票代码列表，逗号分隔 | `000001,000002` |
| `report_date` | string | 否 | - | 报告期 (YYYY-MM-DD) | `2023-12-31` |
| `limit` | integer | 否 | `100` | 每页大小 (1-1000) | `100` |
| `offset` | integer | 否 | `0` | 偏移量 | `0` |

**示例请求**：
```bash
# 获取平安银行财务比率
curl -X GET "http://localhost:8000/api/v1/financial/ratios?symbols=000001"

# 获取2023年所有股票财务比率
curl -X GET "http://localhost:8000/api/v1/financial/ratios?report_date=2023-12-31"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Financial ratios retrieved successfully",
  "data": [
    {
      "symbol": "000001",
      "report_date": "2023-12-31",
      "gross_profit_margin": "44.28",
      "net_profit_margin": "20.55",
      "roa": "0.78",
      "roe": "9.48",
      "debt_to_asset_ratio": "91.75",
      "current_ratio": "0.64",
      "quick_ratio": "0.64",
      "eps": "1.87",
      "bps": "19.71",
      "ocfps": "1.47"
    }
  ],
  "pagination": {
    "total": 5247,
    "limit": 100,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 6.5 获取股票财务摘要

**端点**：`GET /api/v1/financial/summary/{symbol}`

**描述**：获取股票的财务摘要信息，包含最新财务指标、同比增长率、历史趋势等

**路径参数**：
| 参数 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `symbol` | string | 是 | 6位数字股票代码 | `000001` |

**查询参数**：
| 参数 | 类型 | 必填 | 默认值 | 描述 | 示例 |
|------|------|------|--------|------|------|
| `years` | integer | 否 | `3` | 历史年数 (1-10) | `5` |

**示例请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/financial/summary/000001?years=5"
```

**响应示例**：
```json
{
  "success": true,
  "message": "Financial summary retrieved successfully",
  "data": {
    "symbol": "000001",
    "latest_report_date": "2023-12-31",
    "latest_revenue": "17648247.20",
    "latest_net_profit": "3625402.80",
    "latest_eps": "1.87",
    "latest_roe": "9.48",
    "latest_roa": "0.78",
    "latest_gross_margin": "44.28",
    "latest_net_margin": "20.55",
    "latest_debt_ratio": "91.75",
    "latest_current_ratio": "0.64"
  }
}
```

## 统一响应格式

### 成功响应格式

所有成功的 API 响应都遵循以下统一格式：

```json
{
  "success": true,
  "message": "操作成功描述信息",
  "data": {}, // 或 []，具体数据内容
  "pagination": { // 仅分页接口包含
    "total": 1000,
    "limit": 100,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  }
}
```

### 分页响应格式

对于返回列表数据的接口，统一使用分页格式：

```json
{
  "success": true,
  "message": "数据获取成功",
  "data": [...],
  "pagination": {
    "total": 5247,      // 总记录数
    "limit": 100,       // 每页大小
    "offset": 0,        // 当前偏移量
    "has_next": true,   // 是否有下一页
    "has_prev": false   // 是否有上一页
  }
}
```

## 错误处理

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {
    "field_errors": [...], // 字段验证错误（如有）
    "additional_info": "..." // 额外错误信息
  },
  "meta": {
    "path": "/api/v1/market/basic",
    "request_id": "req_123456789",
    "timestamp": "2025-08-12T10:30:00Z"
  }
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 描述 | 示例场景 |
|-----------|-------|------|----------|
| 400 | `BUSINESS_LOGIC_ERROR` | 业务逻辑错误 | 无效的股票代码格式 |
| 400 | `REQUEST_VALIDATION_ERROR` | 请求参数验证失败 | 必填参数缺失或格式错误 |
| 404 | `DATA_NOT_FOUND` | 数据未找到 | 查询的股票或报表不存在 |
| 422 | `VALIDATION_ERROR` | 数据验证错误 | 字段类型或值范围错误 |
| 429 | `RATE_LIMIT_ERROR` | 请求频率限制 | 超过API调用频率限制 |
| 500 | `DATABASE_ERROR` | 数据库操作错误 | 数据库连接失败或查询异常 |
| 500 | `CACHE_ERROR` | 缓存操作错误 | Redis缓存服务异常 |
| 500 | `INTERNAL_SERVER_ERROR` | 内部服务器错误 | 未捕获的系统异常 |

### 错误处理示例

#### 1. 参数验证错误

**请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/market/basic?symbols=invalid_symbol"
```

**响应**：
```json
{
  "success": false,
  "error_code": "BUSINESS_LOGIC_ERROR",
  "message": "Invalid stock symbol format: invalid_symbol. Expected 6-digit code.",
  "details": {},
  "meta": {
    "path": "/api/v1/market/basic",
    "request_id": "req_123456789",
    "timestamp": "2025-08-12T10:30:00Z"
  }
}
```

#### 2. 数据未找到错误

**请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/market/999999"
```

**响应**：
```json
{
  "success": false,
  "error_code": "DATA_NOT_FOUND",
  "message": "Stock 999999 not found",
  "details": {},
  "meta": {
    "path": "/api/v1/market/999999",
    "request_id": "req_123456789",
    "timestamp": "2025-08-12T10:30:00Z"
  }
}
```

#### 3. 字段验证错误

**请求**：
```bash
curl -X GET "http://localhost:8000/api/v1/financial/reports?limit=2000"
```

**响应**：
```json
{
  "success": false,
  "error_code": "REQUEST_VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": {
    "validation_errors": [
      {
        "field": "limit",
        "message": "ensure this value is less than or equal to 1000",
        "type": "value_error.number.not_le"
      }
    ]
  },
  "meta": {
    "path": "/api/v1/financial/reports",
    "request_id": "req_123456789",
    "timestamp": "2025-08-12T10:30:00Z"
  }
}
```

## 数据类型说明

### 1. 股票代码格式

- **格式**：6位数字字符串
- **示例**：`"000001"`、`"600000"`、`"300001"`
- **说明**：
  - 000001-099999：深圳主板
  - 300001-399999：深圳创业板
  - 600000-699999：上海主板
  - 688001-689999：上海科创板

### 2. 日期格式

- **格式**：`YYYY-MM-DD`
- **示例**：`"2024-08-12"`
- **时区**：UTC（响应中的 datetime 字段）

### 3. 金额单位

- **财务数据**：万元（人民币）
- **行情数据**：元（人民币）
- **市值数据**：万元（人民币）

### 4. 比率数据

- **百分比字段**：以百分数形式表示（如 `5.25` 表示 5.25%）
- **比率字段**：以小数形式表示（如 `1.25` 表示 1.25倍）

### 5. 布尔值

- **格式**：`true` / `false`
- **示例**：`"is_st": true`

## 性能优化和最佳实践

### 1. 分页查询优化

**推荐做法**：
```bash
# 使用合适的分页大小（建议50-200）
curl -X GET "http://localhost:8000/api/v1/market/basic?limit=100&offset=0"

# 大数据量查询时分批获取
for i in {0..10}; do
  offset=$((i * 500))
  curl -X GET "http://localhost:8000/api/v1/financial/reports?limit=500&offset=$offset"
done
```

**避免**：
```bash
# 避免单次请求过大数据量
curl -X GET "http://localhost:8000/api/v1/market/basic?limit=1000"  # 不推荐
```

### 2. 查询条件优化

**高效查询**：
```bash
# 使用具体的筛选条件
curl -X GET "http://localhost:8000/api/v1/market/basic?symbols=000001,000002&market=main"

# 使用日期范围限制
curl -X GET "http://localhost:8000/api/v1/market/quotes/daily?symbols=000001&start_date=2024-01-01&end_date=2024-03-31"
```

### 3. 缓存策略

API 服务内置多级缓存：
- **L1 缓存**：应用内存缓存（5分钟TTL）
- **L2 缓存**：Redis分布式缓存（1小时TTL）
- **L3 缓存**：查询结果缓存（1天TTL）

**客户端缓存建议**：
```bash
# 对于不频繁变化的数据（如股票基础信息），客户端可缓存较长时间
# 对于实时性要求高的数据（如行情数据），建议缓存时间不超过5分钟
```

### 4. 并发请求控制

**推荐并发策略**：
```bash
# 控制并发请求数量（建议不超过10个并发）
parallel -j 5 curl -X GET "http://localhost:8000/api/v1/market/000{1}" ::: 001 002 003 004 005
```

## 集成示例

### 1. Python 集成示例（增强版）

```python
import requests
import json
import time
from typing import List, Dict, Optional

class AShareAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_stocks(self, symbols: Optional[List[str]] = None, 
                   market: Optional[str] = None, 
                   limit: int = 100, offset: int = 0) -> Dict:
        """获取股票基础信息"""
        params = {
            "limit": limit,
            "offset": offset
        }
        if symbols:
            params["symbols"] = ",".join(symbols)
        if market:
            params["market"] = market
            
        response = self.session.get(f"{self.base_url}/market/basic", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_financial_reports(self, symbols: List[str], 
                            report_type: str = "A", 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict:
        """获取财务报表数据"""
        params = {
            "symbols": ",".join(symbols),
            "report_type": report_type
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = self.session.get(f"{self.base_url}/financial/reports", params=params)
        response.raise_for_status()
        return response.json()
    
    # 新增：股票数据初始化功能
    def check_rate_limit(self, symbol: str) -> Dict:
        """检查股票的速率限制状态"""
        response = self.session.get(f"{self.base_url}/initialization/stocks/{symbol}/rate-limit")
        response.raise_for_status()
        return response.json()
    
    def initialize_stock(self, symbol: str, start_date: str = "1970-01-01", 
                        end_date: Optional[str] = None, force_update: bool = False) -> Dict:
        """初始化股票数据"""
        data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date or "2025-08-14",
            "force_update": force_update
        }
        
        response = self.session.post(
            f"{self.base_url}/initialization/stocks/{symbol}/initialize",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_initialization_status(self, request_id: str) -> Dict:
        """查询初始化状态"""
        response = self.session.get(
            f"{self.base_url}/initialization/status/{request_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def batch_initialize_stocks(self, symbols: List[str], start_date: str = "1970-01-01", 
                               end_date: Optional[str] = None, force_update: bool = False) -> Dict:
        """批量初始化股票数据"""
        data = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date or "2025-08-14",
            "force_update": force_update
        }
        
        response = self.session.post(
            f"{self.base_url}/initialization/stocks/batch/initialize",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_initialization(self, request_id: str, check_interval: int = 10, 
                               timeout: int = 3600) -> Dict:
        """等待初始化完成，支持超时和轮询"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_initialization_status(request_id)
            
            if status["overall_status"] in ["completed", "failed", "partial_success"]:
                return status
            
            print(f"Status: {status['overall_status']}, Progress: {status.get('progress_percentage', 0):.1f}%")
            time.sleep(check_interval)
        
        raise TimeoutError(f"Initialization timeout after {timeout} seconds")
    
    def cleanup_old_records(self, hours_to_keep: int = 24, days_to_keep: int = 30) -> Dict:
        """清理过期记录"""
        params = {
            "hours_to_keep": hours_to_keep,
            "days_to_keep": days_to_keep
        }
        
        response = self.session.delete(f"{self.base_url}/initialization/cleanup", params=params)
        response.raise_for_status()
        return response.json()

# 使用示例
client = AShareAPIClient()

# 1. 检查速率限制
print("=== 检查速率限制 ===")
rate_limit = client.check_rate_limit("000001")
print(f"Rate limited: {rate_limit['is_rate_limited']}")
if rate_limit['is_rate_limited']:
    print(f"Remaining hours: {rate_limit['remaining_hours']}")

# 2. 初始化股票数据（如果不受限制）
if not rate_limit['is_rate_limited']:
    print("\n=== 初始化股票数据 ===")
    init_result = client.initialize_stock("000001", "2020-01-01", "2024-12-31")
    print(f"Request ID: {init_result['request_id']}")
    print(f"Status: {init_result['overall_status']}")
    
    # 等待完成
    print("\n=== 等待初始化完成 ===")
    final_status = client.wait_for_initialization(init_result['request_id'])
    print(f"Final status: {final_status['overall_status']}")

# 3. 批量初始化多只股票  
print("\n=== 批量初始化 ===")
batch_result = client.batch_initialize_stocks(["000002", "600519"], "2023-01-01")
print(f"Accepted: {batch_result['accepted_symbols']}")
print(f"Rejected: {batch_result['rejected_symbols']}")

# 4. 获取财务数据
print("\n=== 获取财务报表 ===")
reports = client.get_financial_reports(
    symbols=["000001"], 
    report_type="A", 
    start_date="2023-01-01", 
    end_date="2023-12-31"
)
print(f"Found {len(reports['data'])} financial reports")
```

### 2. Python 集成示例（基础版）

```python
import requests
import json
from typing import List, Dict, Optional

class AShareAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_stocks(self, symbols: Optional[List[str]] = None, 
                   market: Optional[str] = None, 
                   limit: int = 100, offset: int = 0) -> Dict:
        """获取股票基础信息"""
        params = {
            "limit": limit,
            "offset": offset
        }
        if symbols:
            params["symbols"] = ",".join(symbols)
        if market:
            params["market"] = market
            
        response = self.session.get(f"{self.base_url}/market/basic", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_financial_reports(self, symbols: List[str], 
                            report_type: str = "A", 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict:
        """获取财务报表数据"""
        params = {
            "symbols": ",".join(symbols),
            "report_type": report_type
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = self.session.get(f"{self.base_url}/financial/reports", params=params)
        response.raise_for_status()
        return response.json()

# 使用示例
client = AShareAPIClient()

# 获取银行股基础信息
stocks = client.get_stocks(symbols=["000001", "600000", "600036"])
print(f"Found {len(stocks['data'])} stocks")

# 获取财务报表
reports = client.get_financial_reports(
    symbols=["000001"], 
    report_type="A", 
    start_date="2023-01-01", 
    end_date="2023-12-31"
)
print(f"Found {len(reports['data'])} financial reports")
```

### 3. JavaScript/Node.js 集成示例

```javascript
const axios = require('axios');

class AShareAPIClient {
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000
        });
    }
    
    async getStocks(options = {}) {
        const { symbols, market, limit = 100, offset = 0 } = options;
        
        const params = { limit, offset };
        if (symbols) params.symbols = symbols.join(',');
        if (market) params.market = market;
        
        try {
            const response = await this.client.get('/market/basic', { params });
            return response.data;
        } catch (error) {
            throw new Error(`API request failed: ${error.message}`);
        }
    }
    
    async getDailyQuotes(symbols, dateRange = {}) {
        const { startDate, endDate, limit = 100, offset = 0 } = dateRange;
        
        const params = { 
            symbols: symbols.join(','),
            limit, 
            offset 
        };
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        try {
            const response = await this.client.get('/market/quotes/daily', { params });
            return response.data;
        } catch (error) {
            throw new Error(`API request failed: ${error.message}`);
        }
    }
    
    // 新增：股票数据初始化相关方法
    async initializeStock(symbol, options = {}) {
        const { startDate = '1970-01-01', endDate, forceUpdate = false } = options;
        
        try {
            const response = await this.client.post(`/initialization/stocks/${symbol}/initialize`, {
                symbol,
                start_date: startDate,
                end_date: endDate || new Date().toISOString().split('T')[0],
                force_update: forceUpdate
            });
            return response.data;
        } catch (error) {
            throw new Error(`Stock initialization failed: ${error.message}`);
        }
    }
    
    async getInitializationStatus(requestId) {
        try {
            const response = await this.client.get(`/initialization/status/${requestId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Status query failed: ${error.message}`);
        }
    }
    
    async checkRateLimit(symbol) {
        try {
            const response = await this.client.get(`/initialization/stocks/${symbol}/rate-limit`);
            return response.data;
        } catch (error) {
            throw new Error(`Rate limit check failed: ${error.message}`);
        }
    }
    
    async batchInitializeStocks(symbols, options = {}) {
        const { startDate = '1970-01-01', endDate, forceUpdate = false } = options;
        
        try {
            const response = await this.client.post('/initialization/stocks/batch/initialize', {
                symbols,
                start_date: startDate,
                end_date: endDate || new Date().toISOString().split('T')[0],
                force_update: forceUpdate
            });
            return response.data;
        } catch (error) {
            throw new Error(`Batch initialization failed: ${error.message}`);
        }
    }
    
    // 新增：申万行业数据查询方法
    async getSWIndustries(level = 'first', options = {}) {
        const { industryCodes, parentCodes, status = 'active', limit = 100, offset = 0 } = options;
        
        const params = { status, limit, offset };
        if (industryCodes) params.industry_codes = industryCodes.join(',');
        if (parentCodes) params.parent_codes = parentCodes.join(',');
        
        try {
            const response = await this.client.get(`/sw-industries/${level}`, { params });
            return response.data;
        } catch (error) {
            throw new Error(`SW industries query failed: ${error.message}`);
        }
    }
    
    async getSWIndustryConstituents(industryCode, options = {}) {
        const { status = 'active', limit = 100, offset = 0 } = options;
        
        const params = { status, limit, offset };
        
        try {
            const response = await this.client.get(`/sw-industries/${industryCode}/constituents`, { params });
            return response.data;
        } catch (error) {
            throw new Error(`SW industry constituents query failed: ${error.message}`);
        }
    }
    
    async getStockIndustryHierarchy(symbol) {
        try {
            const response = await this.client.get(`/sw-industries/hierarchy/${symbol}`);
            return response.data;
        } catch (error) {
            throw new Error(`Stock industry hierarchy query failed: ${error.message}`);
        }
    }
    
    async searchSWIndustries(keyword, options = {}) {
        const { levels = '1,2,3', exactMatch = false, limit = 20, offset = 0 } = options;
        
        const params = { 
            keyword, 
            levels, 
            exact_match: exactMatch,
            limit, 
            offset 
        };
        
        try {
            const response = await this.client.get('/sw-industries/search', { params });
            return response.data;
        } catch (error) {
            throw new Error(`SW industries search failed: ${error.message}`);
        }
    }
}

// 使用示例
(async () => {
    const client = new AShareAPIClient();
    
    try {
        // 获取平安银行股票信息
        const stocks = await client.getStocks({ symbols: ['000001'] });
        console.log('Stock info:', stocks.data[0]);
        
        // 检查速率限制
        const rateLimit = await client.checkRateLimit('000001');
        console.log('Rate limit status:', rateLimit);
        
        if (!rateLimit.is_rate_limited) {
            // 初始化股票数据
            const initResult = await client.initializeStock('000001', {
                startDate: '2020-01-01',
                endDate: '2024-12-31'
            });
            console.log('Initialization started:', initResult.request_id);
            
            // 轮询状态
            const checkStatus = async () => {
                const status = await client.getInitializationStatus(initResult.request_id);
                console.log('Status:', status.overall_status, 'Progress:', status.progress_percentage + '%');
                
                if (status.overall_status === 'processing') {
                    setTimeout(checkStatus, 5000); // 5秒后再次检查
                }
            };
            await checkStatus();
        }
        
        // 申万行业数据查询示例
        console.log('=== 申万行业数据查询 ===');
        
        // 1. 查询银行相关行业
        const bankIndustries = await client.searchSWIndustries('银行');
        console.log('银行相关行业:', bankIndustries.data.map(item => 
            `${item.industry_code} - ${item.industry_name} (L${item.level})`
        ));
        
        // 2. 获取一级行业列表
        const firstLevelIndustries = await client.getSWIndustries('first', { limit: 10 });
        console.log('一级行业数量:', firstLevelIndustries.pagination.total);
        
        // 3. 查询平安银行的行业层级
        const hierarchy = await client.getStockIndustryHierarchy('000001');
        console.log('平安银行行业分类:', hierarchy.data.hierarchy);
        
        // 4. 获取银行业成分股
        if (bankIndustries.data.length > 0) {
            const bankCode = bankIndustries.data[0].industry_code;
            const constituents = await client.getSWIndustryConstituents(bankCode, { limit: 5 });
            console.log(`银行业成分股 (前5只):`, constituents.data.map(item => item.symbol));
        }
        
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```

### 4. curl 脚本示例

```bash
#!/bin/bash

# A股数据API调用脚本示例

API_BASE="http://localhost:8000/api/v1"

# 函数：检查API响应状态
check_response() {
    if [ $? -eq 0 ]; then
        echo "✅ Request successful"
    else
        echo "❌ Request failed"
        exit 1
    fi
}

# 1. 健康检查
echo "🔍 Checking API health..."
curl -s "$API_BASE/health" | jq '.'
check_response

# 2. 获取银行股列表
echo "🏦 Getting bank stocks..."
curl -s "$API_BASE/market/basic?symbols=000001,600000,600036" | jq '.data[].name'
check_response

# 3. 检查股票数据初始化速率限制
echo "⏰ Checking rate limit for 000001..."
curl -s "$API_BASE/initialization/stocks/000001/rate-limit" | jq '.'
check_response

# 4. 初始化股票数据（如果没有速率限制）
echo "🚀 Initializing stock data for 000001..."
curl -s -X POST "$API_BASE/initialization/stocks/000001/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001",
    "start_date": "2020-01-01", 
    "end_date": "2024-12-31",
    "force_update": false
  }' | jq '.'
check_response

# 5. 获取平安银行最新财务数据
echo "📊 Getting latest financial data for 000001..."
curl -s "$API_BASE/financial/reports/latest?symbols=000001" | jq '.data[0] | {symbol, report_date, operating_revenue, net_profit, roe}'
check_response

# 6. 获取沪深300成分股（前10只）
echo "📈 Getting CSI 300 constituents..."
curl -s "$API_BASE/market/indices/000300/constituents?limit=10" | jq '.data[].symbol'
check_response

# 7. 批量初始化多只股票
echo "⚡ Batch initializing multiple stocks..."
curl -s -X POST "$API_BASE/initialization/stocks/batch/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["000002", "600519", "000858"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "force_update": false
  }' | jq '.'
check_response

# 8. 申万行业数据查询示例
echo "🏭 Querying SW industries data..."

# 查询银行相关行业
curl -s "$API_BASE/sw-industries/search?keyword=银行" | jq '.data[] | {industry_code, industry_name, level}'
check_response

# 获取一级行业列表（前10个）
curl -s "$API_BASE/sw-industries/first?limit=10" | jq '.data[] | {industry_code, industry_name}'
check_response

# 查询平安银行的行业层级
curl -s "$API_BASE/sw-industries/hierarchy/000001" | jq '.data.hierarchy'
check_response

# 获取银行业成分股（如果存在）
BANK_INDUSTRY_CODE=$(curl -s "$API_BASE/sw-industries/search?keyword=银行&exact_match=false&limit=1" | jq -r '.data[0].industry_code // empty')
if [ -n "$BANK_INDUSTRY_CODE" ]; then
    echo "🏦 Getting bank industry constituents for code: $BANK_INDUSTRY_CODE"
    curl -s "$API_BASE/sw-industries/$BANK_INDUSTRY_CODE/constituents?limit=5" | jq '.data[] | .symbol'
    check_response
fi

echo "🎉 All requests completed successfully!"
```

## 高级功能

### 1. 数据质量监控

API 服务内置数据质量监控机制：

```bash
# 查看数据质量信息（在响应的data_quality字段中）
curl -X GET "http://localhost:8000/api/v1/market/quotes/daily?symbols=000001" | jq '.data[0].data_quality'
```

质量等级说明：
- `excellent`：数据完整度 ≥ 95%
- `good`：数据完整度 80-95%
- `normal`：数据完整度 60-80%
- `poor`：数据完整度 < 60%

### 2. 数据源追溯

所有数据都包含来源信息：

```bash
# 查看数据源信息
curl -X GET "http://localhost:8000/api/v1/market/000001" | jq '.data.data_source'
# 输出: "akshare"
```

### 3. 批量数据获取

支持批量获取多只股票数据：

```bash
# 批量获取多只股票的财务数据
symbols="000001,000002,600000,600036,600519"
curl -X GET "http://localhost:8000/api/v1/financial/reports/latest?symbols=$symbols" | jq '.data[].symbol'
```

## 故障排除

### 1. 常见问题

**Q: API 返回 500 错误**
```bash
# A: 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
docker compose ps
```

**Q: 数据更新不及时**
```bash
# A: 检查数据收集任务状态
uv run ashare-data status

# 手动触发数据更新
uv run ashare-data collect stock-basic
```

**Q: 查询响应慢**
```bash
# A: 使用更具体的筛选条件
curl -X GET "http://localhost:8000/api/v1/market/basic?market=main&limit=50"

# 检查服务器资源使用情况
docker stats
```

### 2. 调试技巧

**开启详细日志**：
```bash
# 设置日志级别为DEBUG
export LOG_LEVEL=DEBUG
uv run python -m ashare_data.cli.main server --env=development
```

**使用工具测试API**：
```bash
# 使用httpie测试
http GET localhost:8000/api/v1/market/basic symbols==000001

# 使用postman collection导入
# 将API文档转换为Postman collection进行测试
```

## 更新日志

### v1.2.0 (2025-08-15)

**新增功能**：
- ✅ 申万行业数据API接口 (SW Industries Data)
- ✅ 一级行业信息查询 (`GET /api/v1/sw-industries/first`)
- ✅ 二级行业信息查询 (`GET /api/v1/sw-industries/second`)
- ✅ 三级行业信息查询 (`GET /api/v1/sw-industries/third`)
- ✅ 特定行业成分股查询 (`GET /api/v1/sw-industries/{industry_code}/constituents`)
- ✅ 批量行业成分股查询 (`GET /api/v1/sw-industries/constituents`)
- ✅ 行业成分股分析 (`GET /api/v1/sw-industries/constituents/analysis`)
- ✅ 股票行业层级查询 (`GET /api/v1/sw-industries/hierarchy/{symbol}`)
- ✅ 行业代码/名称搜索 (`GET /api/v1/sw-industries/search`)
- ✅ 增强版JavaScript和Python集成示例
- ✅ 完整的curl脚本示例更新

**申万行业数据特性**：
- 完整三级行业分类体系（31+104+227个行业分类）
- 支持模糊和精确搜索功能
- 层级关系查询和成分股分析
- 行业成分股统计分析功能
- 与现有股票数据完整集成

### v1.1.0 (2025-08-14)

**新增功能**：
- ✅ 股票数据初始化API接口 (Stock Data Initialization)
- ✅ 单个股票数据初始化 (`POST /initialization/stocks/{symbol}/initialize`)
- ✅ 批量股票数据初始化 (`POST /initialization/stocks/batch/initialize`)
- ✅ 初始化状态查询 (`GET /initialization/status/{request_id}`)
- ✅ 速率限制状态查询 (`GET /initialization/stocks/{symbol}/rate-limit`)
- ✅ 过期记录清理 (`DELETE /initialization/cleanup`)
- ✅ 支持异步处理和实时进度监控
- ✅ 内置速率限制机制（8小时冷却期）
- ✅ 增强版Python和JavaScript集成示例
- ✅ 完整的curl脚本示例更新

**技术特性增强**：
- 异步任务处理和状态跟踪
- 智能速率限制和冲突检测
- 批量处理支持（最多10个股票）
- 数据质量评分和监控
- 完整的错误处理和重试机制

### v1.0.0 (2025-08-12)

**新增功能**：
- ✅ 股票基础信息查询API
- ✅ 日线行情数据查询API  
- ✅ 指数基础信息查询API
- ✅ 指数成分股查询API
- ✅ 财务报表数据查询API
- ✅ 财务比率数据查询API
- ✅ 财务摘要查询API
- ✅ 统一错误处理机制
- ✅ 多级缓存策略
- ✅ 数据质量监控
- ✅ API文档和用户指南

**技术特性**：
- 基于 FastAPI 框架
- PostgreSQL + MongoDB 混合存储
- Redis 缓存层
- 异步处理支持
- 结构化日志记录
- Docker 容器化部署

## 技术支持

### 1. 文档和资源

- **项目文档**：`docs/` 目录
- **架构设计**：`docs/architecture/`
- **开发指南**：`docs/developer/`
- **部署文档**：`docs/operations/`

### 2. 联系方式

- **技术支持**：通过项目 Issue 提交问题
- **功能建议**：通过项目 Discussion 讨论新功能
- **文档反馈**：通过 Pull Request 改进文档

### 3. 贡献指南

欢迎贡献代码和文档：

```bash
# 克隆项目
git clone <repository-url>
cd ashare-data

# 创建开发环境
uv sync --dev

# 运行测试
uv run pytest

# 提交Pull Request
```

---

© 2025 A股数据同步服务。本文档持续更新中。