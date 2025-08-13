from typing import Dict, Any

from langgraph.graph import StateGraph, START, END

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.agents.analysis_stock_agent.agents import (
    create_core_financials_agent,
    create_industry_competition_agent,
    create_valuation_signal_agent,
    create_a_stock_report_aggregator,
)


class AStockGraph(TradingAgentsGraph):
    def __init__(self, debug: bool = False, config: Dict[str, Any] | None = None):
        super().__init__(selected_analysts=["market"], debug=debug, config=config)

        core = create_core_financials_agent(self.quick_thinking_llm, self.toolkit)
        industry = create_industry_competition_agent(self.quick_thinking_llm, self.toolkit)
        valuation = create_valuation_signal_agent(self.quick_thinking_llm, self.toolkit)
        aggregator = create_a_stock_report_aggregator(self.deep_thinking_llm, self.toolkit)

        sg = StateGraph(self.propagator.state_schema)
        sg.add_node("Core Financials", core)
        sg.add_node("Industry & Competition", industry)
        sg.add_node("Valuation & Signals", valuation)
        sg.add_node("A-Stock Aggregator", aggregator)

        sg.add_edge(START, "Core Financials")
        sg.add_edge("Core Financials", "Industry & Competition")
        sg.add_edge("Industry & Competition", "Valuation & Signals")
        sg.add_edge("Valuation & Signals", "A-Stock Aggregator")
        sg.add_edge("A-Stock Aggregator", END)

        self.graph = sg.compile()


