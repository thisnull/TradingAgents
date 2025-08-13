import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import akshare as ak


def _df_to_markdown(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df is None or df.empty:
        return "(no data)"
    df_disp = df.copy()
    if len(df_disp) > max_rows:
        df_disp = df_disp.head(max_rows)
    return df_disp.to_markdown(index=False)


def _with_source(block: str, source: str) -> str:
    return f"{block}\n\n数据来源: {source}"


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def fetch_core_financials(symbol: str, recent_years: int = 5) -> str:
    symbol = normalize_symbol(symbol)

    sections: List[str] = []

    try:
        ind_df = ak.stock_financial_analysis_indicator(symbol)
        if not ind_df.empty:
            # 只保留最近 N 年
            if "报告期" in ind_df.columns:
                ind_df = ind_df.sort_values("报告期", ascending=False)
                ind_df = ind_df.head(recent_years)
            sections.append(
                _with_source(
                    f"### 主要财务指标\n{_df_to_markdown(ind_df)}",
                    "AKShare: stock_financial_analysis_indicator (东方财富)",
                )
            )
    except Exception as e:
        sections.append(f"主要财务指标获取失败: {e}")

    try:
        is_df = ak.stock_profit_sheet_by_report_em(symbol)
        if not is_df.empty:
            is_df = is_df.sort_values("报告期", ascending=False).head(recent_years)
            sections.append(
                _with_source(
                    f"### 利润表(按报告期)\n{_df_to_markdown(is_df)}",
                    "AKShare: stock_profit_sheet_by_report_em (东方财富)",
                )
            )
    except Exception as e:
        sections.append(f"利润表获取失败: {e}")

    try:
        bs_df = ak.stock_balance_sheet_by_report_em(symbol)
        if not bs_df.empty:
            bs_df = bs_df.sort_values("报告期", ascending=False).head(recent_years)
            sections.append(
                _with_source(
                    f"### 资产负债表(按报告期)\n{_df_to_markdown(bs_df)}",
                    "AKShare: stock_balance_sheet_by_report_em (东方财富)",
                )
            )
    except Exception as e:
        sections.append(f"资产负债表获取失败: {e}")

    try:
        cf_df = ak.stock_cash_flow_sheet_by_report_em(symbol)
        if not cf_df.empty:
            cf_df = cf_df.sort_values("报告期", ascending=False).head(recent_years)
            sections.append(
                _with_source(
                    f"### 现金流量表(按报告期)\n{_df_to_markdown(cf_df)}",
                    "AKShare: stock_cash_flow_sheet_by_report_em (东方财富)",
                )
            )
    except Exception as e:
        sections.append(f"现金流量表获取失败: {e}")

    try:
        div_df = ak.stock_history_dividend(symbol)
        if not div_df.empty:
            div_df = div_df.sort_values("分红年度", ascending=False).head(10)
            sections.append(
                _with_source(
                    f"### 历史分红(近10条)\n{_df_to_markdown(div_df)}",
                    "AKShare: stock_history_dividend (东方财富/巨潮)",
                )
            )
    except Exception as e:
        sections.append(f"历史分红获取失败: {e}")

    return "\n\n".join(sections)


def fetch_shareholder_and_equity(symbol: str) -> str:
    symbol = normalize_symbol(symbol)
    sections: List[str] = []

    try:
        main_holder_df = ak.stock_main_stock_holder(symbol)
        if not main_holder_df.empty:
            sections.append(
                _with_source(
                    f"### 前十大股东\n{_df_to_markdown(main_holder_df)}",
                    "AKShare: stock_main_stock_holder",
                )
            )
    except Exception as e:
        sections.append(f"前十大股东获取失败: {e}")

    try:
        cir_holder_df = ak.stock_circulate_stock_holder(symbol)
        if not cir_holder_df.empty:
            sections.append(
                _with_source(
                    f"### 流通股东\n{_df_to_markdown(cir_holder_df)}",
                    "AKShare: stock_circulate_stock_holder",
                )
            )
    except Exception as e:
        sections.append(f"流通股东获取失败: {e}")

    try:
        gdhs_df = ak.stock_zh_a_gdhs(symbol)
        if not gdhs_df.empty:
            gdhs_df = gdhs_df.sort_values("截止日期", ascending=False).head(12)
            sections.append(
                _with_source(
                    f"### 股东户数(近12期)\n{_df_to_markdown(gdhs_df)}",
                    "AKShare: stock_zh_a_gdhs",
                )
            )
    except Exception as e:
        sections.append(f"股东户数获取失败: {e}")

    try:
        unlock_df = ak.stock_restricted_release_summary_em(symbol)
        if not unlock_df.empty:
            unlock_df = unlock_df.sort_values("解禁时间", ascending=False).head(20)
            sections.append(
                _with_source(
                    f"### 限售解禁概览(近20条)\n{_df_to_markdown(unlock_df)}",
                    "AKShare: stock_restricted_release_summary_em",
                )
            )
    except Exception as e:
        sections.append(f"限售解禁获取失败: {e}")

    return "\n\n".join(sections)


def fetch_industry_comparison(symbol: str) -> str:
    symbol = normalize_symbol(symbol)
    sections: List[str] = []

    try:
        a_ind_df = ak.stock_a_indicator_lg()
        if not a_ind_df.empty:
            # 当前个股指标
            current_row = a_ind_df[a_ind_df["股票代码"].astype(str).str.contains(symbol)].head(1)
            peer_sample = a_ind_df.sample(min(30, len(a_ind_df))) if len(a_ind_df) > 0 else a_ind_df
            sections.append(
                _with_source(
                    f"### 个股估值与全市场样本\n个股(若能匹配):\n{_df_to_markdown(current_row)}\n\n全市场样本(随机30):\n{_df_to_markdown(peer_sample)}",
                    "AKShare: stock_a_indicator_lg (乐咕乐股)",
                )
            )
    except Exception as e:
        sections.append(f"A股估值指标获取失败: {e}")

    try:
        sw_info = ak.sw_index_third_info()
        if not sw_info.empty:
            sw_info = sw_info.sort_values("成份个数", ascending=False)
            sections.append(
                _with_source(
                    f"### 申万行业估值快照\n{_df_to_markdown(sw_info.head(30))}",
                    "AKShare: sw_index_third_info",
                )
            )
    except Exception as e:
        sections.append(f"申万行业信息获取失败: {e}")

    return "\n\n".join(sections)


def fetch_valuation_time_series(symbol: str, recent_periods: int = 8) -> str:
    symbol = normalize_symbol(symbol)
    sections: List[str] = []

    pe_series = None
    roe_series = None

    try:
        ind_df = ak.stock_financial_analysis_indicator(symbol)
        if not ind_df.empty:
            ind_df = ind_df.sort_values("报告期", ascending=False).head(recent_periods)
            cols = ind_df.columns.tolist()
            # 尝试常见中文列名
            # ROE
            for roe_col in ["净资产收益率-加权(%)", "净资产收益率(%)", "ROE(%)"]:
                if roe_col in cols:
                    roe_series = ind_df[["报告期", roe_col]].rename(columns={roe_col: "ROE(%)"})
                    break
            # PE
            for pe_col in ["市盈率-TTM", "市盈率(TTM)", "PE(TTM)"]:
                if pe_col in cols:
                    pe_series = ind_df[["报告期", pe_col]].rename(columns={pe_col: "PE(TTM)"})
                    break
            if pe_series is not None and roe_series is not None:
                merged = pd.merge(pe_series, roe_series, on="报告期", how="inner")
                merged["PR = PE/ROE"] = merged.apply(
                    lambda r: (float(r["PE(TTM)"]) / (float(r["ROE(%)"]) / 100.0)) if r["ROE(%)"] not in [0, None, ""] else None,
                    axis=1,
                )
                sections.append(
                    _with_source(
                        f"### 估值与盈利能力时序\n{_df_to_markdown(merged)}",
                        "AKShare: stock_financial_analysis_indicator (东方财富)",
                    )
                )
            else:
                sections.append("未从指标中解析到可用的PE或ROE列")
    except Exception as e:
        sections.append(f"估值与盈利能力时序计算失败: {e}")

    return "\n\n".join(sections)


