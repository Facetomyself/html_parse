# HTML Analysis Agent 使用示例

这个目录包含了HTML Analysis Agent的各种使用示例，展示如何使用重构后的功能。

## 📁 文件说明

### 主要示例文件

- **`basic_usage.py`** - 基础使用示例
  - 演示如何使用Agent的所有主要功能
  - 使用真实HTML文件进行测试
  - 展示HTML简化、搜索、容器分析等功能

- **`advanced_search_demo.py`** - 高级搜索演示
  - 专门展示搜索和查找功能
  - 多文件批量处理示例
  - 详细的功能对比

### 测试数据文件

- **`13_detail.html`** - 白沙香烟产品详情页面
  - 完整的电商产品页面HTML
  - 包含产品信息、价格、评论等数据
  - 用于测试数据提取功能

- **`95_detail.html`** - 娇子香烟产品详情页面
  - 另一个产品的完整页面
  - 不同的页面结构和内容布局

- **`4761_detail.html`** - 万宝路香烟产品详情页面
  - 第三个测试HTML文件
  - 用于测试系统的通用性

## 🚀 快速开始

### 1. 运行基础示例

```bash
# 确保在项目根目录
cd /path/to/html_analysis_agent

# 运行基础使用示例
python examples/basic_usage.py
```

### 2. 运行高级搜索演示

```bash
python examples/advanced_search_demo.py
```

## 📊 示例功能展示

### HTML简化
```python
from html_analysis_agent import HTMLAnalysisAgent

agent = HTMLAnalysisAgent()
result = agent.analyze_html_with_simplification(html_content)

print(f"简化统计: {result['simplification_stats']}")
print(f"简化后HTML: {result['simplified_html'][:500]}")
```

### 智能搜索
```python
# 关键词搜索
search_result = agent.search_html_content(html_content, ['价格', '品牌', '评分'])

# XPath查找
xpath_result = agent.find_elements_by_xpath(html_content, "//div[@class='price']")

# CSS选择器查找
css_result = agent.find_elements_by_css(html_content, ".product-info")
```

### 数据容器分析
```python
container_result = agent.analyze_data_containers(html_content)
print(f"发现容器类型: {list(container_result['containers'].keys())}")
```

## 🎯 测试数据说明

### 13_detail.html (白沙香烟)
- **页面类型**: 产品详情页
- **主要内容**:
  - 产品基本信息（品牌、类型、焦油含量等）
  - 价格信息
  - 用户评分和评论
  - 产品图片
  - 购买相关按钮

- **适用测试**:
  - 产品信息提取
  - 价格数据抓取
  - 用户评论分析
  - 按钮元素定位

### 95_detail.html (娇子香烟)
- **页面类型**: 产品详情页
- **主要内容**:
  - 产品规格信息
  - 价格和促销信息
  - 用户评价数据
  - 产品描述和图片

- **适用测试**:
  - 不同页面结构的兼容性
  - 多种数据类型的提取
  - 动态内容处理

### 4761_detail.html (未知产品)
- **页面类型**: 产品详情页
- **主要内容**:
  - 未知产品类型的完整页面
  - 用于测试系统的通用性

- **适用测试**:
  - 系统鲁棒性测试
  - 未知内容的处理能力

## 🔧 自定义测试

### 添加新的HTML测试文件

1. 将HTML文件放入 `examples/` 目录
2. 在示例代码中添加新的文件路径：

```python
html_files = {
    '新产品': 'new_product.html',
    '测试页面': 'test_page.html'
}
```

### 修改搜索关键词

```python
# 根据你的HTML内容修改关键词
search_keywords = ['你的关键词', '相关内容', '目标数据']
```

### 自定义XPath和CSS选择器

```python
# 根据页面结构调整选择器
xpath_patterns = [
    "//div[@class='你的元素类名']",
    "//span[contains(text(), '目标文本')]"
]

css_patterns = [
    ".你的类名",
    "#你的ID",
    "div[属性='值']"
]
```

## 📈 性能测试

### 简化效果测试

```bash
# 运行简化功能演示
python examples/basic_usage.py
# 查看输出中的"简化统计"和"压缩比例"
```

### 搜索性能测试

```bash
# 运行搜索功能演示
python examples/advanced_search_demo.py
# 观察搜索速度和准确性
```

## 🐛 故障排除

### 常见问题

1. **文件不存在错误**
   - 确保HTML文件在正确的路径
   - 检查文件名是否正确

2. **编码错误**
   - 确保HTML文件使用UTF-8编码
   - 检查文件是否有特殊字符

3. **导入错误**
   - 确保已安装所有依赖包
   - 检查Python路径设置

### 调试技巧

1. **查看简化结果**
   ```python
   simplified = agent.analyze_html_with_simplification(html_content)
   print("简化统计:", simplified['simplification_stats'])
   ```

2. **检查搜索结果**
   ```python
   search = agent.search_html_content(html_content, ['关键词'])
   print("搜索结果数量:", len(search['search_results']))
   ```

3. **验证选择器**
   ```python
   xpath_result = agent.find_elements_by_xpath(html_content, "//div")
   print("找到元素:", xpath_result['total_found'])
   ```

## 🤝 贡献

欢迎提交新的示例文件和改进建议！

1. 添加新的HTML测试文件
2. 创建针对特定功能的示例
3. 改进现有示例的注释和文档

## 📞 联系

如有问题或建议，请联系开发团队。
