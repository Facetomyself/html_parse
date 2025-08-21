"""
HTML解析核心功能

基于HTML简化技术和结构化存储的解析器
"""

from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from tools.html_simplifier import HTMLSimplifier
from tools.html_content_search import HTMLContentSearch
from tools.structured_data_store import StructuredDataStore


class HTMLParser:
    """HTML解析器"""

    def __init__(self):
        self.simplifier = HTMLSimplifier()
        self.searcher = HTMLContentSearch()
        self.data_store = StructuredDataStore()

    def parse_html_elements(self, html_content: str, element_descriptions: str = "") -> Dict[str, Any]:
        """
        解析HTML内容，提取关键元素的xpath和css选择器

        Args:
            html_content: HTML内容
            element_descriptions: 用户对要查找的元素的描述

        Returns:
            解析结果字典
        """
        try:
            # 使用简化技术和搜索构建索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"html_parse_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 基于描述搜索相关元素
            search_results = []
            if element_descriptions:
                # 分割描述中的关键字
                keywords = element_descriptions.split()
                for keyword in keywords:
                    keyword_results = self.searcher.search_by_keyword(keyword)
                    search_results.extend(keyword_results)
            else:
                # 如果没有描述，搜索常见的交互元素
                common_keywords = ['button', 'input', 'form', 'link', 'title', 'submit']
                for keyword in common_keywords:
                    keyword_results = self.searcher.search_by_keyword(keyword)
                    search_results.extend(keyword_results)

            # 去重和排序
            seen_paths = set()
            unique_results = []
            for result in search_results:
                path = result.get('path', '')
                if path not in seen_paths:
                    seen_paths.add(path)
                    unique_results.append(result)

            # 限制结果数量
            unique_results = unique_results[:20]

            # 生成XPath和CSS选择器
            parsed_elements = []
            for result in unique_results:
                element_info = {
                    'tag': result.get('tag', ''),
                    'path': result.get('path', ''),
                    'attributes': result.get('attributes', {}),
                    'text_content': result.get('text_content', ''),
                    'xpath_selector': self._generate_xpath(result),
                    'css_selector': self._generate_css_selector(result)
                }
                parsed_elements.append(element_info)

            return {
                'doc_id': doc_id,
                'elements': parsed_elements,
                'search_results': unique_results,
                'simplification_stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"HTML解析错误: {str(e)}"}

    def _generate_xpath(self, element_data: Dict[str, Any]) -> str:
        """生成元素的XPath"""
        try:
            # 基于路径信息生成XPath
            path = element_data.get('path', '')
            if path:
                return f"//{path.replace('/', '/')}"
            else:
                return f"//{element_data.get('tag', 'unknown')}"

        except Exception as e:
            return f"//{element_data.get('tag', 'unknown')}"

    def _generate_css_selector(self, element_data: Dict[str, Any]) -> str:
        """生成元素的CSS选择器"""
        try:
            attributes = element_data.get('attributes', {})

            # 优先使用id
            if 'id' in attributes:
                return f"#{attributes['id']}"

            # 其次使用类
            if 'class' in attributes:
                classes = attributes['class']
                if isinstance(classes, list):
                    return f"{element_data.get('tag', '')}.{'.'.join(classes)}"
                else:
                    return f"{element_data.get('tag', '')}.{classes}"

            # 最后使用标签名
            return element_data.get('tag', 'unknown')
        except Exception as e:
            return element_data.get('tag', 'unknown')

    def search_and_extract(self, html_content: str, keywords: List[str], search_type: str = 'all') -> Dict[str, Any]:
        """
        搜索并提取相关内容

        Args:
            html_content: HTML内容
            keywords: 搜索关键词列表
            search_type: 搜索类型

        Returns:
            搜索和提取结果
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"search_extract_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 执行搜索
            all_results = []
            for keyword in keywords:
                results = self.searcher.search_by_keyword(keyword, search_type)
                all_results.extend(results)

            # 去重和排序
            unique_results = self._deduplicate_results(all_results)

            return {
                'doc_id': doc_id,
                'search_results': unique_results,
                'keywords': keywords,
                'simplified_html': search_data.get('simplified_html', ''),
                'stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"搜索提取错误: {str(e)}"}

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重搜索结果"""
        seen = set()
        unique_results = []

        for result in results:
            # 使用路径和标签作为唯一标识
            identifier = (result.get('path', ''), result.get('tag', ''))
            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)

        return unique_results[:50]  # 限制数量

    def get_stored_data(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取存储的数据

        Args:
            doc_id: 文档ID

        Returns:
            存储的数据
        """
        return self.data_store.load_html_data(doc_id)
