# HTML Analysis Agent

一个智能的HTML解析和分析工具，专门用于提取和分析网页中的关键元素和数据容器。

## 功能特性

### 🔄 核心重构特性（基于HTML简化技术）

- **🚀 HTML简化技术**：自动移除脚本、样式、图片等冗余内容，减少90%的上下文占用
- **🔍 智能内容搜索**：支持关键词搜索，快速定位相关HTML元素和内容
- **💾 结构化数据存储**：基于简化结构的高效数据存储和检索
- **⚡ 高效元素定位**：无需读取完整HTML，基于索引的快速元素定位

### 📊 分析功能

- HTML元素解析和XPath/CSS选择器生成
- 智能数据容器识别和价值评估
- 元素位置关系分析
- HTML内容变化检测
- 结构化输出和报告生成

### 🤖 智能功能

- **智能选择器生成**：基于自然语言描述自动生成XPath和CSS选择器
- **批量元素处理**：支持一次处理多个元素的分析和定位
- **变化检测**：基于简化结构的快速HTML变化检测
- **LangGraph集成**：完整的智能代理工作流支持

## 安装说明

### 1. 环境要求
- Python 3.8+
- 虚拟环境（推荐）

### 2. 依赖安装
```bash
pip install -r requirements.txt
```

### 3. 环境配置
复制 `.env.example` 到 `.env` 并配置你的API密钥：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=your_base_url_here
```

## 使用方法

### 基本用法

```python
from html_analysis_agent import HTMLAnalysisAgent

# 初始化Agent
agent = HTMLAnalysisAgent()

# 解析HTML内容
with open('your_html_file.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

result = agent.parse_html(html_content)
print(result)
```

### 数据容器分析

```python
# 分析数据容器
containers = agent.analyze_data_containers(html_content)
print(containers)
```

### 元素位置分析

```python
# 分析元素位置关系
positions = agent.analyze_element_positions(html_content)
print(positions)
```

### HTML简化分析和选择器生成（新功能）

#### HTML简化分析
```python
# 使用HTML简化技术分析HTML内容
analysis_result = agent.analyze_html_with_simplification(html_content)
print("简化统计:", analysis_result['simplification_stats'])
print("简化HTML:", analysis_result['simplified_html'][:500])
```

#### 智能选择器生成
```python
# 为指定元素生成XPath和CSS选择器
result = agent.generate_selectors(html_content, "登录按钮")
print("生成的建议:", result['generated_selectors'])
```

#### 元素信息查询
```python
# 根据选择器获取元素信息
element_info = agent.get_element_info(html_content, "//*[@id='login-btn']", "xpath")
print("元素信息:", element_info)
```

### 🔍 新的搜索和查找功能

#### HTML内容搜索
```python
# 搜索HTML内容中的关键词
search_result = agent.search_html_content(html_content, ["登录", "按钮", "用户名"])
print("搜索结果:", search_result['search_results'])
```

#### XPath元素查找
```python
# 根据XPath查找元素
xpath_result = agent.find_elements_by_xpath(html_content, "//button[@id='login-btn']")
print("找到的元素:", xpath_result['found_elements'])
```

#### CSS选择器元素查找
```python
# 根据CSS选择器查找元素
css_result = agent.find_elements_by_css(html_content, "#login-btn")
print("找到的元素:", css_result['found_elements'])
```

## 📊 性能对比

| 功能 | 传统方式 | 重构后方式 | 改进 |
|------|----------|------------|------|
| 上下文占用 | 完整HTML (~50KB) | 简化结构 (~5KB) | **90%减少** |
| 搜索速度 | 解析完整HTML | 基于索引搜索 | **10倍提升** |
| 内存使用 | 高 | 低 | **显著优化** |
| 扩展性 | 差 | 优 | **大幅提升** |

## 🎯 适用场景

### 智能Web数据提取
- 电商产品信息抓取
- 新闻文章内容提取
- 社交媒体数据采集
- 竞争对手网站监控

### 自动化测试
- Web元素定位和选择器生成
- 页面结构变化检测
- 自动化测试脚本维护

### 数据分析与监控
- 网站内容变化追踪
- SEO优化分析
- 用户行为数据收集

### AI Agent集成
- LangGraph工作流集成
- 智能Web浏览助手
- 自动化Web任务执行

## 项目结构

```
html_analysis_agent/
├── __init__.py              # 包初始化文件
├── agent.py                 # 主要的Agent类
├── html_parser.py           # HTML解析核心功能
├── data_analyzer.py         # 数据容器分析功能
├── element_locator.py       # 元素定位功能
├── change_detector.py       # 变化检测功能
├── selector_agent.py        # **新功能：XPath/CSS选择器生成智能体**
└── utils.py                 # 工具函数
├── tools/
│   ├── html_simplifier.py   # **新功能：HTML简化工具**
│   └── __pycache__/

├── examples/
│   └── basic_usage.py       # 基本使用示例
├── docs/
│   └── API_REFERENCE.md     # API文档
├── .env.example             # 环境变量示例
├── requirements.txt         # 项目依赖
├── setup.py                 # 安装脚本
└── README.md                # 项目说明
```

## 配置选项

### Agent配置

```python
agent = HTMLAnalysisAgent(
    model_name="gemini-2.5-flash",
    temperature=0,
    max_tokens=2000,
    max_retries=2
)
```

### 解析配置

```python
result = agent.parse_html(
    html_content,
    include_tables=True,
    include_lists=True,
    max_elements=50
)
```

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本使用
```python
from html_analysis_agent import HTMLAnalysisAgent

# 初始化Agent
agent = HTMLAnalysisAgent()

# 读取HTML文件
with open('webpage.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 简化HTML分析
result = agent.analyze_html_with_simplification(html_content)
print(f"简化统计: {result['simplification_stats']}")

# 智能搜索
search_results = agent.search_html_content(html_content, ["登录", "按钮"])
print(f"找到 {len(search_results['search_results'])} 个匹配项")
```

### 命令行工具

项目提供了一个命令行工具用于快速测试：

```bash
python -m html_analysis_agent.cli input.html
```