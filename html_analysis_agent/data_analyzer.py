"""
数据容器分析功能

基于HTML简化技术和结构化存储的数据容器分析
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
import json

# 加载环境变量
load_dotenv()


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

        # 初始化LLM
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        self.llm = ChatOpenAI(
            model_name="gemini-2.5-flash",
            temperature=0,
            max_tokens=4000,
            api_key=api_key,
            base_url=api_base
        )

    def analyze_data_containers(self, html_content: str) -> Dict[str, Any]:
        """
        使用LLM智能识别和分析HTML中的数据容器

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

            # 简化HTML内容用于LLM分析
            simplified_html = search_data.get('simplified_html', '')
            if not simplified_html:
                simplified_html = html_content[:8000]  # 限制长度

            # 使用LLM进行智能数据容器分析
            container_analysis = self._analyze_containers_with_llm(simplified_html)

            return {
                'doc_id': doc_id,
                'containers': container_analysis,
                'simplified_html': simplified_html,
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

    def _analyze_containers_with_llm(self, html_content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用LLM智能分析HTML中的数据容器

        Args:
            html_content: HTML内容

        Returns:
            分类后的数据容器字典
        """
        try:
            # 构建通用分析提示
            analysis_prompt = f"""
你是一个专业的HTML内容分析专家，请分析以下HTML内容，识别并分类其中的各种数据容器和内容结构。

HTML内容：
{html_content[:6000]}  # 限制长度避免token超限

请按以下格式返回JSON结果，分类应该基于内容的实际用途和结构特征：

{{
    "content_containers": [
        {{
            "tag": "div",
            "description": "主要内容容器",
            "content_preview": "主要内容文本预览...",
            "attributes": {{"class": "main-content", "id": "content"}},
            "importance": "high",
            "content_type": "article|blog|product|news|etc"
        }}
    ],
    "navigation_menus": [
        {{
            "tag": "nav",
            "description": "导航菜单",
            "content_preview": "菜单项预览...",
            "attributes": {{"class": "nav-menu"}},
            "importance": "medium"
        }}
    ],
    "data_tables": [
        {{
            "tag": "table",
            "description": "数据表格",
            "content_preview": "表格数据预览...",
            "attributes": {{"class": "data-table"}},
            "importance": "medium"
        }}
    ],
    "form_elements": [
        {{
            "tag": "form",
            "description": "表单元素",
            "content_preview": "表单内容预览...",
            "attributes": {{"id": "contact-form"}},
            "importance": "high"
        }}
    ],
    "media_containers": [
        {{
            "tag": "div",
            "description": "媒体内容容器",
            "content_preview": "图片、视频等媒体内容...",
            "attributes": {{"class": "media-gallery"}},
            "importance": "medium"
        }}
    ],
    "interactive_elements": [
        {{
            "tag": "button",
            "description": "交互式元素",
            "content_preview": "按钮、链接等交互元素...",
            "attributes": {{"onclick": "action()"}},
            "importance": "medium"
        }}
    ],
    "metadata_containers": [
        {{
            "tag": "header",
            "description": "元数据容器",
            "content_preview": "标题、作者、时间等元数据...",
            "attributes": {{"class": "article-meta"}},
            "importance": "high"
        }}
    ],
    "list_structures": [
        {{
            "tag": "ul",
            "description": "列表结构",
            "content_preview": "列表项内容...",
            "attributes": {{"class": "feature-list"}},
            "importance": "medium"
        }}
    ],
    "decorative_elements": [
        {{
            "tag": "div",
            "description": "装饰性元素",
            "content_preview": "装饰内容...",
            "attributes": {{"class": "decoration"}},
            "importance": "low"
        }}
    ],
    "other": [
        {{
            "tag": "span",
            "description": "其他未分类元素",
            "content_preview": "其他内容...",
            "attributes": {{}},
            "importance": "low"
        }}
    ]
}}

通用分析要求：
1. 根据HTML元素的实际用途和内容特征进行智能分类
2. 识别各种网页类型的通用结构（文章、博客、电商、新闻、论坛等）
3. 评估内容的价值和重要性
4. 提取有意义的内容预览和关键属性
5. 避免将无用的装饰元素误认为重要数据容器
6. 每个类别最多返回8个最重要的容器
7. 分类应该灵活适应不同类型的网页

分类标准：
- content_containers: 主要内容区域
- navigation_menus: 导航和菜单
- data_tables: 表格数据
- form_elements: 表单和输入
- media_containers: 图片视频等媒体
- interactive_elements: 按钮、链接等交互元素
- metadata_containers: 标题、作者、时间等元信息
- list_structures: 各种列表结构
- decorative_elements: 纯装饰性元素
- other: 未分类的其他元素
"""

            # 调用LLM进行分析
            response = self.llm.invoke(analysis_prompt)
            response_text = response.content.strip()

            # 解析JSON响应
            try:
                # 尝试提取JSON部分
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.rfind('```')
                    json_content = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.rfind('```')
                    json_content = response_text[json_start:json_end].strip()
                else:
                    json_content = response_text

                # 清理JSON字符串
                json_content = json_content.replace('```json', '').replace('```', '').strip()

                result = json.loads(json_content)
                return result

            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {response_text}")
                return self._fallback_analysis(html_content)

        except Exception as e:
            print(f"LLM分析错误: {e}")
            return self._fallback_analysis(html_content)

    def _fallback_analysis(self, html_content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        后备分析方法 - 当LLM分析失败时使用简化的通用HTML分析

        Args:
            html_content: HTML内容

        Returns:
            简化的通用数据容器分类结果
        """
        container_types = {
            'content_containers': [],
            'navigation_menus': [],
            'data_tables': [],
            'form_elements': [],
            'media_containers': [],
            'interactive_elements': [],
            'metadata_containers': [],
            'list_structures': [],
            'decorative_elements': [],
            'other': []
        }

        # 简化的后备逻辑
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找各种可能的容器元素
        candidates = soup.find_all(['div', 'section', 'article', 'nav', 'header', 'footer',
                                  'table', 'form', 'ul', 'ol', 'dl', 'button', 'a',
                                  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])

        for element in candidates[:30]:  # 限制数量
            tag_name = element.name
            attrs = dict(element.attrs) if element.attrs else {}
            text_content = element.get_text()[:200].strip()
            class_attr = attrs.get('class', [])
            id_attr = attrs.get('id', '')

            # 通用分类逻辑
            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or any('title' in str(c).lower() for c in class_attr):
                container_types['metadata_containers'].append({
                    'tag': tag_name,
                    'description': '标题和元数据',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'high'
                })
            elif tag_name == 'nav' or any(nav in str(class_attr).lower() for nav in ['nav', 'menu', 'navigation']):
                container_types['navigation_menus'].append({
                    'tag': tag_name,
                    'description': '导航菜单',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            elif tag_name == 'table':
                container_types['data_tables'].append({
                    'tag': tag_name,
                    'description': '数据表格',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            elif tag_name == 'form':
                container_types['form_elements'].append({
                    'tag': tag_name,
                    'description': '表单元素',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'high'
                })
            elif any(media in str(class_attr).lower() for media in ['image', 'video', 'media', 'gallery', 'photo']):
                container_types['media_containers'].append({
                    'tag': tag_name,
                    'description': '媒体内容容器',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            elif tag_name in ['button', 'a'] or any(click in str(attrs).lower() for click in ['onclick', 'href']):
                container_types['interactive_elements'].append({
                    'tag': tag_name,
                    'description': '交互式元素',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            elif tag_name in ['ul', 'ol', 'dl']:
                container_types['list_structures'].append({
                    'tag': tag_name,
                    'description': '列表结构',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            elif any(dec in str(class_attr).lower() for dec in ['decoration', 'decorative', 'ornament', 'style']):
                container_types['decorative_elements'].append({
                    'tag': tag_name,
                    'description': '装饰性元素',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'low'
                })
            elif any(content in str(class_attr).lower() for content in ['content', 'main', 'article', 'post', 'body']):
                container_types['content_containers'].append({
                    'tag': tag_name,
                    'description': '主要内容容器',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'high'
                })
            elif len(text_content) > 10:  # 有实质内容的容器
                container_types['content_containers'].append({
                    'tag': tag_name,
                    'description': '通用内容容器',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'medium'
                })
            else:
                container_types['other'].append({
                    'tag': tag_name,
                    'description': '其他元素',
                    'content_preview': text_content,
                    'attributes': attrs,
                    'importance': 'low'
                })

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
