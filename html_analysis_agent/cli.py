#!/usr/bin/env python3
"""
HTML Analysis Agent 命令行工具

提供命令行接口来使用HTML分析功能
"""

import argparse
import sys
import os
from .agent import HTMLAnalysisAgent
from .utils import Utils


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='HTML Analysis Agent - 专业的HTML解析和分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m html_analysis_agent.cli input.html
  python -m html_analysis_agent.cli input.html --output results.txt
  python -m html_analysis_agent.cli input.html --analysis data_containers
        """
    )

    parser.add_argument(
        'input_file',
        help='输入的HTML文件路径'
    )

    parser.add_argument(
        '--output', '-o',
        help='输出文件路径',
        default=None
    )

    parser.add_argument(
        '--analysis', '-a',
        choices=['basic', 'data_containers', 'element_positions', 'all'],
        default='all',
        help='分析类型 (basic: 基础解析, data_containers: 数据容器分析, element_positions: 元素位置分析, all: 全部分析)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'html'],
        default='text',
        help='输出格式'
    )

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在", file=sys.stderr)
        sys.exit(1)

    # 加载HTML内容
    try:
        html_content = Utils.load_html_file(args.input_file)
        print(f"成功加载HTML文件: {args.input_file} ({len(html_content):,} 字符)")
    except Exception as e:
        print(f"错误: 无法加载HTML文件 - {e}", file=sys.stderr)
        sys.exit(1)

    # 验证HTML内容
    if not Utils.validate_html_content(html_content):
        print("警告: HTML内容可能无效", file=sys.stderr)

    # 初始化Agent
    try:
        agent = HTMLAnalysisAgent()
        print("HTML Analysis Agent 初始化成功")
    except Exception as e:
        print(f"错误: Agent初始化失败 - {e}", file=sys.stderr)
        sys.exit(1)

    # 执行分析
    results = []

    try:
        if args.analysis in ['basic', 'all']:
            print("\n=== 基础解析 ===")
            basic_result = agent.parse_html(html_content)
            print(basic_result)
            results.append(("基础解析", basic_result))

        if args.analysis in ['data_containers', 'all']:
            print("\n=== 数据容器分析 ===")
            data_result = agent.analyze_data_containers(html_content)
            print(f"文档ID: {data_result.get('doc_id', 'N/A')}")

            containers = data_result.get('containers', {})

            # 显示统计信息
            print("\n发现数据容器类型:")
            for container_type, items in containers.items():
                print(f"  {container_type}: {len(items)} 个")

            # 显示详细示例
            print("\n数据容器详情:")
            for container_type, items in containers.items():
                if items and len(items) > 0:
                    # 更友好的显示名称
                    display_names = {
                        'content_containers': '主要内容容器',
                        'navigation_menus': '导航菜单',
                        'data_tables': '数据表格',
                        'form_elements': '表单元素',
                        'media_containers': '媒体容器',
                        'interactive_elements': '交互元素',
                        'metadata_containers': '元数据容器',
                        'list_structures': '列表结构',
                        'decorative_elements': '装饰元素',
                        'other': '其他元素'
                    }
                    friendly_name = display_names.get(container_type, container_type.upper())

                    print(f"\n{friendly_name} ({len(items)} 个):")
                    for i, item in enumerate(items[:3]):  # 每个类型最多显示3个
                        print(f"  {i+1}. {item.get('description', '未描述')}")
                        print(f"     标签: {item.get('tag', 'unknown')}")
                        print(f"     重要性: {item.get('importance', 'unknown')}")
                        content_type = item.get('content_type', '')
                        if content_type:
                            print(f"     内容类型: {content_type}")
                        content_preview = item.get('content_preview', '')
                        if content_preview:
                            print(f"     内容预览: {content_preview[:80]}...")
                        attributes = item.get('attributes', {})
                        if attributes:
                            attr_preview = ', '.join([f'{k}="{v}"' for k, v in list(attributes.items())[:2]])
                            print(f"     属性: {attr_preview}")
                        print()

            results.append(("数据容器分析", data_result))

        if args.analysis in ['element_positions', 'all']:
            print("\n=== 元素位置分析 ===")
            position_result = agent.analyze_element_positions(html_content)
            print(position_result)
            results.append(("元素位置分析", position_result))

    except Exception as e:
        print(f"错误: 分析过程失败 - {e}", file=sys.stderr)
        sys.exit(1)

    # 保存结果
    if args.output:
        try:
            # 合并所有结果
            combined_result = "\n\n".join([f"=== {title} ===\n{content}" for title, content in results])

            # 格式化输出
            formatted_result = Utils.format_output(combined_result, args.format)

            # 保存到文件
            if Utils.save_results_to_file(formatted_result, args.output):
                print(f"\n结果已保存到: {args.output}")
            else:
                print(f"\n错误: 无法保存结果到 {args.output}", file=sys.stderr)
                sys.exit(1)

        except Exception as e:
            print(f"错误: 保存结果失败 - {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\n分析完成! 共执行 {len(results)} 项分析。")


if __name__ == '__main__':
    main()
