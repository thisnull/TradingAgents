#!/usr/bin/env python3
"""
TradingAgents 系统完整性测试脚本
用于验证系统配置是否正确，各组件是否正常工作
"""

import os
import sys
import traceback
from datetime import datetime, timedelta
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich.tree import Tree
import time

# 加载.env文件
def load_env_file():
    """加载.env文件中的环境变量"""
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ 已加载 .env 文件")
    else:
        print("⚠️  未找到 .env 文件，使用系统环境变量")

# 在导入其他模块前先加载环境变量
load_env_file()

console = Console()

class TradingAgentsHealthChecker:
    def __init__(self):
        self.console = console
        self.test_results = []
        
    def log_test(self, test_name, status, message="", details=""):
        """记录测试结果"""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "details": details
        })
        
        if status == "PASS":
            self.console.print(f"✅ {test_name}: {message}", style="green")
        elif status == "FAIL":
            self.console.print(f"❌ {test_name}: {message}", style="red")
            if details:
                self.console.print(f"   详细信息: {details}", style="red dim")
        elif status == "WARNING":
            self.console.print(f"⚠️  {test_name}: {message}", style="yellow")
        else:
            self.console.print(f"ℹ️  {test_name}: {message}", style="blue")

    def test_environment_variables(self):
        """测试环境变量配置"""
        self.console.print("\n[bold blue]🔧 测试环境变量配置[/bold blue]")
        
        required_vars = {
            "OPENAI_API_KEY": "LLM API密钥",
            "TRADINGAGENTS_BACKEND_URL": "LLM服务端点",
        }
        
        optional_vars = {
            "FINNHUB_API_KEY": "FinnHub API密钥(可选)",
            "TRADINGAGENTS_DEEP_THINK_LLM": "深度思考模型",
            "TRADINGAGENTS_QUICK_THINK_LLM": "快速响应模型",
        }
        
        # 检查必需变量
        for var, desc in required_vars.items():
            value = os.getenv(var)
            if value:
                # 对API密钥进行脱敏显示
                if "KEY" in var:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value
                self.log_test(f"环境变量 {var}", "PASS", f"{desc}: {display_value}")
            else:
                self.log_test(f"环境变量 {var}", "FAIL", f"{desc} 未设置")
        
        # 检查可选变量
        for var, desc in optional_vars.items():
            value = os.getenv(var)
            if value:
                if "KEY" in var:
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value
                self.log_test(f"环境变量 {var}", "PASS", f"{desc}: {display_value}")
            else:
                self.log_test(f"环境变量 {var}", "WARNING", f"{desc} 未设置(使用默认值)")

    def test_dependencies(self):
        """测试依赖包是否正确安装"""
        self.console.print("\n[bold blue]📦 测试依赖包安装[/bold blue]")
        
        required_packages = [
            ("langchain_openai", "LangChain OpenAI集成"),
            ("langgraph", "LangGraph工作流框架"),
            ("pandas", "数据处理库"),
            ("yfinance", "Yahoo Finance数据"),
            ("rich", "命令行美化库"),
            ("requests", "HTTP请求库"),
        ]
        
        for package, desc in required_packages:
            try:
                __import__(package)
                self.log_test(f"依赖包 {package}", "PASS", f"{desc} 已安装")
            except ImportError as e:
                self.log_test(f"依赖包 {package}", "FAIL", f"{desc} 未安装", str(e))

    def test_llm_api_connection(self):
        """测试LLM API连接"""
        self.console.print("\n[bold blue]🌐 测试LLM API连接[/bold blue]")
        
        backend_url = os.getenv("TRADINGAGENTS_BACKEND_URL")
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not backend_url or not api_key:
            self.log_test("LLM API连接", "FAIL", "缺少必要的API配置")
            return
        
        try:
            # 测试API连通性
            models_url = f"{backend_url.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            with self.console.status("[bold green]正在测试API连接..."):
                response = requests.get(models_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    models = [model.get("id", "unknown") for model in data["data"]]
                    self.log_test("LLM API连接", "PASS", f"连接成功，发现 {len(models)} 个可用模型")
                    
                    # 检查配置的模型是否可用
                    deep_model = os.getenv("TRADINGAGENTS_DEEP_THINK_LLM", "deepseek-r1")
                    quick_model = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "gemini-2.5-flash")
                    
                    if deep_model in models:
                        self.log_test("深度思考模型", "PASS", f"{deep_model} 可用")
                    else:
                        self.log_test("深度思考模型", "WARNING", f"{deep_model} 在可用模型中未找到")
                    
                    if quick_model in models:
                        self.log_test("快速响应模型", "PASS", f"{quick_model} 可用")
                    else:
                        self.log_test("快速响应模型", "WARNING", f"{quick_model} 在可用模型中未找到")
                        
                else:
                    self.log_test("LLM API连接", "PASS", "连接成功但响应格式异常")
            else:
                self.log_test("LLM API连接", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            self.log_test("LLM API连接", "FAIL", "连接超时")
        except requests.exceptions.ConnectionError:
            self.log_test("LLM API连接", "FAIL", "无法连接到API端点")
        except Exception as e:
            self.log_test("LLM API连接", "FAIL", "连接测试失败", str(e))

    def test_tradingagents_import(self):
        """测试TradingAgents核心模块导入"""
        self.console.print("\n[bold blue]🏗️ 测试TradingAgents核心模块[/bold blue]")
        
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            self.log_test("TradingAgentsGraph导入", "PASS", "核心类导入成功")
        except Exception as e:
            self.log_test("TradingAgentsGraph导入", "FAIL", "核心类导入失败", str(e))
            return False
            
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            self.log_test("默认配置导入", "PASS", "配置文件导入成功")
        except Exception as e:
            self.log_test("默认配置导入", "FAIL", "配置文件导入失败", str(e))
            return False
            
        return True

    def test_configuration_loading(self):
        """测试配置加载"""
        self.console.print("\n[bold blue]⚙️ 测试配置加载[/bold blue]")
        
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            
            # 检查关键配置项
            key_configs = [
                "llm_provider",
                "deep_think_llm", 
                "quick_think_llm",
                "backend_url",
                "online_tools"
            ]
            
            for config_key in key_configs:
                if config_key in DEFAULT_CONFIG:
                    value = DEFAULT_CONFIG[config_key]
                    self.log_test(f"配置项 {config_key}", "PASS", f"值: {value}")
                else:
                    self.log_test(f"配置项 {config_key}", "FAIL", "配置项缺失")
                    
        except Exception as e:
            self.log_test("配置加载", "FAIL", "配置加载失败", str(e))

    def test_simple_llm_call(self):
        """测试简单的LLM调用"""
        self.console.print("\n[bold blue]🧠 测试LLM调用[/bold blue]")
        
        try:
            from langchain_openai import ChatOpenAI
            
            backend_url = os.getenv("TRADINGAGENTS_BACKEND_URL")
            quick_model = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "gemini-2.5-flash")
            
            llm = ChatOpenAI(
                model=quick_model,
                base_url=backend_url,
                temperature=0.1
            )
            
            with self.console.status("[bold green]正在测试LLM调用..."):
                response = llm.invoke("Hello! Please respond with 'TradingAgents test successful'")
            
            if response and hasattr(response, 'content'):
                self.log_test("LLM调用测试", "PASS", f"响应: {response.content[:100]}...")
                return True
            else:
                self.log_test("LLM调用测试", "FAIL", "LLM返回异常响应")
                return False
                
        except Exception as e:
            self.log_test("LLM调用测试", "FAIL", "LLM调用失败", str(e))
            return False

    def test_data_sources(self):
        """测试数据源可用性"""
        self.console.print("\n[bold blue]📊 测试数据源可用性[/bold blue]")
        
        # 测试Yahoo Finance
        try:
            import yfinance as yf
            with self.console.status("[bold green]正在测试Yahoo Finance..."):
                ticker = yf.Ticker("AAPL")
                info = ticker.info
            if info:
                self.log_test("Yahoo Finance", "PASS", "数据获取成功")
            else:
                self.log_test("Yahoo Finance", "WARNING", "数据获取异常")
        except Exception as e:
            self.log_test("Yahoo Finance", "FAIL", "数据获取失败", str(e))
        
        # 测试FinnHub (如果配置了)
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        if finnhub_key:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={finnhub_key}"
                with self.console.status("[bold green]正在测试FinnHub..."):
                    response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_test("FinnHub API", "PASS", "连接成功")
                else:
                    self.log_test("FinnHub API", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("FinnHub API", "FAIL", "连接失败", str(e))
        else:
            self.log_test("FinnHub API", "WARNING", "未配置FinnHub API Key (可选)")

    def test_full_workflow_dry_run(self):
        """测试完整工作流程(不实际执行交易分析)"""
        self.console.print("\n[bold blue]🔄 测试完整工作流程初始化[/bold blue]")
        
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            
            with self.console.status("[bold green]正在初始化TradingAgents..."):
                ta = TradingAgentsGraph(debug=False, config=DEFAULT_CONFIG)
            
            self.log_test("TradingAgents初始化", "PASS", "系统初始化成功")
            
            # 检查关键组件
            if hasattr(ta, 'graph') and ta.graph:
                self.log_test("工作流图构建", "PASS", "LangGraph工作流构建成功")
            else:
                self.log_test("工作流图构建", "FAIL", "工作流图构建失败")
                
            if hasattr(ta, 'deep_thinking_llm') and hasattr(ta, 'quick_thinking_llm'):
                self.log_test("LLM实例化", "PASS", "深度和快速思考模型实例化成功")
            else:
                self.log_test("LLM实例化", "FAIL", "LLM实例化失败")
                
            return True
            
        except Exception as e:
            self.log_test("TradingAgents初始化", "FAIL", "系统初始化失败", str(e))
            return False

    def run_integration_test(self):
        """运行简单的端到端集成测试"""
        self.console.print("\n[bold blue]🧪 运行端到端集成测试[/bold blue]")
        
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            
            # 创建测试配置 - 减少API调用
            test_config = DEFAULT_CONFIG.copy()
            test_config["max_debate_rounds"] = 1
            test_config["max_risk_discuss_rounds"] = 1
            test_config["online_tools"] = True  # 使用在线工具获取实时数据
            
            self.console.print("⚠️  [yellow]注意: 这将进行实际的API调用，可能产生费用[/yellow]")
            
            with self.console.status("[bold green]正在运行完整交易分析流程..."):
                ta = TradingAgentsGraph(debug=True, config=test_config)
                
                # 使用一个简单的股票进行测试
                test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                final_state, decision = ta.propagate("AAPL", test_date)
            
            if decision and "FINAL TRANSACTION PROPOSAL" in decision:
                self.log_test("端到端集成测试", "PASS", f"完整流程执行成功")
                self.console.print(f"[green]决策结果预览: {decision[:200]}...[/green]")
                return True
            else:
                self.log_test("端到端集成测试", "WARNING", "流程完成但决策格式异常")
                return False
                
        except Exception as e:
            self.log_test("端到端集成测试", "FAIL", "端到端测试失败", str(e))
            return False

    def generate_test_report(self):
        """生成测试报告"""
        self.console.print("\n[bold blue]📋 测试报告[/bold blue]")
        
        table = Table(title="TradingAgents 系统健康检查报告")
        table.add_column("测试项目", style="cyan", no_wrap=True)
        table.add_column("状态", justify="center")
        table.add_column("结果", style="white")
        
        pass_count = 0
        fail_count = 0
        warning_count = 0
        
        for result in self.test_results:
            status_style = {
                "PASS": "[green]✅ PASS[/green]",
                "FAIL": "[red]❌ FAIL[/red]", 
                "WARNING": "[yellow]⚠️  WARNING[/yellow]",
                "INFO": "[blue]ℹ️  INFO[/blue]"
            }.get(result["status"], result["status"])
            
            table.add_row(
                result["test"],
                status_style,
                result["message"]
            )
            
            if result["status"] == "PASS":
                pass_count += 1
            elif result["status"] == "FAIL":
                fail_count += 1
            elif result["status"] == "WARNING":
                warning_count += 1
        
        self.console.print(table)
        
        # 总体评估
        total_tests = len(self.test_results)
        if fail_count == 0:
            if warning_count == 0:
                overall_status = "[bold green]🎉 系统完全正常，可以开始使用！[/bold green]"
            else:
                overall_status = "[bold yellow]⚠️  系统基本正常，有一些警告项需要注意[/bold yellow]"
        else:
            overall_status = "[bold red]❌ 系统存在问题，需要修复后再使用[/bold red]"
        
        self.console.print(f"\n{overall_status}")
        self.console.print(f"测试总数: {total_tests} | 通过: {pass_count} | 失败: {fail_count} | 警告: {warning_count}")
        
        return fail_count == 0

def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]TradingAgents 系统健康检查[/bold blue]\n"
        "验证系统配置和各组件是否正常工作",
        title="🚀 TradingAgents Health Check"
    ))
    
    checker = TradingAgentsHealthChecker()
    
    # 运行所有测试
    checker.test_environment_variables()
    checker.test_dependencies()
    checker.test_llm_api_connection()
    
    if checker.test_tradingagents_import():
        checker.test_configuration_loading()
        if checker.test_simple_llm_call():
            checker.test_data_sources()
            if checker.test_full_workflow_dry_run():
                # 询问是否运行完整集成测试
                console.print("\n[bold yellow]完整集成测试将执行实际的交易分析流程，会产生API调用费用。[/bold yellow]")
                response = input("是否运行完整集成测试？(y/N): ").lower().strip()
                if response in ['y', 'yes']:
                    checker.run_integration_test()
                else:
                    console.print("[blue]跳过完整集成测试[/blue]")
    
    # 生成报告
    system_healthy = checker.generate_test_report()
    
    if system_healthy:
        console.print("\n[bold green]🎊 恭喜！您的TradingAgents系统已经准备就绪！[/bold green]")
        console.print("您可以开始使用以下方式运行分析：")
        console.print("1. 使用CLI: [cyan]python -m cli.main[/cyan]")
        console.print("2. 使用Python API: [cyan]python main.py[/cyan]")
    else:
        console.print("\n[bold red]⚠️  请修复上述问题后再重新运行测试[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()