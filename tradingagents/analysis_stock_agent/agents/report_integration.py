"""
报告整合Agent
负责整合所有分析结果并生成最终投资报告
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_report_integration(llm, config):
    """
    创建报告整合Agent
    
    Args:
        llm: 语言模型实例（深度思考模型）
        config: 配置信息
        
    Returns:
        报告整合节点函数
    """
    
    def report_integration_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """报告整合节点"""
        
        stock_code = state["stock_code"]
        company_name = state.get("company_name", "")
        analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
        
        # 获取各分析结果
        financial_report = state.get("financial_report", "")
        financial_score = state.get("financial_score", 0)
        financial_metrics = state.get("financial_metrics", {})
        financial_risks = state.get("financial_risks", [])
        
        industry_report = state.get("industry_report", "")
        industry_position = state.get("industry_position", "")
        competitive_advantages = state.get("competitive_advantages", [])
        
        valuation_report = state.get("valuation_report", "")
        pr_ratio = state.get("pr_ratio", 0)
        valuation_level = state.get("valuation_level", "")
        target_price = state.get("target_price", 0)
        
        logger.info(f"开始整合 {company_name}({stock_code}) 的分析报告")
        
        # 构建整合提示词
        prompt = f"""
你是一位资深的投资研究总监，负责整合各位分析师的报告，生成最终的投资分析报告。

## 分析汇总信息：

### 公司基本信息
- 股票代码：{stock_code}
- 公司名称：{company_name}
- 分析日期：{analysis_date}

### 财务分析结果
- 财务健康评分：{financial_score}/100
- 关键指标：{json.dumps(financial_metrics, ensure_ascii=False)}
- 财务风险：{json.dumps(financial_risks, ensure_ascii=False)}
- 详细报告：
{financial_report[:1500]}

### 行业分析结果
- 行业地位：{industry_position}
- 竞争优势：{json.dumps(competitive_advantages, ensure_ascii=False)}
- 详细报告：
{industry_report[:1500]}

### 估值分析结果
- 估值水平：{valuation_level}
- PR值：{pr_ratio}
- 目标价格：{target_price}
- 详细报告：
{valuation_report[:1500]}

## 任务要求：

请基于以上分析结果，按照金字塔原理生成一份专业的投资分析报告。

### 1. 投资评级判定
基于综合分析，给出明确的投资评级：
- 强烈推荐：预期收益>30%，风险可控
- 推荐：预期收益15-30%，风险适中
- 中性：预期收益0-15%，风险与收益平衡
- 谨慎：预期收益<0，存在一定风险
- 回避：风险大于收益，不建议投资

### 2. 核心投资逻辑（金字塔顶层）
用1-2句话说明投资建议的核心逻辑

### 3. 支撑论据（金字塔中层）
从以下三个维度提供支撑：
- 财务面：盈利能力、成长性、财务健康度
- 行业面：行业地位、竞争优势、发展前景
- 估值面：估值水平、安全边际、上涨空间

### 4. 风险与机会（金字塔底层）
- 主要风险点（不超过3个）
- 主要机会点（不超过3个）

### 5. 投资建议
- 建议操作：买入/增持/持有/减持/卖出
- 目标价格：基于分析给出12个月目标价
- 止损价格：风险控制价位

## 输出格式：

```markdown
# {company_name}({stock_code}) 投资分析报告

## 一、投资结论

**投资评级**：[评级]  
**目标价格**：XX.XX元（潜在涨幅：XX%）  
**核心逻辑**：[一句话说明投资逻辑]

## 二、核心投资要点

### 2.1 财务表现[优异/良好/一般/较差]
[财务分析核心观点，包含具体数据]

### 2.2 行业地位[领先/稳固/一般/落后]
[行业分析核心观点，包含具体数据]

### 2.3 估值水平[低估/合理/高估]
[估值分析核心观点，包含具体数据]

## 三、投资建议

**操作建议**：[买入/增持/持有/减持/卖出]  
**建议仓位**：[XX%]  
**目标价格**：XX.XX元  
**止损价格**：XX.XX元  

## 四、风险提示

1. [主要风险1]
2. [主要风险2]
3. [主要风险3]

## 五、投资机会

1. [主要机会1]
2. [主要机会2]
3. [主要机会3]

## 六、关键数据汇总

| 指标 | 数值 | 评价 |
|------|------|------|
| ROE | XX% | 优秀/良好/一般 |
| 营收增长率 | XX% | 快速/稳定/缓慢 |
| PE | XX | 低估/合理/高估 |
| PR值 | XX | 合理/偏高/偏低 |
| 财务评分 | XX/100 | - |

---
*分析日期：{analysis_date}*  
*数据来源：公开市场数据*  
*风险提示：股市有风险，投资需谨慎。本报告仅供参考，不构成投资建议。*
```

