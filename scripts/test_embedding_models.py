#!/usr/bin/env python3
"""
TradingAgents Embedding模型测试脚本
用于测试自定义endpoint支持哪些embedding模型
"""

import os
import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

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
        console.print("✅ 已加载 .env 文件")
    else:
        console.print("⚠️  未找到 .env 文件")

def test_endpoint_connection():
    """测试endpoint连接"""
    backend_url = os.getenv("TRADINGAGENTS_BACKEND_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not backend_url or not api_key:
        console.print("[red]❌ 缺少必要的配置：TRADINGAGENTS_BACKEND_URL 或 OPENAI_API_KEY[/red]")
        return False, None, None
    
    console.print(f"[blue]🔗 测试endpoint: {backend_url}[/blue]")
    console.print(f"[blue]🔑 API Key: {api_key[:8]}...{api_key[-4:]}[/blue]")
    
    return True, backend_url, api_key

def get_available_models(backend_url, api_key):
    """获取endpoint支持的所有模型"""
    try:
        models_url = f"{backend_url.rstrip('/')}/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        with console.status("[bold green]正在获取可用模型列表..."):
            response = requests.get(models_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                all_models = [model.get("id", "unknown") for model in data["data"]]
                embedding_models = [model for model in all_models if "embed" in model.lower()]
                
                console.print(f"[green]✅ 成功获取模型列表: 总共 {len(all_models)} 个模型[/green]")
                console.print(f"[green]📊 Embedding模型: {len(embedding_models)} 个[/green]")
                
                return all_models, embedding_models
            else:
                console.print("[yellow]⚠️  API响应格式异常[/yellow]")
                return [], []
        else:
            console.print(f"[red]❌ API请求失败: HTTP {response.status_code}[/red]")
            console.print(f"[red]响应内容: {response.text[:200]}[/red]")
            return [], []
            
    except requests.exceptions.Timeout:
        console.print("[red]❌ 请求超时[/red]")
        return [], []
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ 无法连接到API端点[/red]")
        return [], []
    except Exception as e:
        console.print(f"[red]❌ 获取模型列表失败: {e}[/red]")
        return [], []

def test_embedding_model(backend_url, api_key, model_name):
    """测试特定的embedding模型"""
    try:
        embeddings_url = f"{backend_url.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "input": "This is a test sentence for embedding."
        }
        
        response = requests.post(embeddings_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                embedding_length = len(data["data"][0]["embedding"])
                return True, f"向量维度: {embedding_length}", None
            else:
                return False, "响应格式异常", "API返回数据格式不正确"
        else:
            error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
            return False, error_msg, response.text
            
    except requests.exceptions.Timeout:
        return False, "请求超时", "Embedding API响应超时"
    except requests.exceptions.ConnectionError:
        return False, "连接失败", "无法连接到Embedding API端点"
    except Exception as e:
        return False, str(e), f"测试过程中发生异常: {e}"

def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold blue]TradingAgents Embedding模型测试工具[/bold blue]\n"
        "测试您的自定义endpoint支持哪些embedding模型",
        title="🧪 Embedding模型测试"
    ))
    
    # 加载环境变量
    load_env_file()
    
    # 测试连接
    success, backend_url, api_key = test_endpoint_connection()
    if not success:
        return
    
    # 获取可用模型
    all_models, embedding_models = get_available_models(backend_url, api_key)
    
    if not all_models:
        console.print("[red]❌ 无法获取模型列表，无法继续测试[/red]")
        return
    
    # 显示所有模型
    if all_models:
        console.print("\n[bold cyan]📋 所有可用模型:[/bold cyan]")
        models_table = Table(title="全部模型列表")
        models_table.add_column("序号", justify="right", style="cyan")
        models_table.add_column("模型名称", style="white")
        models_table.add_column("类型", style="green")
        
        for i, model in enumerate(all_models, 1):
            model_type = "🧠 Embedding" if "embed" in model.lower() else "💬 Chat/Text"
            models_table.add_row(str(i), model, model_type)
        
        console.print(models_table)
    
    # 如果找到embedding模型，进行详细测试
    if embedding_models:
        console.print(f"\n[bold green]🎯 发现 {len(embedding_models)} 个Embedding模型，开始详细测试...[/bold green]")
        
        # 创建测试结果表格
        results_table = Table(title="Embedding模型测试结果")
        results_table.add_column("模型名称", style="cyan")
        results_table.add_column("状态", justify="center")
        results_table.add_column("结果", style="white")
        results_table.add_column("备注", style="dim")
        
        # 测试每个embedding模型
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for model in embedding_models:
                task = progress.add_task(f"测试 {model}...", total=None)
                
                success, result, error = test_embedding_model(backend_url, api_key, model)
                
                if success:
                    status = "[green]✅ 可用[/green]"
                    note = "推荐使用"
                else:
                    status = "[red]❌ 不可用[/red]" 
                    note = "跳过"
                
                results_table.add_row(model, status, result, note)
                progress.remove_task(task)
        
        console.print(results_table)
        
        # 提供配置建议
        working_models = []
        for model in embedding_models:
            success, _, _ = test_embedding_model(backend_url, api_key, model)
            if success:
                working_models.append(model)
        
        if working_models:
            console.print(f"\n[bold green]🎉 找到 {len(working_models)} 个可用的Embedding模型！[/bold green]")
            console.print("\n[bold blue]📝 推荐配置：[/bold blue]")
            
            # 推荐最佳模型
            best_model = working_models[0]  # 简单选择第一个可用的
            console.print(f"在您的 .env 文件中设置：")
            console.print(f"[green]TRADINGAGENTS_EMBEDDING_MODEL={best_model}[/green]")
            
            console.print(f"\n[blue]💡 其他可选模型：[/blue]")
            for model in working_models[1:]:
                console.print(f"   • {model}")
                
        else:
            console.print("[red]❌ 没有找到可用的Embedding模型[/red]")
            console.print("\n[yellow]🔧 解决建议：[/yellow]")
            console.print("1. 检查您的API密钥是否正确")
            console.print("2. 确认您的endpoint是否支持embeddings API")
            console.print("3. 联系服务提供商询问embedding模型支持情况")
    
    else:
        console.print("[yellow]⚠️  在模型列表中未找到embedding相关模型[/yellow]")
        
        # 尝试测试常见的embedding模型名称
        common_embedding_models = [
            "text-embedding-3-small",
            "text-embedding-3-large", 
            "text-embedding-ada-002",
            "text-embedding-005",
            "embedding-001",
            "bge-large-zh-v1.5",
            "m3e-base",
            "nomic-embed-text"
        ]
        
        console.print(f"\n[blue]🔍 尝试测试常见的Embedding模型...[/blue]")
        
        working_models = []
        test_table = Table(title="常见Embedding模型测试")
        test_table.add_column("模型名称", style="cyan")
        test_table.add_column("状态", justify="center")
        test_table.add_column("结果")
        
        for model in common_embedding_models:
            success, result, _ = test_embedding_model(backend_url, api_key, model)
            if success:
                status = "[green]✅ 可用[/green]"
                working_models.append(model)
            else:
                status = "[red]❌ 不可用[/red]"
            
            test_table.add_row(model, status, result)
        
        console.print(test_table)
        
        if working_models:
            console.print(f"\n[green]🎉 找到 {len(working_models)} 个可用的Embedding模型！[/green]")
            console.print(f"[green]推荐使用: {working_models[0]}[/green]")
        else:
            console.print("\n[red]❌ 测试的常见模型都不可用[/red]")
    
    console.print(f"\n[bold blue]🔗 测试的endpoint: {backend_url}/embeddings[/bold blue]")
    console.print("[dim]如需了解更多，请查看服务商的API文档[/dim]")

if __name__ == "__main__":
    main()