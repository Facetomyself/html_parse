"""
元素定位功能

基于HTML简化技术和搜索的元素定位器
"""

from typing import List, Dict, Any, Optional


class ElementLocator:
    """元素定位"""

    def __init__(self):
        # 延迟导入以避免循环依赖
        from tools.html_simplifier import HTMLSimplifier
        from tools.html_content_search import HTMLContentSearch
        from tools.structured_data_store import StructuredDataStore

        self.simplifier = HTMLSimplifier()
        self.searcher = HTMLContentSearch()
        self.data_store = StructuredDataStore()

    def analyze_element_positions(self, html_content: str, target_xpath: str = "") -> Dict[str, Any]:
        """
        分析元素位置关系

        Args:
            html_content: HTML内容
            target_xpath: 目标元素XPath（可选）

        Returns:
            位置分析结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"position_analysis_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 分析元素位置
            position_analysis = self._analyze_positions(search_data, target_xpath)

            return {
                'doc_id': doc_id,
                'position_analysis': position_analysis,
                'simplified_html': search_data.get('simplified_html', ''),
                'stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"位置分析错误: {str(e)}"}

    def find_elements_by_xpath(self, html_content: str, xpath: str) -> Dict[str, Any]:
        """
        根据XPath查找元素

        Args:
            html_content: HTML内容
            xpath: XPath表达式

        Returns:
            查找结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 使用搜索器查找匹配的元素
            search_results = self.searcher.search_by_selector(xpath, 'xpath')

            return {
                'found_elements': search_results,
                'xpath': xpath,
                'total_found': len(search_results)
            }

        except Exception as e:
            return {'error': f"XPath查找错误: {str(e)}"}

    def find_elements_by_css(self, html_content: str, css_selector: str) -> Dict[str, Any]:
        """
        根据CSS选择器查找元素

        Args:
            html_content: HTML内容
            css_selector: CSS选择器

        Returns:
            查找结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 使用搜索器查找匹配的元素
            search_results = self.searcher.search_by_selector(css_selector, 'css')

            return {
                'found_elements': search_results,
                'css_selector': css_selector,
                'total_found': len(search_results)
            }

        except Exception as e:
            return {'error': f"CSS选择器查找错误: {str(e)}"}

    def _analyze_positions(self, search_data: Dict[str, Any], target_xpath: str = "") -> Dict[str, Any]:
        """
        分析元素位置关系

        Args:
            search_data: 搜索数据
            target_xpath: 目标XPath

        Returns:
            位置分析结果
        """
        search_index = search_data.get('search_index', {})

        # 分析层级结构
        hierarchy_analysis = self._analyze_hierarchy(search_index)

        # 分析相似元素
        similar_analysis = {}
        if target_xpath:
            similar_elements = self._find_similar_elements(search_index, target_xpath)
            similar_analysis = {
                'target_xpath': target_xpath,
                'similar_elements': similar_elements,
                'total_similar': len(similar_elements)
            }

        # 分析元素分布
        distribution_analysis = self._analyze_distribution(search_index)

        return {
            'hierarchy_analysis': hierarchy_analysis,
            'similar_analysis': similar_analysis,
            'distribution_analysis': distribution_analysis
        }

    def _analyze_hierarchy(self, search_index: Dict[str, Any]) -> Dict[str, Any]:
        """分析元素层级结构"""
        depth_distribution = {}
        tag_hierarchy = {}

        for element_id, element_data in search_index.items():
            depth = element_data.get('depth', 0)
            tag = element_data.get('tag', '')
            path = element_data.get('path', '')

            # 统计深度分布
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

            # 统计标签层级
            if tag not in tag_hierarchy:
                tag_hierarchy[tag] = []
            tag_hierarchy[tag].append({
                'element_id': element_id,
                'depth': depth,
                'path': path
            })

        return {
            'depth_distribution': depth_distribution,
            'tag_hierarchy': tag_hierarchy,
            'max_depth': max(depth_distribution.keys()) if depth_distribution else 0,
            'total_elements': len(search_index)
        }

    def _find_similar_elements(self, search_index: Dict[str, Any], target_xpath: str) -> List[Dict[str, Any]]:
        """查找相似元素"""
        similar_elements = []
        target_tag = target_xpath.split('/')[-1] if target_xpath else ''

        for element_id, element_data in search_index.items():
            tag = element_data.get('tag', '')

            # 查找相同标签的元素
            if tag == target_tag:
                similar_elements.append({
                    'element_id': element_id,
                    'tag': tag,
                    'path': element_data.get('path', ''),
                    'attributes': element_data.get('attributes', {}),
                    'depth': element_data.get('depth', 0)
                })

        return similar_elements[:10]  # 限制数量

    def _analyze_distribution(self, search_index: Dict[str, Any]) -> Dict[str, Any]:
        """分析元素分布"""
        tag_counts = {}
        attribute_counts = {}

        for element_id, element_data in search_index.items():
            tag = element_data.get('tag', '')
            attributes = element_data.get('attributes', {})

            # 统计标签分布
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # 统计属性分布
            for attr_name in attributes.keys():
                attribute_counts[attr_name] = attribute_counts.get(attr_name, 0) + 1

        return {
            'tag_distribution': tag_counts,
            'attribute_distribution': attribute_counts,
            'most_common_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_common_attributes': sorted(attribute_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
