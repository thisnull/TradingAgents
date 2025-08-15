"""
估值分析Agent
负责分析公司的估值水平和市场信号
"""

import json
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def create_valuation_analyst(llm, toolkit):
    """
    创建估值分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 数据工具包实例
        
    Returns:
        估值分析节点函数
    """
    
    def valuation_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """估值分析节点"""
        
        stock_code = state["stock_code"]
        company_name = state.get("company_name", "")
        financial_metrics = state.get("financial_metrics", {})
        industry_position = state.get("industry_position", "")
        
        logger.info(f"开始分析 {company_name}({stock_code}) 的估值水平")
        
        try:
            # 1. 获取估值数据
            valuation_data = toolkit.get_stock_valuation(stock_code)
            
            # 2. 获取股东结构
            shareholder_data = toolkit.get_shareholder_structure(stock_code)
            
            # 3. 获取历史行情（用于计算历史PE分位）
            # 注：这里简化处理，实际应该获取历史PE数据
            
            # 保存原始数据
            raw_market_data = {
                "valuation": valuation_data,
                "shareholder": shareholder_data,
            }
            
            # 计算PR值
            pr_ratio = None
            if valuation_data and financial_metrics:
                pe = valuation_data.get("PE_动态")
                roe = financial_metrics.get("ROE")
                if pe and roe and roe > 0:
                    pr_ratio = pe / roe
            
            # 构建分析提示词
            prompt = f"""
你是一位专业的估值分析师，负责分析A股公司{company_name}({stock_code})的估值水平和市场信号。

## 可用数据：

### 1. 当前估值数据：
{json.dumps(valuation_data, ensure_ascii=False, indent=2)}

### 2. 股东结构数据：
{json.dumps(shareholder_data, ensure_ascii=False, indent=2)[:2000]}

### 3. 财务指标（来自财务分析）：
{json.dumps(financial_metrics, ensure_ascii=False, indent=2)}

### 4. 行业地位：
{industry_position}

### 5. 计算的PR值：
{pr_ratio if pr_ratio else "无法计算（ROE或PE数据缺失）"}

## 分析任务：

### 1. 估值水平评估
- 分析当前PE、PB估值水平
- 判断估值在历史区间的位置（假设当前PE处于历史30%分位）
- 评估PR值的合理性（PR=PE/ROE，一般1-2为合理）
- 给出估值结论（低估/合理/高估）

### 2. 股东结构分析
- 分析股东人数变化趋势
- 评估股东集中度
- 识别机构持股情况
- 判断是否存在异常变动

### 3. 市场信号识别
- 分析近期股价表现
- 识别资金流向信号
- 评估市场情绪
- 判断买卖时机

### 4. 估值风险评估
- 识别估值相关的风险因素
- 评估风险等级
- 提供风险提示

## 输出格式：

请按以下JSON格式输出分析结果：

```json
{{
    "valuation_level": "低估/合理/高估",
    "pe_current": 15.5,  // 当前PE
    "pb_current": 2.3,  // 当前PB
    "pr_ratio": 1.2,  // PR值（PE/ROE）
    "pe_percentile": 30,  // PE历史百分位
    "pr_analysis": {{
        "value": 1.2,
        "assessment": "合理",  // 合理/偏高/偏低
        "explanation": "PR值在1-2之间，估值相对合理"
    }},
    "shareholder_analysis": {{
        "concentration": "集中/分散/稳定",
        "trend": "增加/减少/稳定",
        "institution_holding": "高/中/低",
        "abnormal_signal": "无/有（说明）"
    }},
    "market_signals": {{
        "price_trend": "上涨/下跌/震荡",
        "volume_signal": "放量/缩量/正常",
        "sentiment": "乐观/中性/悲观",
        "timing": "买入时机/持有观望/卖出时机"
    }},
    "valuation_risks": [
        "估值处于历史高位",
        "市盈率高于行业平均"
    ],
    "target_price": 25.5,  // 目标价格（基于估值模型）
    "upside_potential": 20,  // 上涨空间（%）
    "summary": "一句话总结估值情况",
    "detailed_report": "详细的估值分析报告..."
}}
```

请确保分析客观、计算准确，所有结论都有数据支撑。
"""
            
            # 调用LLM进行分析
            response = llm.invoke(prompt)
            
            # 解析响应
            try:
                content = response.content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    analysis_result = {
                        "valuation_level": "未知",
                        "pr_ratio": pr_ratio,
                        "summary": "估值分析完成，但格式解析失败",
                        "detailed_report": content
                    }
            except json.JSONDecodeError as e:
                logger.error(f"解析估值分析结果失败: {e}")
                analysis_result = {
                    "valuation_level": "未知",
                    "pr_ratio": pr_ratio,
                    "summary": "估值分析完成，但结果解析失败",
                    "detailed_report": response.content
                }
            
            # 提取关键信息
            pr_ratio_final = analysis_result.get("pr_ratio", pr_ratio)
            pe_percentile = analysis_result.get("pe_percentile", 50)
            shareholder_structure = analysis_result.get("shareholder_analysis", {})
            valuation_level = analysis_result.get("valuation_level", "未知")
            
            # 更新状态
            return {
                "raw_market_data": raw_market_data,
                "valuation_report": analysis_result.get("detailed_report", ""),
                "pr_ratio": pr_ratio_final,
                "pe_percentile": pe_percentile,
                "shareholder_structure": shareholder_structure,
                "valuation_level": valuation_level,
                "target_price": analysis_result.get("target_price", 0),
            }
            
        except Exception as e:
            logger.error(f"估值分析失败: {e}")
            return {
                "valuation_report": f"估值分析失败: {str(e)}",
                "pr_ratio": 0,
                "pe_percentile": 50,
                "shareholder_structure": {},
                "valuation_level": "未知",
                "target_price": 0,
                "error_messages": state.get("error_messages", []) + [str(e)]
            }
    
    return valuation_analyst_node


class ValuationAnalystAgent:
    """估值分析Agent类"""
    
    def __init__(self, llm, toolkit):
        """
        初始化估值分析Agent
        
        Args:
            llm: 语言模型实例
            toolkit: 数据工具包实例
        """
        self.llm = llm
        self.toolkit = toolkit
        self.analyst_node = create_valuation_analyst(llm, toolkit)
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行估值分析
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        return self.analyst_node(state)
    
    def get_tools(self) -> List:
        """获取使用的工具列表"""
        return [
            self.toolkit.get_stock_valuation,
            self.toolkit.get_shareholder_structure,
        ]
