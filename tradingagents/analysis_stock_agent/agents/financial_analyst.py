"""
财务分析Agent
负责分析公司的财务状况和健康度
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_financial_analyst(llm, toolkit):
    """
    创建财务分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 数据工具包实例
        
    Returns:
        财务分析节点函数
    """
    
    def financial_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """财务分析节点"""
        
        stock_code = state["stock_code"]
        company_name = state.get("company_name", "")
        analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
        
        # 获取财务数据
        logger.info(f"开始分析 {company_name}({stock_code}) 的财务状况")
        
        try:
            # 1. 获取财务报表
            financial_statements = toolkit.get_financial_statements(stock_code)
            
            # 2. 获取财务指标
            financial_indicators = toolkit.get_financial_indicators(stock_code)
            
            # 3. 获取分红历史
            dividend_history = toolkit.get_dividend_history(stock_code)
            
            # 保存原始数据
            raw_financial_data = {
                "statements": financial_statements,
                "indicators": financial_indicators,
                "dividends": dividend_history
            }
            
            # 构建分析提示词
            prompt = f"""
你是一位专业的财务分析师，负责分析A股公司{company_name}({stock_code})的财务状况。

分析日期：{analysis_date}

可用数据：
1. 财务报表数据：
{json.dumps(financial_statements, ensure_ascii=False, indent=2)[:3000]}

2. 财务指标数据：
{json.dumps(financial_indicators, ensure_ascii=False, indent=2)}

3. 分红历史：
{json.dumps(dividend_history, ensure_ascii=False, indent=2)[:1000]}

请基于以上数据，完成以下分析任务：

## 分析要求：

### 1. 营收与净利润分析
- 分析近3年的营收增长趋势（计算CAGR）
- 评估净利润率变化趋势
- 识别增长驱动因素
- 判断增长的可持续性

### 2. 盈利能力分析
- 分析ROE变化趋势（近3年）
- 评估ROA、净利率、毛利率
- 与行业平均水平对比（假设行业平均ROE为12%）
- 评估盈利质量

### 3. 财务健康度评估
- 资产负债率分析（是否在合理范围）
- 流动性分析（流动比率、速动比率）
- 现金流质量分析（经营现金流/净利润比率）
- 偿债能力评估

### 4. 股东回报分析
- 历史分红记录分析
- 股息率计算与评估
- 股东回报政策稳定性

### 5. 财务风险识别
- 列出主要财务风险点（不超过3个）
- 评估风险等级（低/中/高）

## 输出格式：

请按以下JSON格式输出分析结果：

```json
{{
    "financial_score": 75,  // 财务健康评分（0-100）
    "summary": "一句话总结财务状况",
    "revenue_analysis": {{
        "cagr_3y": 15.5,  // 3年营收CAGR（%）
        "trend": "稳定增长",
        "driver": "主营业务扩张"
    }},
    "profitability": {{
        "roe_latest": 18.5,  // 最新ROE（%）
        "roe_trend": "上升",
        "profit_margin": 12.3,  // 净利率（%）
        "quality": "优秀"
    }},
    "financial_health": {{
        "debt_ratio": 45.2,  // 资产负债率（%）
        "current_ratio": 1.8,  // 流动比率
        "cash_flow_quality": "良好",
        "overall": "健康"
    }},
    "dividend": {{
        "dividend_yield": 2.5,  // 股息率（%）
        "stability": "稳定",
        "policy": "持续分红"
    }},
    "risks": [
        "应收账款增长过快",
        "存货周转率下降"
    ],
    "detailed_report": "详细的财务分析报告文本..."
}}
```

请确保所有数值计算准确，结论有数据支撑。
"""
            
            # 调用LLM进行分析
            response = llm.invoke(prompt)
            
            # 解析响应
            try:
                # 提取JSON内容
                content = response.content
                # 查找JSON块
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    # 如果没有找到JSON，使用默认结构
                    analysis_result = {
                        "financial_score": 60,
                        "summary": "财务分析完成，但格式解析失败",
                        "detailed_report": content
                    }
            except json.JSONDecodeError as e:
                logger.error(f"解析财务分析结果失败: {e}")
                analysis_result = {
                    "financial_score": 60,
                    "summary": "财务分析完成，但结果解析失败",
                    "detailed_report": response.content
                }
            
            # 提取关键指标
            financial_metrics = {
                "营收CAGR": analysis_result.get("revenue_analysis", {}).get("cagr_3y"),
                "ROE": analysis_result.get("profitability", {}).get("roe_latest"),
                "净利率": analysis_result.get("profitability", {}).get("profit_margin"),
                "资产负债率": analysis_result.get("financial_health", {}).get("debt_ratio"),
                "流动比率": analysis_result.get("financial_health", {}).get("current_ratio"),
                "股息率": analysis_result.get("dividend", {}).get("dividend_yield"),
            }
            
            # 更新状态
            return {
                "raw_financial_data": raw_financial_data,
                "financial_report": analysis_result.get("detailed_report", ""),
                "financial_score": analysis_result.get("financial_score", 60),
                "financial_metrics": financial_metrics,
                "financial_risks": analysis_result.get("risks", []),
            }
            
        except Exception as e:
            logger.error(f"财务分析失败: {e}")
            return {
                "financial_report": f"财务分析失败: {str(e)}",
                "financial_score": 0,
                "financial_metrics": {},
                "financial_risks": ["数据获取失败"],
                "error_messages": [str(e)]
            }
    
    return financial_analyst_node


class FinancialAnalystAgent:
    """财务分析Agent类"""
    
    def __init__(self, llm, toolkit):
        """
        初始化财务分析Agent
        
        Args:
            llm: 语言模型实例
            toolkit: 数据工具包实例
        """
        self.llm = llm
        self.toolkit = toolkit
        self.analyst_node = create_financial_analyst(llm, toolkit)
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行财务分析
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        return self.analyst_node(state)
    
    def get_tools(self) -> List:
        """获取使用的工具列表"""
        return [
            self.toolkit.get_financial_statements,
            self.toolkit.get_financial_indicators,
            self.toolkit.get_dividend_history,
        ]