请确保报告逻辑清晰、数据准确、结论有理有据。
"""
        
        try:
            # 调用深度思考模型进行报告整合
            response = llm.invoke(prompt)
            
            final_report = response.content
            
            # 提取投资评级和关键信息
            investment_rating = "中性"  # 默认值
            key_risks = []
            key_opportunities = []
            
            # 简单的文本解析提取关键信息
            lines = final_report.split('\n')
            for line in lines:
                if "投资评级" in line and "：" in line:
                    rating_text = line.split("：")[1].strip()
                    for rating in ["强烈推荐", "推荐", "中性", "谨慎", "回避"]:
                        if rating in rating_text:
                            investment_rating = rating
                            break
                elif line.strip().startswith("1. ") or line.strip().startswith("2. ") or line.strip().startswith("3. "):
                    if "风险提示" in final_report[:final_report.index(line)]:
                        risk = line.strip()[3:].strip()
                        if risk:
                            key_risks.append(risk)
                    elif "投资机会" in final_report[:final_report.index(line)]:
                        opportunity = line.strip()[3:].strip()
                        if opportunity:
                            key_opportunities.append(opportunity)
            
            # 计算置信度分数
            confidence_score = calculate_confidence_score(state)
            
            # 计算数据质量分数
            data_quality_score = calculate_data_quality_score(state)
            
            # 更新状态
            return {
                "final_report": final_report,
                "investment_rating": investment_rating,
                "target_price": target_price if target_price else 0,
                "key_risks": key_risks[:3],  # 最多3个
                "key_opportunities": key_opportunities[:3],  # 最多3个
                "confidence_score": confidence_score,
                "data_quality_score": data_quality_score,
                "analysis_version": "1.0.0",
                "analysis_duration": 0,  # 实际应计算耗时
            }
            
        except Exception as e:
            logger.error(f"报告整合失败: {e}")
            return {
                "final_report": "报告生成失败",
                "investment_rating": "未评级",
                "target_price": 0,
                "key_risks": ["报告生成失败"],
                "key_opportunities": [],
                "confidence_score": 0,
                "data_quality_score": 0,
                "error_messages": state.get("error_messages", []) + [str(e)]
            }
    
    return report_integration_node


def calculate_confidence_score(state: Dict[str, Any]) -> float:
    """
    计算决策置信度
    
    基于各项分析的完整性和一致性计算
    """
    score = 0
    max_score = 100
    
    # 财务分析完整性（30分）
    if state.get("financial_score", 0) > 0:
        score += min(30, state["financial_score"] * 0.3)
    
    # 行业分析完整性（20分）
    if state.get("industry_position") and state["industry_position"] != "未知":
        score += 10
    if state.get("competitive_advantages"):
        score += 10
    
    # 估值分析完整性（20分）
    if state.get("valuation_level") and state["valuation_level"] != "未知":
        score += 10
    if state.get("pr_ratio") and state["pr_ratio"] > 0:
        score += 10
    
    # 数据质量（20分）
    if not state.get("error_messages"):
        score += 20
    else:
        score += max(0, 20 - len(state.get("error_messages", [])) * 5)
    
    # 分析一致性（10分）
    # 简化处理：如果三个分析都完成且没有严重矛盾，给满分
    if (state.get("financial_report") and 
        state.get("industry_report") and 
        state.get("valuation_report")):
        score += 10
    
    return min(max_score, score)


def calculate_data_quality_score(state: Dict[str, Any]) -> float:
    """
    计算数据质量分数
    
    基于数据的完整性、时效性和准确性
    """
    score = 0
    max_score = 100
    
    # 财务数据完整性（40分）
    if state.get("raw_financial_data"):
        data = state["raw_financial_data"]
        if data.get("statements"):
            score += 15
        if data.get("indicators"):
            score += 15
        if data.get("dividends"):
            score += 10
    
    # 行业数据完整性（30分）
    if state.get("raw_industry_data"):
        data = state["raw_industry_data"]
        if data.get("industry_info"):
            score += 10
        if data.get("industry_comparison"):
            score += 10
        if data.get("company_valuation"):
            score += 10
    
    # 市场数据完整性（20分）
    if state.get("raw_market_data"):
        data = state["raw_market_data"]
        if data.get("valuation"):
            score += 10
        if data.get("shareholder"):
            score += 10
    
    # 错误扣分（最多扣10分）
    error_count = len(state.get("error_messages", []))
    score -= min(10, error_count * 5)
    
    return max(0, min(max_score, score))


class ReportIntegrationAgent:
    """报告整合Agent类"""
    
    def __init__(self, llm, config):
        """
        初始化报告整合Agent
        
        Args:
            llm: 语言模型实例（深度思考模型）
            config: 配置信息
        """
        self.llm = llm
        self.config = config
        self.integration_node = create_report_integration(llm, config)
    
    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成最终报告
        
        Args:
            state: 包含所有分析结果的状态
            
        Returns:
            包含最终报告的更新状态
        """
        return self.integration_node(state)
    
    def save_report(self, state: Dict[str, Any], output_path: str = None):
        """
        保存报告到文件
        
        Args:
            state: 包含报告的状态
            output_path: 输出路径
        """
        if not output_path:
            stock_code = state.get("stock_code", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/{stock_code}_report_{timestamp}.md"
        
        try:
            from pathlib import Path
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(state.get("final_report", ""))
            
            logger.info(f"报告已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None
