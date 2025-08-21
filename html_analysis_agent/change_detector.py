"""
变化检测工具

基于HTML简化技术的变化检测器
"""

from typing import List, Dict, Any, Optional
import difflib


class ChangeDetector:
    """变化检测器"""

    def __init__(self):
        # 延迟导入以避免循环依赖
        from tools.html_simplifier import HTMLSimplifier
        from tools.html_content_search import HTMLContentSearch
        from tools.structured_data_store import StructuredDataStore

        self.simplifier = HTMLSimplifier()
        self.searcher = HTMLContentSearch()
        self.data_store = StructuredDataStore()

    def detect_changes(self, html_content: str, previous_html: str = "") -> Dict[str, Any]:
        """
        检测HTML内容变化

        Args:
            html_content: 当前HTML内容
            previous_html: 之前的HTML内容（可选）

        Returns:
            变化检测结果字典
        """
        try:
            if not previous_html:
                return {'error': '没有可比较的HTML内容，请先解析一个HTML文档'}

            # 简化当前HTML
            current_simplified = self.simplifier.simplify_html_string(html_content)
            current_stats = self.simplifier.get_simplification_stats()

            # 简化之前的HTML
            previous_simplified = self.simplifier.simplify_html_string(previous_html)
            previous_stats = self.simplifier.get_simplification_stats()

            # 构建搜索索引
            current_search_data = self.searcher.build_search_index(html_content)
            previous_search_data = self.searcher.build_search_index(previous_html)

            # 存储数据
            current_doc_id = self.data_store.store_html_data(f"current_{hash(html_content) % 10000}", current_search_data)
            previous_doc_id = self.data_store.store_html_data(f"previous_{hash(previous_html) % 10000}", previous_search_data)

            # 分析变化
            changes = self._analyze_changes(
                current_search_data, previous_search_data,
                current_stats, previous_stats
            )

            return {
                'current_doc_id': current_doc_id,
                'previous_doc_id': previous_doc_id,
                'changes': changes,
                'current_simplified': current_simplified,
                'previous_simplified': previous_simplified,
                'current_stats': current_stats,
                'previous_stats': previous_stats
            }

        except Exception as e:
            return {'error': f"变化检测错误: {str(e)}"}

    def _analyze_changes(self, current_data: Dict[str, Any], previous_data: Dict[str, Any],
                        current_stats: Dict[str, Any], previous_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析HTML变化

        Args:
            current_data: 当前数据
            previous_data: 之前数据
            current_stats: 当前统计
            previous_stats: 之前统计

        Returns:
            变化分析结果
        """
        current_index = current_data.get('search_index', {})
        previous_index = previous_data.get('search_index', {})

        # 比较简化统计
        simplification_changes = self._compare_simplification_stats(current_stats, previous_stats)

        # 比较搜索索引
        index_changes = self._compare_search_indexes(current_index, previous_index)

        # 文本差异分析
        text_differences = self._analyze_text_differences(
            current_data.get('simplified_html', ''),
            previous_data.get('simplified_html', '')
        )

        return {
            'simplification_changes': simplification_changes,
            'index_changes': index_changes,
            'text_differences': text_differences,
            'summary': {
                'total_current_elements': len(current_index),
                'total_previous_elements': len(previous_index),
                'elements_difference': len(current_index) - len(previous_index)
            }
        }

    def _compare_simplification_stats(self, current_stats: Dict[str, Any], previous_stats: Dict[str, Any]) -> Dict[str, Any]:
        """比较简化统计"""
        changes = {}

        for key in current_stats.keys():
            current_value = current_stats.get(key, 0)
            previous_value = previous_stats.get(key, 0)
            difference = current_value - previous_value

            if difference != 0:
                changes[key] = {
                    'current': current_value,
                    'previous': previous_value,
                    'difference': difference
                }

        return changes

    def _compare_search_indexes(self, current_index: Dict[str, Any], previous_index: Dict[str, Any]) -> Dict[str, Any]:
        """比较搜索索引"""
        current_paths = {data.get('path', '') for data in current_index.values()}
        previous_paths = {data.get('path', '') for data in previous_index.values()}

        added_paths = current_paths - previous_paths
        removed_paths = previous_paths - current_paths

        return {
            'added_elements': len(added_paths),
            'removed_elements': len(removed_paths),
            'added_paths': list(added_paths)[:10],  # 限制数量
            'removed_paths': list(removed_paths)[:10]  # 限制数量
        }

    def _analyze_text_differences(self, current_html: str, previous_html: str) -> Dict[str, Any]:
        """分析文本差异"""
        # 计算文本差异
        differ = difflib.Differ()
        diff = list(differ.compare(previous_html.splitlines(), current_html.splitlines()))

        # 统计差异
        additions = len([line for line in diff if line.startswith('+')])
        deletions = len([line for line in diff if line.startswith('-')])
        changes = len([line for line in diff if line.startswith('?')])

        # 生成差异摘要
        diff_summary = []
        for i, line in enumerate(diff):
            if line.startswith(('+', '-', '?')):
                diff_summary.append(line)
                if len(diff_summary) >= 20:  # 限制摘要长度
                    break

        return {
            'additions': additions,
            'deletions': deletions,
            'changes': changes,
            'diff_summary': diff_summary
        }
