"""
行业对比与竞争优势分析Agent

专门负责A股公司的行业对比分析，包括行业地位、竞争格局、
发展趋势、竞争优势评估等多个维度的全面分析。
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..utils.data_tools import AShareDataTools, DataProcessor
from ..utils.mcp_tools import MCPToolsWrapper
from ..utils.calculation_utils import FinancialCalculator, RiskCalculator
from ..utils.state_models import AnalysisStage, AnalysisDepth
from ..prompts.industry_prompts import (
    INDUSTRY_ANALYSIS_SYSTEM_PROMPT,
    INDUSTRY_ANALYSIS_USER_PROMPT,
    INDUSTRY_COMPETITIVENESS_SCORING_CRITERIA,
    INDUSTRY_ANALYSIS_REPORT_TEMPLATE,
    COMPETITIVE_ADVANTAGE_ANALYSIS_FRAMEWORK
)


logger = logging.getLogger(__name__)


def create_industry_analyst(llm, toolkit, config):
    """
    创建行业对比与竞争优势分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 工具集
        config: 配置字典
        
    Returns:
        行业分析Agent节点函数
    """
    
    # 初始化数据工具
    data_tools = AShareDataTools(config)
    mcp_tools = MCPToolsWrapper(config) if config.get("mcp_tools_enabled") else None
    
    # 创建行业数据获取工具
    @tool
    def get_industry_hierarchy_info(stock_code: str) -> Dict[str, Any]:
        """
        获取股票的申万行业层级信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            行业层级信息字典
        """
        try:
            logger.info(f"Getting industry hierarchy for {stock_code}")
            
            # 获取股票行业层级信息
            industry_hierarchy = data_tools.get_stock_industry_hierarchy(stock_code)
            
            if not industry_hierarchy:
                return {"error": "无法获取行业分类信息"}
            
            # 获取各级行业的详细信息
            industry_details = {}
            
            for level in [1, 2, 3]:
                level_code = industry_hierarchy.get(f"sw_level{level}_code")
                if level_code:
                    level_info = data_tools.get_shenwan_industry_info(
                        level=level, 
                        industry_codes=[level_code]
                    )
                    if level_info:
                        industry_details[f"level_{level}"] = level_info[0]
            
            return {
                "stock_code": stock_code,
                "industry_hierarchy": industry_hierarchy,
                "industry_details": industry_details,
                "classification_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting industry hierarchy for {stock_code}: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def get_industry_peers_analysis(stock_code: str, analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        获取行业同业公司对比分析数据
        
        Args:
            stock_code: 股票代码
            analysis_depth: 分析深度 (basic/comprehensive)
            
        Returns:
            同业对比分析数据
        """
        try:
            logger.info(f"Getting industry peers analysis for {stock_code}")
            
            # 获取股票行业信息
            industry_info = data_tools.get_stock_industry_hierarchy(stock_code)
            if not industry_info:
                return {"error": "无法获取行业分类信息"}
            
            # 获取同行业公司
            industry_codes = []
            for level in [2, 3]:  # 优先使用二三级行业
                code = industry_info.get(f"sw_level{level}_code")
                if code:
                    industry_codes.append(code)
                    break
            
            if not industry_codes:
                # 如果没有二三级行业，使用一级行业
                level1_code = industry_info.get("sw_level1_code")
                if level1_code:
                    industry_codes.append(level1_code)
            
            if not industry_codes:
                return {"error": "无法确定行业分类"}
            
            # 获取行业成分股
            peers = data_tools.get_industry_constituents(industry_codes)
            
            if not peers:
                return {"error": "无法获取行业成分股数据"}
            
            # 获取同业公司的财务数据
            peers_financial_data = []
            target_company_data = None
            
            # 限制分析的公司数量以提高效率
            max_peers = 20 if analysis_depth == "comprehensive" else 10
            selected_peers = peers[:max_peers]
            
            for peer in selected_peers:
                peer_code = peer.get("symbol", "")
                if not peer_code:
                    continue
                    
                try:
                    # 获取财务数据
                    financial_data = data_tools.get_latest_financial_report(peer_code)
                    if financial_data:
                        financial_data["stock_code"] = peer_code
                        financial_data["stock_name"] = peer.get("name", "")
                        peers_financial_data.append(financial_data)
                        
                        # 标记目标公司数据
                        if peer_code == stock_code:
                            target_company_data = financial_data
                            
                except Exception as e:
                    logger.warning(f"Failed to get financial data for peer {peer_code}: {str(e)}")
                    continue
            
            return {
                "stock_code": stock_code,
                "industry_codes": industry_codes,
                "total_peers": len(peers),
                "analyzed_peers": len(peers_financial_data),
                "target_company_data": target_company_data,
                "peers_financial_data": peers_financial_data,
                "industry_info": industry_info,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting industry peers analysis for {stock_code}: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_industry_metrics(peers_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算行业财务指标统计
        
        Args:
            peers_data: 同业公司数据
            
        Returns:
            行业指标统计结果
        """
        try:
            logger.info("Calculating industry metrics")
            
            peers_financial_data = peers_data.get("peers_financial_data", [])
            target_company_data = peers_data.get("target_company_data")
            
            if not peers_financial_data:
                return {"error": "缺少同业财务数据"}
            
            # 需要分析的财务指标
            metrics = [
                "total_revenue", "net_profit", "total_assets", "total_equity", 
                "total_liabilities", "roa", "roe", "eps", "gross_profit_margin",
                "net_profit_margin", "debt_to_asset_ratio"
            ]
            
            industry_stats = {}
            
            for metric in metrics:
                values = []
                for peer in peers_financial_data:
                    value = peer.get(metric)
                    if value is not None and str(value).replace('.', '').replace('-', '').isdigit():
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            continue
                
                if values:
                    industry_stats[metric] = {
                        "count": len(values),
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "min": min(values),
                        "max": max(values),
                        "stdev": statistics.stdev(values) if len(values) > 1 else 0
                    }
            
            # 计算目标公司在行业中的排名和分位数
            target_ranking = {}
            if target_company_data:
                for metric in metrics:
                    target_value = target_company_data.get(metric)
                    if target_value is not None and metric in industry_stats:
                        try:
                            target_value = float(target_value)
                            values = [float(peer.get(metric, 0)) for peer in peers_financial_data 
                                    if peer.get(metric) is not None]
                            
                            # 计算排名（降序，值越大排名越高）
                            rank = sum(1 for v in values if v < target_value) + 1
                            percentile = (rank / len(values)) * 100
                            
                            target_ranking[metric] = {
                                "value": target_value,
                                "rank": rank,
                                "total": len(values),
                                "percentile": percentile,
                                "above_average": target_value > industry_stats[metric]["mean"],
                                "above_median": target_value > industry_stats[metric]["median"]
                            }
                        except (ValueError, TypeError):
                            continue
            
            return {
                "industry_statistics": industry_stats,
                "target_company_ranking": target_ranking,
                "total_companies_analyzed": len(peers_financial_data),
                "metrics_calculated": len(industry_stats),
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating industry metrics: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def assess_competitive_advantages(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估竞争优势
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            竞争优势评估结果
        """
        try:
            logger.info("Assessing competitive advantages")
            
            target_ranking = analysis_data.get("target_company_ranking", {})
            industry_stats = analysis_data.get("industry_statistics", {})
            
            if not target_ranking:
                return {"error": "缺少目标公司排名数据"}
            
            advantages = {}
            advantage_score = 0
            
            # 技术优势评估（基于研发投入、ROA等）
            tech_indicators = ["roa", "total_assets"]
            tech_score = 0
            tech_count = 0
            
            for indicator in tech_indicators:
                if indicator in target_ranking:
                    percentile = target_ranking[indicator]["percentile"]
                    if percentile >= 75:
                        tech_score += 3
                    elif percentile >= 50:
                        tech_score += 2
                    else:
                        tech_score += 1
                    tech_count += 1
            
            if tech_count > 0:
                advantages["technology_advantage"] = {
                    "score": tech_score / tech_count,
                    "level": "强" if tech_score / tech_count >= 2.5 else "中" if tech_score / tech_count >= 1.5 else "弱",
                    "indicators": tech_indicators
                }
                advantage_score += (tech_score / tech_count) * 25
            
            # 盈利能力优势评估
            profit_indicators = ["roe", "net_profit_margin", "gross_profit_margin"]
            profit_score = 0
            profit_count = 0
            
            for indicator in profit_indicators:
                if indicator in target_ranking:
                    percentile = target_ranking[indicator]["percentile"]
                    if percentile >= 75:
                        profit_score += 3
                    elif percentile >= 50:
                        profit_score += 2
                    else:
                        profit_score += 1
                    profit_count += 1
            
            if profit_count > 0:
                advantages["profitability_advantage"] = {
                    "score": profit_score / profit_count,
                    "level": "强" if profit_score / profit_count >= 2.5 else "中" if profit_score / profit_count >= 1.5 else "弱",
                    "indicators": profit_indicators
                }
                advantage_score += (profit_score / profit_count) * 25
            
            # 规模优势评估
            scale_indicators = ["total_revenue", "total_assets"]
            scale_score = 0
            scale_count = 0
            
            for indicator in scale_indicators:
                if indicator in target_ranking:
                    percentile = target_ranking[indicator]["percentile"]
                    if percentile >= 75:
                        scale_score += 3
                    elif percentile >= 50:
                        scale_score += 2
                    else:
                        scale_score += 1
                    scale_count += 1
            
            if scale_count > 0:
                advantages["scale_advantage"] = {
                    "score": scale_score / scale_count,
                    "level": "强" if scale_score / scale_count >= 2.5 else "中" if scale_score / scale_count >= 1.5 else "弱",
                    "indicators": scale_indicators
                }
                advantage_score += (scale_score / scale_count) * 25
            
            # 财务稳健性优势评估
            stability_indicators = ["debt_to_asset_ratio"]  # 负向指标，债务率越低越好
            stability_score = 0
            stability_count = 0
            
            for indicator in stability_indicators:
                if indicator in target_ranking:
                    percentile = target_ranking[indicator]["percentile"]
                    # 对于负向指标，percentile越低越好
                    if percentile <= 25:
                        stability_score += 3
                    elif percentile <= 50:
                        stability_score += 2
                    else:
                        stability_score += 1
                    stability_count += 1
            
            if stability_count > 0:
                advantages["financial_stability_advantage"] = {
                    "score": stability_score / stability_count,
                    "level": "强" if stability_score / stability_count >= 2.5 else "中" if stability_score / stability_count >= 1.5 else "弱",
                    "indicators": stability_indicators
                }
                advantage_score += (stability_score / stability_count) * 25
            
            # 综合竞争优势评级
            if advantage_score >= 225:
                overall_advantage = "极强"
            elif advantage_score >= 200:
                overall_advantage = "很强"
            elif advantage_score >= 175:
                overall_advantage = "较强"
            elif advantage_score >= 150:
                overall_advantage = "中等"
            else:
                overall_advantage = "较弱"
            
            return {
                "competitive_advantages": advantages,
                "overall_advantage_score": advantage_score,
                "overall_advantage_level": overall_advantage,
                "advantage_count": len(advantages),
                "assessment_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing competitive advantages: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_industry_competitiveness_score(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算行业竞争力评分
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            竞争力评分结果
        """
        try:
            logger.info("Calculating industry competitiveness score")
            
            target_ranking = analysis_data.get("target_company_ranking", {})
            advantages = analysis_data.get("competitive_advantages", {})
            
            if not target_ranking:
                return {"error": "缺少目标公司排名数据"}
            
            score = 0
            score_breakdown = {}
            
            # 行业地位评分 (25分)
            revenue_rank = target_ranking.get("total_revenue", {})
            if revenue_rank:
                percentile = revenue_rank.get("percentile", 0)
                if percentile >= 85:
                    position_score = 25
                elif percentile >= 70:
                    position_score = 20
                elif percentile >= 50:
                    position_score = 15
                elif percentile >= 30:
                    position_score = 10
                else:
                    position_score = 5
            else:
                position_score = 10  # 默认评分
            
            score += position_score
            score_breakdown["industry_position"] = position_score
            
            # 盈利能力相对优势评分 (20分)
            roe_rank = target_ranking.get("roe", {})
            if roe_rank:
                percentile = roe_rank.get("percentile", 0)
                if percentile >= 85:
                    profit_score = 20
                elif percentile >= 70:
                    profit_score = 16
                elif percentile >= 50:
                    profit_score = 12
                elif percentile >= 30:
                    profit_score = 8
                else:
                    profit_score = 4
            else:
                profit_score = 8  # 默认评分
            
            score += profit_score
            score_breakdown["profitability_advantage"] = profit_score
            
            # 成长性相对优势评分 (15分) - 简化处理，基于规模
            asset_rank = target_ranking.get("total_assets", {})
            if asset_rank:
                percentile = asset_rank.get("percentile", 0)
                if percentile >= 85:
                    growth_score = 15
                elif percentile >= 70:
                    growth_score = 12
                elif percentile >= 50:
                    growth_score = 9
                elif percentile >= 30:
                    growth_score = 6
                else:
                    growth_score = 3
            else:
                growth_score = 6  # 默认评分
            
            score += growth_score
            score_breakdown["growth_advantage"] = growth_score
            
            # 护城河深度评分 (20分)
            advantage_count = len(advantages)
            if advantage_count >= 4:
                moat_score = 20
            elif advantage_count >= 3:
                moat_score = 16
            elif advantage_count >= 2:
                moat_score = 12
            elif advantage_count >= 1:
                moat_score = 8
            else:
                moat_score = 4
            
            score += moat_score
            score_breakdown["moat_depth"] = moat_score
            
            # 行业景气度评分 (10分) - 基于行业平均ROE
            industry_roe = analysis_data.get("industry_statistics", {}).get("roe", {}).get("mean", 0)
            if industry_roe > 15:
                industry_score = 10
            elif industry_roe > 10:
                industry_score = 8
            elif industry_roe > 5:
                industry_score = 6
            else:
                industry_score = 4
            
            score += industry_score
            score_breakdown["industry_attractiveness"] = industry_score
            
            # 风险控制能力评分 (10分)
            debt_rank = target_ranking.get("debt_to_asset_ratio", {})
            if debt_rank:
                percentile = debt_rank.get("percentile", 50)
                # 债务率越低越好
                if percentile <= 25:
                    risk_score = 10
                elif percentile <= 50:
                    risk_score = 8
                elif percentile <= 75:
                    risk_score = 6
                else:
                    risk_score = 4
            else:
                risk_score = 6  # 默认评分
            
            score += risk_score
            score_breakdown["risk_control"] = risk_score
            
            # 确定竞争力等级
            if score >= 90:
                competitiveness_level = "极强"
            elif score >= 80:
                competitiveness_level = "很强"
            elif score >= 70:
                competitiveness_level = "较强"
            elif score >= 60:
                competitiveness_level = "中等"
            else:
                competitiveness_level = "较弱"
            
            return {
                "total_score": score,
                "competitiveness_level": competitiveness_level,
                "score_breakdown": score_breakdown,
                "max_score": 100,
                "scoring_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating competitiveness score: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def generate_industry_analysis_report(analysis_data: Dict[str, Any]) -> str:
        """
        生成行业分析报告
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            格式化的行业分析报告
        """
        try:
            logger.info("Generating industry analysis report")
            
            stock_code = analysis_data.get("stock_code", "")
            stock_name = analysis_data.get("stock_name", "")
            
            # 获取各部分数据
            industry_info = analysis_data.get("industry_hierarchy", {})
            industry_details = analysis_data.get("industry_details", {})
            industry_stats = analysis_data.get("industry_statistics", {})
            target_ranking = analysis_data.get("target_company_ranking", {})
            advantages = analysis_data.get("competitive_advantages", {})
            competitiveness_score = analysis_data.get("competitiveness_score", {})
            
            # 构建报告基础信息
            report_sections = {
                "stock_name": stock_name,
                "stock_code": stock_code,
                "competitiveness_score": competitiveness_score.get("total_score", 0),
                "competitiveness_level": competitiveness_score.get("competitiveness_level", "未知"),
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 行业分类信息
            industry_classification = "申万行业分类：\n"
            for level in [1, 2, 3]:
                level_info = industry_details.get(f"level_{level}", {})
                if level_info:
                    industry_classification += f"- {level}级行业：{level_info.get('name', '未知')}（{level_info.get('code', '未知')}）\n"
            
            # 市场地位分析
            market_position = ""
            revenue_rank = target_ranking.get("total_revenue", {})
            if revenue_rank:
                rank = revenue_rank.get("rank", 0)
                total = revenue_rank.get("total", 0)
                percentile = revenue_rank.get("percentile", 0)
                market_position = f"在{total}家同行业公司中排名第{rank}位，处于前{percentile:.1f}%"
            
            # 竞争优势总结
            key_advantages = []
            for adv_type, adv_data in advantages.items():
                if adv_data.get("level") in ["强", "很强"]:
                    adv_name = {
                        "technology_advantage": "技术优势",
                        "profitability_advantage": "盈利能力优势", 
                        "scale_advantage": "规模优势",
                        "financial_stability_advantage": "财务稳健性优势"
                    }.get(adv_type, adv_type)
                    key_advantages.append(adv_name)
            
            advantages_text = "、".join(key_advantages) if key_advantages else "暂无明显竞争优势"
            
            # 行业指标对比
            profitability_comparison = ""
            if "roe" in target_ranking and "roe" in industry_stats:
                target_roe = target_ranking["roe"]["value"]
                industry_avg_roe = industry_stats["roe"]["mean"]
                profitability_comparison = f"""
                ROE对比分析：
                - 公司ROE：{target_roe:.2f}%
                - 行业平均ROE：{industry_avg_roe:.2f}%
                - 相对优势：{'超出' if target_roe > industry_avg_roe else '低于'}行业平均{abs(target_roe - industry_avg_roe):.2f}个百分点
                """
            
            report_sections.update({
                "core_conclusion": f"基于行业对比分析，该公司行业竞争力评分为{competitiveness_score.get('total_score', 0)}分，属于{competitiveness_score.get('competitiveness_level', '未知')}水平。",
                "key_advantages": advantages_text,
                "key_risks": "需关注行业竞争加剧和政策变化风险",
                "industry_classification": industry_classification,
                "market_share_position": market_position,
                "profitability_comparison": profitability_comparison,
                "data_sources": "A股数据同步服务API、申万行业分类"
            })
            
            # 使用简化的报告模板
            report = f"""
# {stock_name}（{stock_code}）行业对比与竞争优势分析报告

## 执行摘要
- **行业竞争力评分**：{report_sections['competitiveness_score']}/100分 ({report_sections['competitiveness_level']})
- **核心结论**：{report_sections['core_conclusion']}
- **竞争优势**：{report_sections['key_advantages']}
- **主要风险**：{report_sections['key_risks']}

## 行业分类与地位
{report_sections['industry_classification']}

### 市场地位
{report_sections['market_share_position']}

## 盈利能力对比分析
{report_sections['profitability_comparison']}

## 竞争优势评估
"""
            
            # 添加具体竞争优势分析
            for adv_type, adv_data in advantages.items():
                adv_name = {
                    "technology_advantage": "技术优势",
                    "profitability_advantage": "盈利能力优势",
                    "scale_advantage": "规模优势", 
                    "financial_stability_advantage": "财务稳健性优势"
                }.get(adv_type, adv_type)
                
                report += f"\n### {adv_name}\n"
                report += f"- 优势等级：{adv_data.get('level', '未知')}\n"
                report += f"- 评分：{adv_data.get('score', 0):.1f}/3.0\n"
            
            report += f"""

## 综合结论
基于以上行业对比与竞争优势分析，该公司在同行业中的竞争地位已进行全面评估。
投资者应重点关注公司的核心竞争优势及其可持续性，以及行业发展趋势对公司的影响。

---
**数据来源**：{report_sections['data_sources']}
**分析日期**：{report_sections['analysis_date']}
**报告生成时间**：{report_sections['report_time']}
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating industry analysis report: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    # 工具列表
    tools = [
        get_industry_hierarchy_info,
        get_industry_peers_analysis,
        calculate_industry_metrics,
        assess_competitive_advantages,
        calculate_industry_competitiveness_score,
        generate_industry_analysis_report
    ]
    
    # 如果启用MCP工具，添加MCP相关工具
    if mcp_tools:
        @tool
        def get_mcp_industry_data(stock_code: str) -> Dict[str, Any]:
            """
            使用MCP服务获取行业数据
            
            Args:
                stock_code: 股票代码
                
            Returns:
                MCP行业数据
            """
            try:
                return mcp_tools.get_industry_analysis(stock_code)
            except Exception as e:
                logger.error(f"Error getting MCP industry data: {str(e)}")
                return {"error": str(e)}
        
        tools.append(get_mcp_industry_data)
    
    def industry_analyst_node(state):
        """
        行业分析Agent节点函数
        
        Args:
            state: 当前分析状态
            
        Returns:
            更新后的状态
        """
        try:
            logger.info("Starting industry analysis")
            
            # 获取分析参数
            stock_code = state.get("stock_code", "")
            stock_name = state.get("stock_name", "")
            analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            
            if not stock_code:
                return {
                    "messages": [{"role": "assistant", "content": "错误：缺少股票代码"}],
                    "industry_analysis_report": "分析失败：缺少股票代码",
                    "analysis_stage": AnalysisStage.ERROR
                }
            
            # 构建系统提示词
            system_prompt = INDUSTRY_ANALYSIS_SYSTEM_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_date=analysis_date
            )
            
            # 构建用户提示词
            user_prompt = INDUSTRY_ANALYSIS_USER_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name
            )
            
            # 创建提示词模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt),
                MessagesPlaceholder(variable_name="messages")
            ])
            
            # 创建LLM链
            chain = prompt | llm.bind_tools(tools)
            
            # 执行分析
            messages = state.get("messages", [])
            if not messages:
                messages = [{"role": "user", "content": user_prompt}]
            
            result = chain.invoke({"messages": messages})
            
            # 处理工具调用结果
            industry_report = ""
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # 如果有工具调用，处理工具调用结果
                industry_report = f"{stock_name}（{stock_code}）行业分析已启动，正在处理行业数据..."
            else:
                # 如果没有工具调用，使用LLM直接回答
                industry_report = result.content
            
            logger.info("Industry analysis completed")
            
            return {
                "messages": [result],
                "industry_analysis_report": industry_report,
                "analysis_stage": AnalysisStage.INDUSTRY_ANALYSIS,
                "industry_data": state.get("industry_data", {}),
                "key_industry_metrics": {},  # 从分析中提取
                "competitive_position": {},  # 竞争地位信息
                "data_sources": state.get("data_sources", []) + ["A股数据API", "申万行业分类"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in industry analysis: {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": f"行业分析过程中出现错误: {str(e)}"}],
                "industry_analysis_report": f"分析失败: {str(e)}",
                "analysis_stage": AnalysisStage.ERROR
            }
    
    return industry_analyst_node