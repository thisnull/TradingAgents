"""
Agent测试框架

提供独立测试每个Agent的基础设施，绕过LangGraph复杂性
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
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
            
    def save_analysis_report(self, agent_name: str, stock_code: str, 
                           agent_result: Dict[str, Any], 
                           output_dir: str = "test_reports") -> str:
        """
        保存Agent分析报告到文件
        
        Args:
            agent_name: Agent名称
            stock_code: 股票代码
            agent_result: Agent分析结果
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        try:
            # 创建输出目录
            report_dir = Path.cwd() / output_dir
            report_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{agent_name}_{stock_code}_{timestamp}.md"
            filepath = report_dir / filename
            
            # 构建报告内容
            report_content = self._build_report_content(agent_name, stock_code, agent_result)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
            print(f"📄 分析报告已保存: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return ""
    
    def _build_report_content(self, agent_name: str, stock_code: str, 
                            agent_result: Dict[str, Any]) -> str:
        """
        构建报告内容
        
        Args:
            agent_name: Agent名称
            stock_code: 股票代码
            agent_result: Agent分析结果
            
        Returns:
            格式化的报告内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# {agent_name} 分析报告

## 📊 基本信息
- **股票代码**: {stock_code}
- **分析时间**: {timestamp}
- **Agent类型**: {agent_name}
- **分析深度**: 独立测试

## 🤖 LLM消息与工具调用
"""
        
        # 分析messages内容
        if "messages" in agent_result and agent_result["messages"]:
            message = agent_result["messages"][0]
            
            # 显示完整的LLM回复内容
            if hasattr(message, 'content') and message.content:
                report += f"""
### 💬 LLM完整回复内容
```
{message.content}
```
"""
            
            # 工具调用信息
            if hasattr(message, 'tool_calls') and message.tool_calls:
                report += f"""
### 🔧 工具调用详情
共调用 {len(message.tool_calls)} 个工具:

"""
                for i, tool_call in enumerate(message.tool_calls, 1):
                    report += f"""
#### 工具调用 {i}
- **工具名称**: {tool_call.get('name', 'Unknown')}
- **工具ID**: {tool_call.get('id', 'Unknown')}
- **参数**:
```json
{json.dumps(tool_call.get('args', {}), indent=2, ensure_ascii=False)}
```
"""

        # ===== 核心部分：显示Agent分析报告原文 =====
        report += """
## 📊 Agent分析结果原文

以下是Agent生成的完整分析报告内容：

"""
        
        # 显示各类分析报告的完整原文
        report_fields = [
            ("financial_analysis_report", "📊 财务分析报告原文"),
            ("industry_analysis_report", "🏭 行业分析报告原文"),
            ("valuation_analysis_report", "💰 估值分析报告原文"),
            ("comprehensive_analysis_report", "🎯 综合分析报告原文")
        ]
        
        for field_key, field_title in report_fields:
            if field_key in agent_result and agent_result[field_key]:
                report_content = str(agent_result[field_key])
                report += f"""
### {field_title}

{report_content}

---

"""
        
        # 显示其他重要数据的原文
        data_fields = [
            ("financial_data", "💰 财务数据"),
            ("industry_data", "🏭 行业数据"),
            ("key_financial_metrics", "📊 关键财务指标"),
            ("key_industry_metrics", "🏭 关键行业指标"),
            ("key_valuation_metrics", "💰 关键估值指标"),
            ("integration_data", "🔗 整合数据"),
            ("competitive_position", "🥇 竞争地位"),
            ("investment_recommendation", "💡 投资建议"),
            ("comprehensive_score", "📊 综合评分"),
            ("final_conclusion", "🎯 最终结论")
        ]
        
        has_data_section = False
        data_section_content = ""
        
        for field_key, field_title in data_fields:
            if field_key in agent_result and agent_result[field_key]:
                if not has_data_section:
                    has_data_section = True
                    data_section_content += "## 📈 Agent产出的关键数据\n\n"
                
                data_content = agent_result[field_key]
                
                if isinstance(data_content, (dict, list)):
                    data_section_content += f"""
### {field_title}
```json
{json.dumps(data_content, indent=2, ensure_ascii=False)}
```

"""
                else:
                    data_section_content += f"""
### {field_title}
```
{data_content}
```

"""
        
        if has_data_section:
            report += data_section_content
        
        # 数据源信息
        if "data_sources" in agent_result and agent_result["data_sources"]:
            sources = agent_result["data_sources"]
            report += f"""
## 📚 数据来源
```json
{json.dumps(sources, indent=2, ensure_ascii=False)}
```

"""

        # 元数据信息
        meta_fields = ["analysis_stage", "last_updated", "analysis_completed"]
        for field in meta_fields:
            if field in agent_result:
                value = agent_result[field]
                report += f"""
### 📋 {field}
```
{value}
```

"""
        
        report += f"""
---
**报告生成时间**: {timestamp}  
**测试框架版本**: v2.0 (原文展示版)  
**说明**: 本报告重点展示Agent输出的原始分析内容，便于评估分析质量
"""
        
        return report
    
    def print_test_summary(self, test_results: List[Dict[str, Any]]):
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