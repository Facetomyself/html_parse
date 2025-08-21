"""
HTML内容搜索工具

基于HTML简化结构进行高效的内容搜索和标签定位
"""

from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import re
from pathlib import Path


class HTMLContentSearch:
    """HTML内容搜索器"""

    def __init__(self):
        """初始化搜索器"""
        self.search_results = []
        self.content_index = {}

    def build_search_index(self, html_content: str) -> Dict[str, Any]:
        """
        构建搜索索引

        Args:
            html_content: 原始HTML内容

        Returns:
            搜索索引和简化结构
        """
        # 解析HTML
        soup = BeautifulSoup(html_content, 'lxml')

        # 构建索引
        self.content_index = {}
        self._traverse_and_index(soup)

        # 简化HTML结构
        from .html_simplifier import HTMLSimplifier
        simplifier = HTMLSimplifier()
        simplified_html = simplifier.simplify_html_string(html_content)
        stats = simplifier.get_simplification_stats()

        return {
            'search_index': self.content_index,
            'simplified_html': simplified_html,
            'simplification_stats': stats
        }

    def _traverse_and_index(self, element, depth: int = 0, parent_path: str = ""):
        """递归遍历并建立索引"""
        if hasattr(element, 'name') and element.name:
            # 生成元素路径
            element_id = f"element_{len(self.content_index)}"
            current_path = f"{parent_path}/{element.name}" if parent_path else element.name

            # 提取元素信息
            text_content = element.get_text(strip=True)
            attributes = dict(element.attrs)

            # 建立索引项
            index_item = {
                'element_id': element_id,
                'tag': element.name,
                'path': current_path,
                'depth': depth,
                'text_content': text_content,
                'attributes': attributes,
                'full_text': element.get_text(),
                'parent_path': parent_path
            }

            # 添加到索引
            self.content_index[element_id] = index_item

            # 递归处理子元素
            if hasattr(element, 'children'):
                for child in element.children:
                    if hasattr(child, 'name') and child.name:
                        self._traverse_and_index(child, depth + 1, current_path)

    def search_by_keyword(self, keyword: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        根据关键字搜索

        Args:
            keyword: 搜索关键字
            search_type: 搜索类型 ('all', 'tag', 'text', 'attribute')

        Returns:
            搜索结果列表
        """
        results = []
        keyword_lower = keyword.lower()

        for element_id, item in self.content_index.items():
            match_score = 0
            match_reasons = []

            # 搜索标签名
            if search_type in ['all', 'tag']:
                if keyword_lower in item['tag'].lower():
                    match_score += 10
                    match_reasons.append('tag_match')

            # 搜索文本内容
            if search_type in ['all', 'text']:
                if item['text_content'] and keyword_lower in item['text_content'].lower():
                    match_score += 5
                    match_reasons.append('text_match')

            # 搜索属性值
            if search_type in ['all', 'attribute']:
                for attr_name, attr_value in item['attributes'].items():
                    if isinstance(attr_value, list):
                        attr_value = ' '.join(attr_value)
                    if keyword_lower in str(attr_value).lower():
                        match_score += 3
                        match_reasons.append(f'attr_match_{attr_name}')

            # 如果有匹配，添加到结果
            if match_score > 0:
                result_item = item.copy()
                result_item['match_score'] = match_score
                result_item['match_reasons'] = match_reasons
                results.append(result_item)

        # 按匹配分数排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

    def search_by_selector(self, selector: str, selector_type: str = 'css') -> List[Dict[str, Any]]:
        """
        根据选择器搜索元素

        Args:
            selector: CSS选择器或XPath表达式
            selector_type: 选择器类型 ('css' 或 'xpath')

        Returns:
            匹配的元素列表
        """
        results = []

        for element_id, item in self.content_index.items():
            if self._matches_selector(item, selector, selector_type):
                results.append(item)

        return results

    def _matches_selector(self, item: Dict[str, Any], selector: str, selector_type: str) -> bool:
        """检查元素是否匹配选择器"""
        if selector_type == 'css':
            return self._matches_css_selector(item, selector)
        elif selector_type == 'xpath':
            return self._matches_xpath_selector(item, selector)
        return False

    def _matches_css_selector(self, item: Dict[str, Any], selector: str) -> bool:
        """检查元素是否匹配CSS选择器"""
        # 简化版本的CSS选择器匹配
        if selector.startswith('#'):
            # ID选择器
            element_id = selector[1:]
            return item['attributes'].get('id') == element_id
        elif selector.startswith('.'):
            # 类选择器
            class_name = selector[1:]
            classes = item['attributes'].get('class', [])
            return class_name in classes
        elif selector.startswith('[') and selector.endswith(']'):
            # 属性选择器
            attr_match = re.search(r'\[([^=]+)=([^\]]+)\]', selector)
            if attr_match:
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2).strip('"\'')
                return item['attributes'].get(attr_name) == attr_value
        else:
            # 标签选择器
            return item['tag'] == selector

        return False

    def _matches_xpath_selector(self, item: Dict[str, Any], selector: str) -> bool:
        """检查元素是否匹配XPath选择器"""
        # 简化版本的XPath匹配
        if '[@id=' in selector:
            id_match = re.search(r"@id='([^']*)'", selector)
            if id_match:
                element_id = id_match.group(1)
                return item['attributes'].get('id') == element_id
        elif '[@class=' in selector:
            class_match = re.search(r"@class='([^']*)'", selector)
            if class_match:
                class_name = class_match.group(1)
                classes = item['attributes'].get('class', [])
                return class_name in classes
        elif item['tag'] in selector:
            return True

        return False

    def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        根据元素ID获取元素信息

        Args:
            element_id: 元素ID

        Returns:
            元素信息或None
        """
        return self.content_index.get(element_id)

    def get_elements_by_path(self, path_pattern: str) -> List[Dict[str, Any]]:
        """
        根据路径模式获取元素

        Args:
            path_pattern: 路径模式

        Returns:
            匹配的元素列表
        """
        results = []
        for element_id, item in self.content_index.items():
            if path_pattern in item['path']:
                results.append(item)

        return results

    def get_search_statistics(self) -> Dict[str, Any]:
        """
        获取搜索统计信息

        Returns:
            统计信息
        """
        total_elements = len(self.content_index)
        tag_counts = {}
        depth_counts = {}

        for item in self.content_index.values():
            tag = item['tag']
            depth = item['depth']

            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            depth_counts[depth] = depth_counts.get(depth, 0) + 1

        return {
            'total_elements': total_elements,
            'tag_distribution': tag_counts,
            'depth_distribution': depth_counts
        }
