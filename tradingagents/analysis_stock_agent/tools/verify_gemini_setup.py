#!/usr/bin/env python3
"""
Gemini API密钥验证和模型发现工具

使用此脚本来：
1. 验证你的Google/Gemini API密钥是否可以正常工作
2. 发现当前可用的Gemini模型版本
3. 测试推荐模型的可用性

使用方法:
    python -m tradingagents.analysis_stock_agent.tools.verify_gemini_setup
    python -m tradingagents.analysis_stock_agent.tools.verify_gemini_setup --test-generation
    python -m tradingagents.analysis_stock_agent.tools.verify_gemini_setup --list-only
"""

import os
import sys
import argparse
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# 添加项目路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  警告: python-dotenv未安装，无法自动加载.env文件")
    print("   请手动设置环境变量或运行: pip install python-dotenv")

try:
    # 尝试导入Google Gen AI SDK
    from google import generativeai as genai
    from google.generativeai import types
except ImportError:
    try:
        # 如果没有，尝试从LangChain集成导入
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("⚠️  使用LangChain Google GenAI集成进行验证")
        USE_LANGCHAIN = True
    except ImportError:
        print("❌ 错误: 需要安装Google Generative AI SDK")
        print("   请运行以下命令之一:")
        print("   pip install google-generativeai  # 直接SDK")
        print("   或保持当前的 langchain-google-genai")
        sys.exit(1)
else:
    USE_LANGCHAIN = False


def get_api_key() -> Optional[str]:
    """
    从环境变量中获取API密钥
    
    Returns:
        API密钥字符串，如果未找到则返回None
    """
    # 按优先级尝试不同的环境变量
    key_vars = [
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY", 
        "GOOGLE_GENERATIVE_AI_API_KEY"
    ]
    
    for var in key_vars:
        api_key = os.getenv(var)
        if api_key:
            print(f"✅ 找到API密钥: {var}")
            return api_key
    
    return None


def verify_api_key(api_key: str) -> bool:
    """
    验证API密钥是否有效
    
    Args:
        api_key: API密钥
        
    Returns:
        API密钥是否有效
    """
    try:
        if USE_LANGCHAIN:
            # 使用LangChain集成验证
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=api_key,
                temperature=0
            )
            
            # 简单测试
            result = llm.invoke("Hello")
            if result and hasattr(result, 'content'):
                print("✅ API密钥验证成功！")
                return True
            else:
                print("❌ API密钥验证失败：无响应")
                return False
        else:
            # 使用直接SDK验证
            genai.configure(api_key=api_key)
            
            # 尝试列出模型（最简单的验证方法）
            models = list(genai.list_models())
            
            if models:
                print("✅ API密钥验证成功！")
                return True
            else:
                print("❌ API密钥验证失败：无法获取模型列表")
                return False
            
    except Exception as e:
        print(f"❌ API密钥验证失败: {str(e)}")
        return False


def list_available_models(api_key: str) -> List[Dict[str, Any]]:
    """
    列出所有可用的模型
    
    Args:
        api_key: API密钥
        
    Returns:
        模型信息列表
    """
    try:
        print("🔍 正在获取可用模型列表...")
        
        if USE_LANGCHAIN:
            # LangChain集成方式 - 返回已知的推荐模型
            print("⚠️  LangChain集成模式：显示推荐模型列表")
            known_models = [
                {
                    "name": "gemini-2.5-flash",
                    "display_name": "Gemini 2.5 Flash",
                    "description": "通用文本和多模态任务的推荐模型",
                    "input_token_limit": "1,000,000",
                    "output_token_limit": "8,192",
                    "supported_actions": ["generate_content"],
                    "version": "2.5"
                },
                {
                    "name": "gemini-2.5-pro",
                    "display_name": "Gemini 2.5 Pro", 
                    "description": "编程和复杂推理任务的推荐模型",
                    "input_token_limit": "2,000,000",
                    "output_token_limit": "8,192",
                    "supported_actions": ["generate_content"],
                    "version": "2.5"
                }
            ]
            return known_models
        else:
            # 直接SDK方式
            genai.configure(api_key=api_key)
            models = list(genai.list_models())
            
            model_info = []
            for model in models:
                info = {
                    "name": getattr(model, 'name', 'N/A'),
                    "display_name": getattr(model, 'display_name', 'N/A'),
                    "description": getattr(model, 'description', 'N/A'),
                    "input_token_limit": getattr(model, 'input_token_limit', 'N/A'),
                    "output_token_limit": getattr(model, 'output_token_limit', 'N/A'),
                    "supported_actions": getattr(model, 'supported_generation_methods', []),
                    "version": getattr(model, 'version', 'N/A')
                }
                model_info.append(info)
            
            return model_info
        
    except Exception as e:
        print(f"❌ 获取模型列表失败: {str(e)}")
        return []


