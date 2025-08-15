"""
行业分析Agent
负责分析公司的行业地位和竞争优势
"""

import json
from typing import Dict, Any, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def create_industry_analyst(llm, toolkit):
    """
    创建行业分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 数据工具包实例
        
    Returns:
        行业分析节点函数
    """
    
    def industry_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """行业分析节点"""
        
        stock_code = state["stock_code"]
        company_name = state.get("company_name", "")
        financial_metrics = state.get("financial_metrics", {})
        
        logger.info(f"开始分析 {company_name}({stock_code}) 的行业地位")
        
        try:
            # 1. 获取行业分类
            industry_info = toolkit.get_industry_classification(stock_code)
            
            # 2. 获取行业对比数据
            industry_comparison = None
            if industry_info and "行业代码" in industry_info:
                industry_comparison = toolkit.get_industry_comparison(
                    industry_info["行业代码"]
                )
            
            # 3. 获取公司市值等数据
            valuation_data = toolkit.get_stock_valuation(stock_code)
            
            # 保存原始数据
            raw_industry_data = {
                "industry_info": industry_info,
                "industry_comparison": industry_comparison.to_dict('records') if isinstance(industry_comparison, pd.DataFrame) else industry_comparison,
                "company_valuation": valuation_data
            }
            
            # 构建分析提示词
            prompt = f"""
你是一位专业的行业分析师，负责分析A股公司{company_name}({stock_code})的行业地位和竞争优势。

## 可用数据：

### 1. 公司行业信息：
{json.dumps(industry_info, ensure_ascii=False, indent=2)}

### 2. 行业内公司对比数据：
{json.dumps(raw_industry_data["industry_comparison"], ensure_ascii=False, indent=2)[:2000] if raw_industry_data["industry_comparison"] else "暂无数据"}

### 3. 公司估值数据：
{json.dumps(valuation_data, ensure_ascii=False, indent=2)}

### 4. 公司财务指标（来自财务分析）：
{json.dumps(financial_metrics, ensure_ascii=False, indent=2)}

## 分析任务：

### 1. 行业地位分析
- 确定公司在行业中的市场份额和排名
- 评估公司规模（市值、营收）在行业中的位置
- 分析公司的市场影响力

### 2. 竞争优势识别
- 对比分析公司与行业头部企业的关键指标差异
- 识别公司的独特竞争优势（如果有）
- 评估护城河的宽度和深度

### 3. 行业发展趋势
- 分析行业整体发展状况
- 评估行业增长前景
- 判断公司能否充分受益于行业发展

### 4. 对标分析
- 选择2-3家主要竞争对手进行对标
- 对比ROE、PE、营收增速等关键指标
- 找出公司的相对优势和劣势

## 输出格式：

请按以下JSON格式输出分析结果：

```json
{{
    "industry_position": "行业龙头/领先/中等/落后",
    "market_share": 15.5,  // 市场份额（%），如无法计算则为null
    "industry_ranking": {{
        "market_cap": 3,  // 市值排名
        "revenue": 5,  // 营收排名
        "overall": 4  // 综合排名
    }},
    "competitive_advantages": [
        "技术领先优势",
        "成本控制能力强",
        "品牌认知度高"
    ],
    "competitive_disadvantages": [
        "市场份额较小",
        "产品线单一"
    ],
    "industry_outlook": {{
        "growth_rate": "10-15%",  // 行业预期增长率
        "trend": "快速增长/稳定增长/缓慢增长/衰退",
        "opportunities": ["政策支持", "需求增长"],
        "threats": ["竞争加剧", "技术替代"]
    }},
    "peer_comparison": [
        {{
            "company": "竞争对手A",
            "metrics": {{
                "market_cap": 500,  // 亿元
                "pe": 25,
                "roe": 15
            }},
            "relative_position": "落后"
        }}
    ],
    "summary": "一句话总结行业地位",
    "detailed_report": "详细的行业分析报告..."
}}
```

请确保分析客观、数据准确，所有结论都有数据支撑。
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
                        "industry_position": "未知",
                        "summary": "行业分析完成，但格式解析失败",
                        "detailed_report": content
                    }
            except json.JSONDecodeError as e:
                logger.error(f"解析行业分析结果失败: {e}")
                analysis_result = {
                    "industry_position": "未知",
                    "summary": "行业分析完成，但结果解析失败",
                    "detailed_report": response.content
                }
            
            # 提取竞争优势
            competitive_advantages = analysis_result.get("competitive_advantages", [])
            
            # 行业排名
            industry_ranking = analysis_result.get("industry_ranking", {})
            
            # 更新状态
            return {
                "raw_industry_data": raw_industry_data,
                "industry_report": analysis_result.get("detailed_report", ""),
                "industry_position": analysis_result.get("industry_position", "未知"),
                "competitive_advantages": competitive_advantages,
                "industry_ranking": industry_ranking,
            }
            
        except Exception as e:
            logger.error(f"行业分析失败: {e}")
            return {
                "industry_report": f"行业分析失败: {str(e)}",
                "industry_position": "未知",
                "competitive_advantages": [],
                "industry_ranking": {},
                "error_messages": state.get("error_messages", []) + [str(e)]
            }
    
    return industry_analyst_node


class IndustryAnalystAgent:
    """行业分析Agent类"""
    
    def __init__(self, llm, toolkit):
        """
        初始化行业分析Agent
        
        Args:
            llm: 语言模型实例
            toolkit: 数据工具包实例
        """
        self.llm = llm
        self.toolkit = toolkit
        self.analyst_node = create_industry_analyst(llm, toolkit)
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行行业分析
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        return self.analyst_node(state)
    
    def get_tools(self) -> List:
        """获取使用的工具列表"""
        return [
            self.toolkit.get_industry_classification,
            self.toolkit.get_industry_comparison,
            self.toolkit.get_stock_valuation,
        ]
