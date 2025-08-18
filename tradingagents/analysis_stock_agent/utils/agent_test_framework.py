"""
Agent测试框架

提供独立测试每个Agent的基础设施，绕过LangGraph复杂性
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent.config.a_share_config import A_SHARE_DEFAULT_CONFIG
from tradingagents.analysis_stock_agent.utils.llm_utils import LLMManager


class AgentTestFramework:
    """Agent独立测试框架"""
    
    def __init__(self, debug: bool = True):
        """
        初始化测试框架
        
        Args:
            debug: 是否启用详细调试
        """
        self.debug = debug
        self.config = A_SHARE_DEFAULT_CONFIG.copy()
        self.llm_manager = None
        self.test_start_time = datetime.now()
        
        # 设置日志
        self._setup_logging()
        
        # 加载环境变量
        self._load_environment()
        
        # 初始化LLM管理器
        self._initialize_llm()
        
        self.logger = logging.getLogger(__name__)
        
    def _setup_logging(self):
        """配置详细日志"""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def _load_environment(self):
        """加载环境变量"""
        # 尝试加载.env文件
        env_files = [
            Path.cwd() / '.env',
            Path.cwd() / 'tradingagents' / 'analysis_stock_agent' / '.env',
            Path.home() / '.env'
        ]
        
        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file)
                print(f"✅ 已加载环境变量文件: {env_file}")
                break
        else:
            print("⚠️  未找到.env文件，将使用系统环境变量")
            
    def _initialize_llm(self):
        """初始化LLM管理器"""
        try:
            self.llm_manager = LLMManager(self.config)
            print("✅ LLM管理器初始化成功")
        except Exception as e:
            print(f"❌ LLM管理器初始化失败: {str(e)}")
            self.llm_manager = None
            
    def get_test_llm(self, model_name: Optional[str] = None):
        """
        获取测试用LLM实例
        
        Args:
            model_name: 模型名称，默认使用深度思考模型
            
        Returns:
            LLM实例
        """
        if not self.llm_manager:
            raise RuntimeError("LLM管理器未初始化")
            
        model = model_name or self.config.get("deep_think_llm", "gemini-2.5-pro")
        return self.llm_manager.get_llm(model)
        
    def create_mock_state(self, stock_code: str = "002594", 
                         stock_name: str = "比亚迪") -> Dict[str, Any]:
        """
        创建模拟状态数据
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            模拟状态字典
        """
        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "analyst_name": "AI测试分析师",
            "analysis_depth": "comprehensive",
            "messages": [],
            "data_sources": [],
            "last_updated": datetime.now().isoformat()
        }
        
    def run_agent_test(self, agent_name: str, agent_function, 
                      mock_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行Agent测试
        
        Args:
            agent_name: Agent名称
            agent_function: Agent函数
            mock_state: 模拟状态
            
        Returns:
            测试结果
        """
        print(f"\n{'='*60}")
        print(f"🧪 测试Agent: {agent_name}")
        print(f"📈 股票代码: {mock_state.get('stock_code', 'N/A')}")
        print(f"🕒 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # 运行Agent
            result = agent_function(mock_state)
            
            print(f"\n✅ {agent_name} 执行成功")
            print(f"📊 返回字段数: {len(result.keys()) if isinstance(result, dict) else 'N/A'}")
            
            if isinstance(result, dict):
                print(f"🔑 返回字段: {list(result.keys())}")
                
                # 检查关键字段
                if "messages" in result:
                    print(f"💬 消息数量: {len(result['messages']) if result['messages'] else 0}")
                    
                if "data_sources" in result:
                    print(f"📚 数据源: {result['data_sources']}")
                    
                # 显示报告内容（如果有）
                report_fields = [
                    "financial_analysis_report",
                    "industry_analysis_report", 
                    "valuation_analysis_report",
                    "comprehensive_analysis_report"
                ]
                
                for field in report_fields:
                    if field in result and result[field]:
                        print(f"📄 {field}: {len(str(result[field]))} 字符")
                        if self.debug:
                            print(f"📄 内容预览: {str(result[field])[:200]}...")
                            
            return {
                "success": True,
                "agent_name": agent_name,
                "result": result,
                "execution_time": (datetime.now() - self.test_start_time).total_seconds()
            }
            
        except Exception as e:
            print(f"\n❌ {agent_name} 执行失败")
            print(f"🔥 错误类型: {type(e).__name__}")
            print(f"💥 错误信息: {str(e)}")
            
            if self.debug:
                import traceback
                print(f"📚 详细堆栈:")
                traceback.print_exc()
                
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": (datetime.now() - self.test_start_time).total_seconds()
            }
            
    def print_test_summary(self, test_results: list):
        """
        打印测试总结
        
        Args:
            test_results: 测试结果列表
        """
        print(f"\n{'='*60}")
        print("📊 测试总结")
        print(f"{'='*60}")
        
        successful_tests = [r for r in test_results if r.get("success", False)]
        failed_tests = [r for r in test_results if not r.get("success", False)]
        
        print(f"✅ 成功: {len(successful_tests)}/{len(test_results)}")
        print(f"❌ 失败: {len(failed_tests)}/{len(test_results)}")
        
        if successful_tests:
            print(f"\n🎉 成功的Agent:")
            for result in successful_tests:
                print(f"  ✅ {result['agent_name']} ({result['execution_time']:.2f}s)")
                
        if failed_tests:
            print(f"\n💥 失败的Agent:")
            for result in failed_tests:
                print(f"  ❌ {result['agent_name']}: {result.get('error_type', 'Unknown')}")
                
        total_time = (datetime.now() - self.test_start_time).total_seconds()
        print(f"\n⏱️  总执行时间: {total_time:.2f}秒")
        print(f"{'='*60}")


def create_test_framework(debug: bool = True) -> AgentTestFramework:
    """
    创建测试框架实例
    
    Args:
        debug: 是否启用调试模式
        
    Returns:
        测试框架实例
    """
    return AgentTestFramework(debug=debug)


if __name__ == "__main__":
    # 测试框架本身
    print("🧪 测试Agent测试框架")
    
    framework = create_test_framework(debug=True)
    mock_state = framework.create_mock_state()
    
    print(f"✅ 测试框架初始化成功")
    print(f"🔧 LLM管理器状态: {'已初始化' if framework.llm_manager else '未初始化'}")
    print(f"📊 模拟状态字段: {list(mock_state.keys())}")
    
    if framework.llm_manager:
        try:
            llm = framework.get_test_llm()
            print(f"✅ 获取测试LLM成功: {llm}")
        except Exception as e:
            print(f"❌ 获取测试LLM失败: {e}")
    
    print("🎉 测试框架验证完成")