# TradingAgents 系统测试指南

## 🚀 测试步骤

我为您创建了两个测试脚本来验证系统是否正常工作：

### 1. 快速测试（推荐先运行）

```bash
python quick_test.py
```

**快速测试包括**：
- ✅ 环境变量检查
- ✅ 模块导入测试  
- ✅ 配置加载验证
- ✅ 系统初始化测试
- ✅ LLM连接测试
- ✅ 可选的迷你分析测试

**预期输出**：
```
🚀 TradingAgents 快速测试开始...

1️⃣ 检查环境变量...
   ✅ OPENAI_API_KEY: sk-proj-...xyz
   ✅ TRADINGAGENTS_BACKEND_URL: https://your-api.com/v1

2️⃣ 测试模块导入...
   ✅ 核心模块导入成功

3️⃣ 测试配置加载...
   ✅ LLM Provider: openai
   ✅ Backend URL: https://your-api.com/v1
   ✅ Deep Think Model: deepseek-r1
   ✅ Quick Think Model: gemini-2.5-flash

4️⃣ 测试系统初始化...
   ✅ TradingAgents 初始化成功

5️⃣ 测试LLM连接（快速）...
   ✅ LLM响应: 测试成功...

🎉 快速测试完成！系统基本配置正确。
```

### 2. 完整系统健康检查

```bash
python test_system.py
```

**完整测试包括**：
- 🔧 环境变量详细检查
- 📦 依赖包安装验证
- 🌐 LLM API连接测试
- 🏗️ TradingAgents核心模块测试
- ⚙️ 配置加载测试
- 🧠 LLM调用测试
- 📊 数据源可用性测试
- 🔄 完整工作流程初始化测试
- 🧪 端到端集成测试（可选）

## 🛠️ 常见问题排查

### 问题1: 环境变量未生效

```bash
# 检查环境变量是否正确设置
echo "Backend URL: $TRADINGAGENTS_BACKEND_URL"
echo "Deep Think Model: $TRADINGAGENTS_DEEP_THINK_LLM"

# 如果没有输出，请确保：
source .env  # 或者重启终端
```

### 问题2: 模块导入失败

```bash
# 确保在正确的虚拟环境中
conda activate tradingagents

# 检查是否在项目根目录
pwd
ls -la | grep tradingagents

# 重新安装依赖
pip install -r requirements.txt
```

### 问题3: LLM API连接失败

```bash
# 手动测试API连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "$TRADINGAGENTS_BACKEND_URL/models"

# 检查模型是否存在
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "$TRADINGAGENTS_BACKEND_URL/models" | grep "deepseek-r1"
```

### 问题4: 权限或路径问题

```bash
# 确保脚本有执行权限
chmod +x quick_test.py
chmod +x test_system.py

# 使用Python直接运行
python quick_test.py
python test_system.py
```

## 📊 测试结果解读

### ✅ PASS (通过)
- 绿色显示，表示该项测试完全正常
- 系统该部分功能可以正常使用

### ⚠️ WARNING (警告)  
- 黄色显示，表示该项有潜在问题但不影响基本功能
- 通常是可选配置未设置（如FinnHub API Key）

### ❌ FAIL (失败)
- 红色显示，表示该项测试失败
- 需要修复该问题才能正常使用系统

## 🎯 成功标准

**系统可以正常工作的条件**：
1. ✅ 所有必需的环境变量已设置
2. ✅ 核心模块可以正常导入
3. ✅ LLM API连接正常
4. ✅ TradingAgents可以成功初始化
5. ✅ 至少一个数据源（如Yahoo Finance）可用

**可选但推荐的条件**：
- ✅ FinnHub API配置（提供更丰富的数据）
- ✅ 完整集成测试通过

## 🚦 下一步行动

### 如果快速测试通过：
```bash
# 尝试CLI模式
python -m cli.main

# 或者使用Python API
python main.py
```

### 如果测试失败：
1. 仔细查看错误信息
2. 根据上面的故障排查指南修复问题
3. 重新运行测试
4. 如果问题持续，可以查看详细的测试报告

## 💡 测试技巧

**快速诊断**：
```bash
# 一行命令快速检查配置
python -c "from tradingagents.default_config import DEFAULT_CONFIG; print('Deep Model:', DEFAULT_CONFIG['deep_think_llm']); print('Quick Model:', DEFAULT_CONFIG['quick_think_llm'])"
```

**环境隔离测试**：
```bash
# 在干净环境中测试
conda create -n test-env python=3.13
conda activate test-env
pip install -r requirements.txt
python quick_test.py
```

现在您可以运行 `python quick_test.py` 来快速验证系统是否配置正确！