def test_recommended_models(api_key: str) -> Dict[str, bool]:
    """
    测试推荐模型的可用性
    
    Args:
        api_key: API密钥
        
    Returns:
        模型可用性字典
    """
    recommended_models = {
        "gemini-2.5-flash": "通用文本和多模态任务",
        "gemini-2.5-pro": "编程和复杂推理任务"
    }
    
    results = {}
    
    for model_name, description in recommended_models.items():
        try:
            print(f"🧪 测试模型: {model_name} ({description})")
            
            if USE_LANGCHAIN:
                # LangChain集成方式
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0,
                    max_output_tokens=50
                )
                
                # 简单的生成测试
                result = llm.invoke("Hello! Please respond with 'API test successful'")
                
                if result and hasattr(result, 'content') and result.content:
                    print(f"   ✅ {model_name}: 可用")
                    print(f"   📝 响应: {result.content.strip()}")
                    results[model_name] = True
                else:
                    print(f"   ❌ {model_name}: 无响应")
                    results[model_name] = False
            else:
                # 直接SDK方式
                genai.configure(api_key=api_key)
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    "Hello! Please respond with 'API test successful'",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=50,
                        candidate_count=1
                    )
                )
                
                if response and response.text:
                    print(f"   ✅ {model_name}: 可用")
                    print(f"   📝 响应: {response.text.strip()}")
                    results[model_name] = True
                else:
                    print(f"   ❌ {model_name}: 无响应")
                    results[model_name] = False
                
        except Exception as e:
            print(f"   ❌ {model_name}: 测试失败 - {str(e)}")
            results[model_name] = False
    
    return results


def format_model_info(models: List[Dict[str, Any]]) -> None:
    """
    格式化显示模型信息
    
    Args:
        models: 模型信息列表
    """
    if not models:
        print("❌ 没有找到可用的模型")
        return
    
    print(f"\n📋 找到 {len(models)} 个可用模型:")
    print("=" * 80)
    
    # 按模型名称排序
    models.sort(key=lambda x: x.get('name', ''))
    
    # 筛选Gemini模型
    gemini_models = [m for m in models if 'gemini' in m.get('name', '').lower()]
    other_models = [m for m in models if 'gemini' not in m.get('name', '').lower()]
    
    if gemini_models:
        print("\n🔸 Gemini模型:")
        for model in gemini_models:
            name = model.get('name', 'N/A')
            display_name = model.get('display_name', 'N/A')
            description = model.get('description', 'N/A')
            input_limit = model.get('input_token_limit', 'N/A')
            output_limit = model.get('output_token_limit', 'N/A')
            
            print(f"   📍 {name}")
            if display_name != 'N/A':
                print(f"      显示名称: {display_name}")
            if description != 'N/A' and len(description) < 100:
                print(f"      描述: {description}")
            if input_limit != 'N/A':
                print(f"      输入限制: {input_limit} tokens")
            if output_limit != 'N/A':
                print(f"      输出限制: {output_limit} tokens")
            print()
    
    if other_models:
        print("\n🔸 其他模型:")
        for model in other_models:
            name = model.get('name', 'N/A')
            display_name = model.get('display_name', 'N/A')
            print(f"   📍 {name}")
            if display_name != 'N/A':
                print(f"      显示名称: {display_name}")
            print()


