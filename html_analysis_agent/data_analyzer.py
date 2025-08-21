"""
数据容器分析功能

基于HTML简化技术和结构化存储的数据容器分析
"""

from typing import List, Dict, Any, Optional


class DataAnalyzer:
    """数据容器分析器"""

    def __init__(self):
        # 延迟导入以避免循环依赖
        from tools.html_simplifier import HTMLSimplifier
        from tools.html_content_search import HTMLContentSearch
        from tools.structured_data_store import StructuredDataStore

        self.simplifier = HTMLSimplifier()
        self.searcher = HTMLContentSearch()
        self.data_store = StructuredDataStore()

    def analyze_data_containers(self, html_content: str) -> Dict[str, Any]:
        """
        智能识别和分析HTML中的数据容器

        Args:
            html_content: HTML内容

        Returns:
            数据容器分析结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"data_analysis_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 基于关键字搜索数据容器
            data_container_keywords = [
                'product', 'detail', 'spec', 'info', 'property',
                'table', 'list', 'data', 'content', 'item'
            ]

            # 执行搜索
            search_results = []
            for keyword in data_container_keywords:
                results = self.searcher.search_by_keyword(keyword)
                search_results.extend(results)

            # 分类和分析数据容器
            container_analysis = self._analyze_container_types(search_results)

            return {
                'doc_id': doc_id,
                'containers': container_analysis,
                'search_results': search_results[:20],  # 限制数量
                'simplified_html': search_data.get('simplified_html', ''),
                'stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"数据容器分析错误: {str(e)}"}

    def analyze_tables(self, html_content: str) -> Dict[str, Any]:
        """
        分析HTML中的表格结构

        Args:
            html_content: HTML内容

        Returns:
            表格分析结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"table_analysis_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 搜索表格相关元素
            table_keywords = ['table', 'thead', 'tbody', 'tr', 'th', 'td']
            table_results = []
            for keyword in table_keywords:
                results = self.searcher.search_by_keyword(keyword)
                table_results.extend(results)

            # 分析表格结构
            table_analysis = self._analyze_table_structure(table_results)

            return {
                'doc_id': doc_id,
                'table_analysis': table_analysis,
                'table_elements': table_results[:20],
                'simplified_html': search_data.get('simplified_html', ''),
                'stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"表格分析错误: {str(e)}"}

    def analyze_lists(self, html_content: str) -> Dict[str, Any]:
        """
        分析HTML中的列表结构

        Args:
            html_content: HTML内容

        Returns:
            列表分析结果字典
        """
        try:
            # 构建搜索索引
            search_data = self.searcher.build_search_index(html_content)

            # 存储数据
            source_id = f"list_analysis_{hash(html_content) % 10000}"
            doc_id = self.data_store.store_html_data(source_id, search_data)

            # 搜索列表相关元素
            list_keywords = ['ul', 'ol', 'dl', 'li', 'dt', 'dd']
            list_results = []
            for keyword in list_keywords:
                results = self.searcher.search_by_keyword(keyword)
                list_results.extend(results)

            # 分析列表结构
            list_analysis = self._analyze_list_structure(list_results)

            return {
                'doc_id': doc_id,
                'list_analysis': list_analysis,
                'list_elements': list_results[:20],
                'simplified_html': search_data.get('simplified_html', ''),
                'stats': search_data.get('simplification_stats', {})
            }

        except Exception as e:
            return {'error': f"列表分析错误: {str(e)}"}

    def _analyze_container_types(self, search_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """分析和分类数据容器"""
        container_types = {
            'product_details': [],
            'property_lists': [],
            'tables': [],
            'data_containers': [],
            'other': []
        }

        for result in search_results:
            tag = result.get('tag', '').lower()
            attributes = result.get('attributes', {})
            text_content = result.get('text_content', '').lower()

            # 产品详情容器
            if (self._matches_keywords(text_content, ['product', 'detail', 'spec', 'info']) or
                self._matches_attributes(attributes, ['product', 'detail', 'spec', 'info'])):
                container_types['product_details'].append(result)

            # 属性列表
            elif tag in ['ul', 'ol', 'dl'] and (
                self._matches_attributes(attributes, ['info', 'property', 'spec', 'attr', 'detail']) or
                self._matches_keywords(text_content, ['property', 'spec', 'attribute'])):
                container_types['property_lists'].append(result)

            # 表格
            elif tag in ['table', 'tbody', 'thead', 'tr', 'th', 'td']:
                container_types['tables'].append(result)

            # 通用数据容器
            elif (self._matches_attributes(attributes, ['data', 'content', 'item', 'list']) or
                  self._matches_keywords(text_content, ['data', 'content', 'item'])):
                container_types['data_containers'].append(result)

            else:
                container_types['other'].append(result)

        return container_types

    def _analyze_table_structure(self, table_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析表格结构"""
        tables = []
        headers = []
        rows = []

        for result in table_results:
            tag = result.get('tag', '').lower()
            if tag == 'table':
                tables.append(result)
            elif tag in ['th', 'thead']:
                headers.append(result)
            elif tag in ['tr', 'td', 'tbody']:
                rows.append(result)

        return {
            'total_tables': len(tables),
            'header_elements': headers[:10],
            'data_rows': rows[:20],
            'table_structure': tables[:5]
        }

    def _analyze_list_structure(self, list_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析列表结构"""
        unordered_lists = []
        ordered_lists = []
        definition_lists = []
        list_items = []

        for result in list_results:
            tag = result.get('tag', '').lower()
            if tag == 'ul':
                unordered_lists.append(result)
            elif tag == 'ol':
                ordered_lists.append(result)
            elif tag == 'dl':
                definition_lists.append(result)
            elif tag in ['li', 'dt', 'dd']:
                list_items.append(result)

        return {
            'unordered_lists': unordered_lists[:5],
            'ordered_lists': ordered_lists[:5],
            'definition_lists': definition_lists[:5],
            'list_items': list_items[:20]
        }

    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """检查文本是否匹配关键词"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def _matches_attributes(self, attributes: Dict[str, Any], keywords: List[str]) -> bool:
        """检查属性是否匹配关键词"""
        for attr_name, attr_value in attributes.items():
            attr_name_lower = attr_name.lower()
            if isinstance(attr_value, list):
                attr_value_str = ' '.join(str(v).lower() for v in attr_value)
            else:
                attr_value_str = str(attr_value).lower()

            if any(keyword.lower() in attr_name_lower or keyword.lower() in attr_value_str
                   for keyword in keywords):
                return True
        return False
