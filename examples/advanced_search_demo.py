#!/usr/bin/env python3
"""
高级搜索功能演示

展示如何使用重构后的搜索和查找功能
"""
import sys
from pathlib import Path

# 将项目根目录添加到sys.path，确保可以正确导入html_analysis_agent
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from html_analysis_agent import HTMLAnalysisAgent
from pathlib import Path


def load_html_file(file_path):
    """加载HTML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def demo_advanced_search():
    """高级搜索功能演示"""
    print("HTML Analysis Agent 高级搜索功能演示")
    print("=" * 60)

    # 初始化Agent
    agent = HTMLAnalysisAgent()

    # 测试文件
    test_file = Path('examples/13_detail.html')
    if not test_file.exists():
        print(f"错误: 测试文件 {test_file} 不存在")
        return

    # 加载HTML内容
    html_content = load_html_file(test_file)
    print(f"加载文件: {test_file.name}")
    print(f"   文件大小: {len(html_content):,} 字符")

    # 1. 关键词搜索
    print("\n1. 关键词搜索")
    print("-" * 30)

    keywords = ['白沙', '价格', '评分', '评论', 'button']
    search_result = agent.search_html_content(html_content, keywords)

    print(f"搜索关键词: {keywords}")
    print(f"找到匹配项: {len(search_result.get('search_results', []))}")

    # 按关键词分组显示结果
    results_by_keyword = {}
    for result in search_result.get('search_results', []):
        keyword = result.get('matched_keyword', 'unknown')
        if keyword not in results_by_keyword:
            results_by_keyword[keyword] = []
        results_by_keyword[keyword].append(result)

    for keyword, results in results_by_keyword.items():
        print(f"\n'{keyword}' 相关结果 ({len(results)} 个):")
        for i, result in enumerate(results[:2]):  # 每个关键词最多显示2个结果
            print(f"  {i+1}. {result.get('tag', 'unknown')} - {result.get('text_content', '')[:60]}...")

    # 2. XPath查找
    print("\n\n2. XPath元素查找")
    print("-" * 30)

    xpath_tests = [
        "//div[@class='column_tit']",
        "//span[contains(@class, 'price')]",
        "//button[@id='login-btn']",
        "//h1",
        "//ul[@class='ul_1']"
    ]

    for xpath in xpath_tests:
        result = agent.find_elements_by_xpath(html_content, xpath)
        found_count = result.get('total_found', 0)
        print(f"XPath: {xpath}")
        print(f"  找到元素: {found_count} 个")

        # 显示找到的元素信息
        found_elements = result.get('found_elements', [])
        for i, element in enumerate(found_elements[:1]):  # 只显示第一个
            print(f"  示例: {element.get('tag')} - {element.get('text_content', '')[:40]}...")
        print()

    # 3. CSS选择器查找
    print("\n3. CSS选择器元素查找")
    print("-" * 30)

    css_tests = [
        ".column_tit",
        ".price",
        "button",
        "h1",
        ".ul_1"
    ]

    for css in css_tests:
        result = agent.find_elements_by_css(html_content, css)
        found_count = result.get('total_found', 0)
        print(f"CSS: {css}")
        print(f"  找到元素: {found_count} 个")

        # 显示找到的元素信息
        found_elements = result.get('found_elements', [])
        for i, element in enumerate(found_elements[:1]):  # 只显示第一个
            print(f"  示例: {element.get('tag')} - {element.get('text_content', '')[:40]}...")
        print()

    # 4. 数据容器分析
    print("\n4. 数据容器分析")
    print("-" * 30)

    container_result = agent.analyze_data_containers(html_content)
    containers = container_result.get('containers', {})

    print("发现的数据容器类型:")
    for container_type, items in containers.items():
        print(f"  {container_type}: {len(items)} 个容器")

    # 显示每个类型的前几个容器
    for container_type, items in containers.items():
        if items:
            print(f"\n{container_type} 容器示例:")
            for i, item in enumerate(items[:2]):  # 每个类型最多显示2个
                print(f"  {i+1}. {item.get('tag', 'unknown')} - {item.get('text_content', '')[:60]}...")

    # 5. 元素位置分析
    print("\n\n5. 元素位置分析")
    print("-" * 30)

    position_result = agent.analyze_element_positions(html_content)
    hierarchy = position_result.get('position_analysis', {}).get('hierarchy_analysis', {})

    print(f"层级分析:")
    print(f"  最大深度: {hierarchy.get('max_depth', 0)}")
    print(f"  总元素数: {hierarchy.get('total_elements', 0)}")

    depth_dist = hierarchy.get('depth_distribution', {})
    print(f"  深度分布:")
    for depth, count in sorted(depth_dist.items())[:5]:
        print(f"    深度 {depth}: {count} 个元素")

    # 6. HTML简化分析
    print("\n\n6. HTML简化分析")
    print("-" * 30)

    simplified_result = agent.analyze_html_with_simplification(html_content)
    stats = simplified_result.get('simplification_stats', {})

    print("简化统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    original_size = len(html_content)
    simplified_size = len(simplified_result.get('simplified_html', ''))
    compression_ratio = (1 - simplified_size / original_size) * 100

    print(f"\n压缩效果:")
    print(f"  原始大小: {original_size:,} 字符")
    print(f"  简化后: {simplified_size:,} 字符")
    print(f"  压缩比例: {compression_ratio:.1f}%")

    print(f"\n高级搜索演示完成！")


def demo_multiple_files():
    """演示多文件处理"""
    print("\n多文件批量处理演示")
    print("=" * 40)

    agent = HTMLAnalysisAgent()

    # 测试文件列表
    test_files = [
        ('白沙香烟', 'examples/13_detail.html'),
        ('娇子香烟', 'examples/95_detail.html'),
        ('未知产品', 'examples/4761_detail.html')
    ]

    results = {}

    for product_name, file_path in test_files:
        file_obj = Path(file_path)
        if not file_obj.exists():
            print(f"警告: 跳过 {product_name}: 文件不存在")
            continue

        print(f"\n处理: {product_name}")

        try:
            html_content = load_html_file(file_path)

            # 执行简化分析
            simplified_result = agent.analyze_html_with_simplification(html_content)
            stats = simplified_result.get('simplification_stats', {})

            # 执行搜索
            search_result = agent.search_html_content(html_content, ['价格', '评分'])

            # 存储结果
            results[product_name] = {
                'file_size': len(html_content),
                'simplified_stats': stats,
                'search_count': len(search_result.get('search_results', []))
            }

            print(f"   文件大小: {len(html_content):,} 字符")
            print(f"   移除脚本: {stats.get('script_tags', 0)} 个")
            print(f"   移除样式: {stats.get('style_tags', 0)} 个")
            print(f"   搜索结果: {len(search_result.get('search_results', []))} 个")

        except Exception as e:
            print(f"  处理失败: {e}")

    # 显示对比结果
    if results:
        print(f"\n{'='*40}")
        print("处理结果对比")
        print('='*40)

        for product_name, data in results.items():
            print(f"\n{product_name}:")
            print(f"  文件大小: {data['file_size']:,} 字符")
            print(f"  脚本移除: {data['simplified_stats'].get('script_tags', 0)}")
            print(f"  样式移除: {data['simplified_stats'].get('style_tags', 0)}")
            print(f"  搜索结果: {data['search_count']} 个")


def main():
    """主函数"""
    try:
        # 高级搜索演示
        demo_advanced_search()

        # 多文件处理演示
        demo_multiple_files()

    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
