from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any

from tradingagents.dataflows import a_stock_utils as autils


def create_core_financials_agent(llm, toolkit):
    def node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        report = autils.fetch_core_financials(ticker)

        system_message = (
            "你是A股公司财务分析助手。根据工具输出，对营收、净利润、ROE、资产负债表与现金流、股东回报进行解读，"
            "评估财务是否健康、是否具备可持续性增长。输出分点叙述，并保留每节后的数据表与来源。"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message + "\n{data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(data=report)

        result = (prompt | llm).invoke(state["messages"])  
        return {
            "messages": [result],
            "a_core_financials": result.content,
        }

    return node


def create_industry_competition_agent(llm, toolkit):
    def node(state):
        ticker = state["company_of_interest"]

        report = autils.fetch_industry_comparison(ticker)

        system_message = (
            "你是行业竞争力分析助手。基于行业估值与财务指标样本，对目标公司与行业头部公司在毛利率、净利率、ROE等方面做横向比较，"
            "指出优势与短板，并说明行业整体所处阶段（高增/成熟/衰退）。输出包含清晰结论与表格证据。"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message + "\n{data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(data=report)

        result = (prompt | llm).invoke(state["messages"])  
        return {
            "messages": [result],
            "a_industry_competition": result.content,
        }

    return node


def create_valuation_signal_agent(llm, toolkit):
    def node(state):
        ticker = state["company_of_interest"]

        equity_report = autils.fetch_shareholder_and_equity(ticker)
        valuation_ts = autils.fetch_valuation_time_series(ticker)
        merged = f"{equity_report}\n\n{valuation_ts}" if equity_report else valuation_ts

        system_message = (
            "你是估值与市场信号分析助手。结合股权结构、限售解禁、股东户数变化、以及PR=PE/ROE的时序，判断是否存在异常或风险，"
            "并给出估值的历史相对位置与当前性价比结论。输出清晰可执行的判断与表格证据。"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message + "\n{data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(data=merged)

        result = (prompt | llm).invoke(state["messages"])  
        return {
            "messages": [result],
            "a_valuation_signal": result.content,
        }

    return node


def create_a_stock_report_aggregator(llm, toolkit):
    def node(state):
        system = (
            "你是报告整合助手。按照金字塔原理整合A股分析：先结论、后论据；涵盖核心财务、行业竞争、估值与市场信号。"
            "输出结构：\n"
            "1) 结论与操作建议(是否值得投资)\n"
            "2) 关键证据(要点式)\n"
            "3) 数据与来源(按节罗列并保留表格)\n"
        )

        data_blocks = []
        for key in ["a_core_financials", "a_industry_competition", "a_valuation_signal"]:
            if state.get(key):
                data_blocks.append(f"## {key}\n{state[key]}")
        fused = "\n\n".join(data_blocks) if data_blocks else "(no data)"

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system + "\n{data}"),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(data=fused)

        result = (prompt | llm).invoke(state["messages"])  
        return {
            "messages": [result],
            "a_stock_final_report": result.content,
        }

    return node


