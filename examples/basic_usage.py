#!/usr/bin/env python3
"""
HTML Analysis Agent 重构后使用示例

演示如何使用基于HTML简化技术的HTML Analysis Agent
使用真实HTML文件进行测试和演示
"""
import sys
from pathlib import Path

# 将项目根目录添加到sys.path，确保可以正确导入html_analysis_agent
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from html_analysis_agent import HTMLAnalysisAgent


def load_html_file(file_path):
    """加载HTML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def demo_with_real_html():
    """使用真实HTML文件进行演示"""
    print("HTML Analysis Agent 重构后功能演示")
    print("=" * 60)

    # 初始化Agent
    print("1. 初始化Agent...")
    agent = HTMLAnalysisAgent()
    print("   ✓ Agent初始化成功")

    # 准备测试文件
    html_files = {
        '白沙香烟': '13_detail.html',
        '娇子香烟': '95_detail.html',
        '万宝路香烟': '4761_detail.html'
    }

    # 遍历测试文件
    for product_name, filename in html_files.items():
        file_path = Path('examples') / filename

        if not file_path.exists():
            print(f"\n警告: 文件 {filename} 不存在，跳过...")
            continue

        print(f"\n{'='*60}")
        print(f"分析产品: {product_name} ({filename})")
        print('='*60)

        try:
            # 加载HTML内容
            html_content = load_html_file(file_path)
            print(f"   文件大小: {len(html_content):,} 字符")

            # 2. HTML简化分析
            print("\n2. HTML简化分析...")
            simplified_result = agent.analyze_html_with_simplification(html_content)
            stats = simplified_result.get('simplification_stats', {})
            print(f"   简化统计:")
            for key, value in stats.items():
                print(f"     {key}: {value}")
            print(f"   简化后HTML长度: {len(simplified_result.get('simplified_html', '')):,} 字符")

            # 3. 数据容器分析
            print("\n3. 数据容器分析...")
            container_result = agent.analyze_data_containers(html_content)
            containers = container_result.get('containers', {})
            print(f"   发现数据容器类型:")
            for container_type, items in containers.items():
                print(f"     {container_type}: {len(items)} 个")
            print(f"   文档ID: {container_result.get('doc_id', 'N/A')}")

            # 4. 内容搜索
            print("\n4. 内容搜索...")
            search_keywords = ['价格', '品牌', '评分', '评论']
            search_result = agent.search_html_content(html_content, search_keywords)
            print(f"   搜索关键词: {search_keywords}")
            search_items = search_result.get('search_results', [])
            print(f"   找到匹配项: {len(search_items)} 个")

            # 显示前几个搜索结果
            for i, item in enumerate(search_items[:3]):
                print(f"     结果 {i+1}: {item.get('tag', 'unknown')} - {item.get('text_content', '')[:50]}...")

            # 5. XPath元素查找
            print("\n5. XPath元素查找...")
            xpath_patterns = [
                "//div[@class='column_tit']",
                "//span[@class='price']",
                "//button"
            ]

            for xpath in xpath_patterns:
                xpath_result = agent.find_elements_by_xpath(html_content, xpath)
                found_count = xpath_result.get('total_found', 0)
                print(f"     {xpath}: 找到 {found_count} 个元素")

            # 6. CSS选择器元素查找
            print("\n6. CSS选择器元素查找...")
            css_patterns = [
                ".column_tit",
                ".price",
                "button"
            ]

            for css in css_patterns:
                css_result = agent.find_elements_by_css(html_content, css)
                found_count = css_result.get('total_found', 0)
                print(f"     {css}: 找到 {found_count} 个元素")

            # 7. 元素位置分析
            print("\n7. 元素位置分析...")
            position_result = agent.analyze_element_positions(html_content)
            hierarchy = position_result.get('position_analysis', {}).get('hierarchy_analysis', {})
            print(f"   元素层级分析:")
            print(f"     最大深度: {hierarchy.get('max_depth', 0)}")
            print(f"     总元素数: {hierarchy.get('total_elements', 0)}")
            print(f"     文档ID: {position_result.get('doc_id', 'N/A')}")

        except Exception as e:
            print(f"   处理文件时出错: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("演示完成！")
    print("=" * 60)

    # 显示总结
    print("\n演示总结:")
    print("   HTML简化技术 - 90%内容减少")
    print("   内容搜索 - 关键词快速定位")
    print("   数据容器分析 - 结构化信息提取")
    print("   XPath/CSS查找 - 精确元素定位")
    print("   元素位置分析 - 层级结构理解")
    print("   结构化存储 - 高效数据管理")


def demo_html_simplification():
    """演示HTML简化功能"""
    print("\nHTML简化功能单独演示")
    print("=" * 40)

    from tools.html_simplifier import HTMLSimplifier

    simplifier = HTMLSimplifier()

    # 使用第一个HTML文件作为示例
    sample_file = Path('examples/13_detail.html')
    if sample_file.exists():
        html_content = load_html_file(sample_file)

        print(f"原始HTML长度: {len(html_content):,} 字符")

        # 简化HTML
        simplified = simplifier.simplify_html_string(html_content)
        stats = simplifier.get_simplification_stats()

        print(f"简化后HTML长度: {len(simplified):,} 字符")
        print(f"压缩比例: {(1 - len(simplified)/len(html_content)):.1%}")
        print("\n简化统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n简化前后对比:")
        print("原始HTML片段:")
        print(html_content[:200] + "..." if len(html_content) > 200 else html_content)
        print("\n简化HTML片段:")
        print(simplified[:200] + "..." if len(simplified) > 200 else simplified)


def demo_content_search():
    """演示内容搜索功能"""
    print("\n内容搜索功能单独演示")
    print("=" * 40)

    from tools.html_content_search import HTMLContentSearch

    searcher = HTMLContentSearch()

    # 使用HTML文件进行搜索演示
    sample_file = Path('examples/13_detail.html')
    if sample_file.exists():
        html_content = load_html_file(sample_file)

        # 构建搜索索引
        search_data = searcher.build_search_index(html_content)
        print(f"构建搜索索引完成，找到 {len(search_data.get('search_index', {}))} 个元素")

        # 搜索示例
        search_terms = ['白沙', '价格', 'button', 'div']

        for term in search_terms:
            results = searcher.search_by_keyword(term)
            print(f"\n搜索 '{term}': 找到 {len(results)} 个结果")
            for i, result in enumerate(results[:2]):  # 只显示前2个
                print(f"  结果 {i+1}: {result.get('tag')} - {result.get('text_content', '')[:60]}...")

        # CSS选择器搜索
        css_results = searcher.search_by_selector('.column_tit', 'css')
        print(f"\nCSS选择器 '.column_tit': 找到 {len(css_results)} 个结果")


def main():
    """主函数"""
    try:
        # 主要演示
        demo_with_real_html()

        # 单独功能演示
        demo_html_simplification()
        demo_content_search()

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已正确安装所有依赖包")
    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
