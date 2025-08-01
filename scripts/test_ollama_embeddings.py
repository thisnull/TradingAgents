#!/usr/bin/env python3
"""
TradingAgents Ollama Embedding模型测试脚本
用于测试本地ollama支持哪些embedding模型
"""

import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def test_ollama_connection(ollama_url):
    """测试ollama连接"""
    console.print(f"[blue]🔗 测试ollama endpoint: {ollama_url}[/blue]")
    
    try:
        # 测试ollama是否在线
        response = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=5)
        if response.status_code == 200:
            console.print("[green]✅ Ollama连接成功[/green]")
            return True
        else:
            console.print(f"[red]❌ Ollama连接失败: HTTP {response.status_code}[/red]")
            return False
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ 无法连接到Ollama，请确保Ollama正在运行[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ 连接测试失败: {e}[/red]")
        return False

def get_ollama_models(ollama_url):
    """获取ollama所有模型"""
    try:
        response = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "models" in data:
                all_models = [model["name"] for model in data["models"]]
                
                # 识别可能的embedding模型
                embedding_models = []
                for model in all_models:
                    # 常见的embedding模型名称特征
                    if any(keyword in model.lower() for keyword in [
                        'embed', 'embedding', 'bge', 'm3e', 'nomic', 'gte', 'e5',
                        'sentence', 'text2vec', 'multilingual'
                    ]):
                        embedding_models.append(model)
                
                console.print(f"[green]✅ 成功获取模型列表: 总共 {len(all_models)} 个模型[/green]")
                console.print(f"[green]📊 可能的Embedding模型: {len(embedding_models)} 个[/green]")
                
                return all_models, embedding_models
            else:
                console.print("[yellow]⚠️  API响应格式异常[/yellow]")
                return [], []
        else:
            console.print(f"[red]❌ API请求失败: HTTP {response.status_code}[/red]")
            console.print(f"[red]响应内容: {response.text[:200]}[/red]")
            return [], []
            
    except Exception as e:
        console.print(f"[red]❌ 获取模型列表失败: {e}[/red]")
        return [], []

def test_ollama_embedding(ollama_url, model_name):
    """测试ollama embedding模型"""
    try:
        embed_url = f"{ollama_url.rstrip('/')}/api/embeddings"
        payload = {
            "model": model_name,
            "prompt": "This is a test sentence for embedding."
        }
        
        response = requests.post(embed_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "embedding" in data and len(data["embedding"]) > 0:
                embedding_length = len(data["embedding"])
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
        "[bold blue]TradingAgents Ollama Embedding模型测试工具[/bold blue]\n"
        "测试您的本地ollama支持哪些embedding模型",
        title="🦙 Ollama Embedding测试"
    ))
    
    ollama_url = "http://localhost:10000"
    
    # 测试连接
    if not test_ollama_connection(ollama_url):
        console.print("\n[red]❌ 请确保Ollama正在运行并监听端口10000[/red]")
        console.print("[yellow]💡 启动命令示例: ollama serve --host 0.0.0.0:10000[/yellow]")
        return
    
    # 获取可用模型
    all_models, potential_embedding_models = get_ollama_models(ollama_url)
    
    if not all_models:
        console.print("[red]❌ 无法获取模型列表，无法继续测试[/red]")
        return
    
    # 显示所有模型
    console.print("\n[bold cyan]📋 所有可用模型:[/bold cyan]")
    models_table = Table(title="Ollama模型列表")
    models_table.add_column("序号", justify="right", style="cyan")
    models_table.add_column("模型名称", style="white")
    models_table.add_column("类型推测", style="green")
    
    for i, model in enumerate(all_models, 1):
        if model in potential_embedding_models:
            model_type = "🧠 可能是Embedding"
        else:
            model_type = "💬 Chat/Text"
        models_table.add_row(str(i), model, model_type)
    
    console.print(models_table)
    
    # 如果找到潜在embedding模型，进行详细测试
    if potential_embedding_models:
        console.print(f"\n[bold green]🎯 发现 {len(potential_embedding_models)} 个可能的Embedding模型，开始详细测试...[/bold green]")
        
        # 创建测试结果表格
        results_table = Table(title="Embedding模型测试结果")
        results_table.add_column("模型名称", style="cyan")
        results_table.add_column("状态", justify="center")
        results_table.add_column("结果", style="white")
        results_table.add_column("备注", style="dim")
        
        working_models = []
        
        # 测试每个可能的embedding模型
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for model in potential_embedding_models:
                task = progress.add_task(f"测试 {model}...", total=None)
                
                success, result, error = test_ollama_embedding(ollama_url, model)
                
                if success:
                    status = "[green]✅ 可用[/green]"
                    note = "推荐使用"
                    working_models.append(model)
                else:
                    status = "[red]❌ 不可用[/red]" 
                    note = "跳过"
                
                results_table.add_row(model, status, result, note)
                progress.remove_task(task)
        
        console.print(results_table)
        
        # 提供配置建议
        if working_models:
            console.print(f"\n[bold green]🎉 找到 {len(working_models)} 个可用的Embedding模型！[/bold green]")
            console.print("\n[bold blue]📝 推荐配置：[/bold blue]")
            
            # 推荐最佳模型
            best_model = working_models[0]
            console.print("在您的 .env 文件中设置：")
            console.print(f"[green]# 使用Ollama提供embedding服务[/green]")
            console.print(f"[green]TRADINGAGENTS_LLM_PROVIDER=openai[/green]")
            console.print(f"[green]TRADINGAGENTS_EMBEDDING_BACKEND_URL=http://localhost:10000[/green]")
            console.print(f"[green]TRADINGAGENTS_EMBEDDING_MODEL={best_model}[/green]")
            
            console.print(f"\n[blue]💡 其他可选模型：[/blue]")
            for model in working_models[1:]:
                console.print(f"   • {model}")
                
        else:
            console.print("[red]❌ 测试的模型都不支持embedding功能[/red]")
    
    else:
        console.print("[yellow]⚠️  在模型列表中未找到明显的embedding模型[/yellow]")
        
        # 建议一些常见的ollama embedding模型
        suggested_models = [
            "nomic-embed-text",
            "bge-large-en-v1.5", 
            "bge-base-en-v1.5",
            "all-minilm",
            "sentence-transformers",
            "gte-large"
        ]
        
        console.print(f"\n[blue]💡 建议下载的Embedding模型：[/blue]")
        download_table = Table(title="推荐的Embedding模型")
        download_table.add_column("模型名称", style="cyan")
        download_table.add_column("下载命令", style="green")
        download_table.add_column("说明", style="dim")
        
        for model in suggested_models:
            download_table.add_row(
                model, 
                f"ollama pull {model}",
                "通用文本embedding"
            )
        
        console.print(download_table)
    
    console.print(f"\n[bold blue]🔗 测试的ollama endpoint: {ollama_url}/api/embeddings[/bold blue]")
    console.print("[dim]如需了解更多ollama模型，请访问 https://ollama.ai/library[/dim]")

if __name__ == "__main__":
    main()