def save_report(api_key_valid: bool, models: List[Dict[str, Any]], 
                model_tests: Optional[Dict[str, bool]] = None) -> str:
    """
    保存验证报告
    
    Args:
        api_key_valid: API密钥是否有效
        models: 模型列表
        model_tests: 模型测试结果
        
    Returns:
        报告文件路径
    """
    try:
        # 创建报告目录
        report_dir = Path("results")
        report_dir.mkdir(exist_ok=True)
        
        # 生成报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"gemini_setup_verification_{timestamp}.json"
        
        report_data = {
            "timestamp": timestamp,
            "api_key_valid": api_key_valid,
            "total_models": len(models),
            "models": models,
            "model_tests": model_tests or {},
            "recommended_models": {
                "gemini-2.5-flash": "通用文本和多模态任务",
                "gemini-2.5-pro": "编程和复杂推理任务"
            },
            "deprecated_models": [
                "gemini-1.5-flash",
                "gemini-1.5-pro", 
                "gemini-pro"
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return str(report_file)
        
    except Exception as e:
        print(f"⚠️  保存报告失败: {str(e)}")
        return ""


def print_summary(api_key_valid: bool, models: List[Dict[str, Any]], 
                  model_tests: Optional[Dict[str, bool]] = None) -> None:
    """
    打印验证摘要
    
    Args:
        api_key_valid: API密钥是否有效
        models: 模型列表
        model_tests: 模型测试结果
    """
    print("\n" + "=" * 60)
    print("📊 Gemini设置验证摘要")
    print("=" * 60)
    
    # API密钥状态
    print(f"🔑 API密钥状态: {'✅ 有效' if api_key_valid else '❌ 无效'}")
    
    # 模型统计
    print(f"📋 可用模型数量: {len(models)}")
    
    if models:
        gemini_models = [m for m in models if 'gemini' in m.get('name', '').lower()]
        print(f"🔸 Gemini模型数量: {len(gemini_models)}")
        
        # 检查推荐模型
        recommended_available = []
        recommended_models = ["gemini-2.5-flash", "gemini-2.5-pro"]
        
        for model in models:
            model_name = model.get('name', '')
            for recommended in recommended_models:
                if recommended in model_name:
                    recommended_available.append(recommended)
        
        print(f"✨ 推荐模型可用: {len(recommended_available)}/{len(recommended_models)}")
        for model in recommended_available:
            print(f"   ✅ {model}")
        
        missing_recommended = set(recommended_models) - set(recommended_available)
        for model in missing_recommended:
            print(f"   ❌ {model} (不可用)")
    
    # 测试结果
    if model_tests:
        successful_tests = sum(1 for success in model_tests.values() if success)
        print(f"🧪 模型测试: {successful_tests}/{len(model_tests)} 成功")
        
        for model, success in model_tests.items():
            status = "✅" if success else "❌"
            print(f"   {status} {model}")
    
    # 建议
    print("\n💡 建议:")
    if not api_key_valid:
        print("   ❌ 请检查你的GOOGLE_API_KEY环境变量设置")
        print("   📖 获取API密钥: https://ai.google.dev/")
    elif not models:
        print("   ❌ 无法获取模型列表，请检查网络连接和API权限")
    elif len(recommended_available) < len(recommended_models):
        print("   ⚠️  部分推荐模型不可用，可能影响系统性能")
    else:
        print("   🎉 Gemini设置完成，可以开始使用A股分析系统！")
    
    print("\n🚀 下一步:")
    print("   python -m tradingagents.analysis_stock_agent.main 002594 --debug")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Gemini API密钥验证和模型发现工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                           # 完整验证
  %(prog)s --test-generation         # 包含生成测试
  %(prog)s --list-only               # 仅列出模型
  %(prog)s --save-report             # 保存详细报告
        """
    )
    
    parser.add_argument(
        '--test-generation',
        action='store_true',
        help='测试推荐模型的内容生成功能'
    )
    
    parser.add_argument(
        '--list-only',
        action='store_true',
        help='仅列出可用模型，不进行验证测试'
    )
    
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='保存详细的JSON格式验证报告'
    )
    
    args = parser.parse_args()
    
    print("🔍 Gemini API设置验证工具")
    print("=" * 60)
    
    try:
        # 1. 获取API密钥
        print("🔑 正在检查API密钥...")
        api_key = get_api_key()
        
        if not api_key:
            print("❌ 未找到API密钥")
            print("\n💡 请设置以下环境变量之一:")
            print("   export GOOGLE_API_KEY=your_api_key_here")
            print("   export GEMINI_API_KEY=your_api_key_here")
            print("\n📖 或在.env文件中配置:")
            print("   GOOGLE_API_KEY=your_api_key_here")
            sys.exit(1)
        
        # 2. 验证API密钥
        api_key_valid = False
        if not args.list_only:
            print("🔒 正在验证API密钥...")
            api_key_valid = verify_api_key(api_key)
            
            if not api_key_valid:
                print("❌ API密钥验证失败，请检查密钥是否正确")
                sys.exit(1)
        
        # 3. 获取模型列表
        models = list_available_models(api_key)
        
        # 4. 显示模型信息
        format_model_info(models)
        
        # 5. 测试推荐模型（如果请求）
        model_tests = None
        if args.test_generation and api_key_valid:
            print("\n🧪 正在测试推荐模型...")
            model_tests = test_recommended_models(api_key)
        
        # 6. 保存报告（如果请求）
        if args.save_report:
            print("\n💾 正在保存验证报告...")
            report_file = save_report(api_key_valid, models, model_tests)
            if report_file:
                print(f"📄 报告已保存: {report_file}")
        
        # 7. 显示摘要
        print_summary(api_key_valid, models, model_tests)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断了验证过程")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {str(e)}")
        print("\n🔧 详细错误信息:")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()