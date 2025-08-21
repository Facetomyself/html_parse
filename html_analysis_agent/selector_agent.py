"""
XPath和CSS选择器生成智能体

基于LangGraph框架，使用HTML简化技术来帮助生成XPath和CSS选择器
"""

from typing import Dict, List, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import re

from .html_parser import HTMLParser
from .element_locator import ElementLocator
from .utils import Utils


class SelectorAgent:
    """XPath和CSS选择器生成智能体"""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0,
        max_tokens: int = 200000,
        max_retries: int = 2,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        初始化选择器生成智能体

        Args:
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            api_key: API密钥（可选，从环境变量读取）
            api_base: API基础URL（可选，从环境变量读取）
        """
        # 加载环境变量
        load_dotenv()

        # 配置LLM
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        api_base = api_base or os.getenv("OPENAI_API_BASE")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            api_key=api_key,
            base_url=api_base
        )

        # 初始化工具
        # 动态导入以避免循环依赖
        from tools.html_simplifier import HTMLSimplifier
        self.html_simplifier = HTMLSimplifier()
        self.html_parser = HTMLParser()
        self.element_locator = ElementLocator()
        self.utils = Utils()

        # 修复HTMLSimplifier的解析器引用
        self.html_simplifier.html_parser = self.html_parser

        # 内存检查点
        self.memory = InMemorySaver()

        # 存储简化后的HTML结构和原始内容映射
        self.simplified_structure = None
        self.content_mapping = {}  # 存储标签ID到内容的映射

    def analyze_html_with_simplification(self, html_content: str) -> Dict[str, Any]:
        """
        使用HTML简化技术分析HTML内容

        Args:
            html_content: 原始HTML内容

        Returns:
            包含简化结构和内容的分析结果
        """
        # 简化HTML结构
        simplified_html = self.html_simplifier.simplify_html_string(html_content)

        # 提取结构树
        structure_tree = self.html_simplifier.extract_structure_tree(html_content)

        # 构建内容映射（为简化后的标签创建内容索引）
        self._build_content_mapping(html_content)

        # 获取简化统计
        stats = self.html_simplifier.get_simplification_stats()

        return {
            'simplified_html': simplified_html,
            'structure_tree': structure_tree,
            'content_mapping': self.content_mapping,
            'simplification_stats': stats
        }

    def _build_content_mapping(self, html_content: str) -> None:
        """构建内容映射，为简化后的标签创建内容索引"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # 遍历所有有意义的内容标签
        content_tags = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                       'a', 'button', 'input', 'textarea', 'select', 'option',
                       'li', 'dt', 'dd', 'blockquote', 'pre', 'code']

        for tag in soup.find_all(content_tags):
            # 为每个标签生成唯一ID
            tag_id = self._generate_tag_id(tag)

            # 提取文本内容
            text_content = tag.get_text(strip=True)

            # 提取属性
            attributes = dict(tag.attrs)

            if text_content or attributes:
                self.content_mapping[tag_id] = {
                    'tag': tag.name,
                    'text_content': text_content[:200] + '...' if len(text_content) > 200 else text_content,
                    'attributes': attributes,
                    'xpath': self._generate_xpath(tag),
                    'css_selector': self._generate_css_selector(tag)
                }

    def _generate_tag_id(self, tag) -> str:
        """为标签生成唯一ID"""
        if tag.get('id'):
            return f"id_{tag['id']}"
        elif tag.get('class'):
            return f"class_{'_'.join(tag['class'][:2])}"
        else:
            # 使用标签名和位置生成ID
            return f"tag_{tag.name}_{hash(str(tag)) % 10000}"

    def _generate_xpath(self, tag) -> str:
        """生成XPath表达式"""
        # 简化版XPath生成
        if tag.get('id'):
            return f"//*[@id='{tag['id']}']"

        xpath_parts = []
        current = tag
        while current and current.name != '[document]':
            # 计算兄弟元素位置
            siblings = [s for s in current.parent.children if hasattr(s, 'name') and s.name == current.name]
            if len(siblings) > 1:
                index = siblings.index(current) + 1
                xpath_parts.append(f"{current.name}[{index}]")
            else:
                xpath_parts.append(current.name)

            current = current.parent

        xpath_parts.reverse()
        return "/" + "/".join(xpath_parts)

    def _generate_css_selector(self, tag) -> str:
        """生成CSS选择器"""
        if tag.get('id'):
            return f"#{tag['id']}"

        if tag.get('class'):
            # 使用第一个class
            return f".{tag['class'][0]}"

        # 使用标签名
        return tag.name

    def generate_selectors_for_element(self, html_content: str, element_description: str) -> Dict[str, Any]:
        """
        为指定元素生成XPath和CSS选择器

        Args:
            html_content: HTML内容
            element_description: 元素描述（如"红色按钮"、"用户名输入框"等）

        Returns:
            包含生成的各种选择器的结果
        """
        # 先分析HTML结构
        analysis_result = self.analyze_html_with_simplification(html_content)

        # 构建简化的上下文信息
        context = self._build_context_for_selector_generation(analysis_result, element_description)

        # 使用LLM生成选择器
        prompt = f"""
你是一个专业的Web自动化专家，需要为用户描述的元素生成准确的XPath和CSS选择器。

用户要查找的元素：{element_description}

HTML页面结构（已简化，去除了具体内容）：
{context}

基于以上简化结构，请生成以下选择器：

1. 推荐的XPath选择器（优先使用id，然后是class，最后使用结构定位）
2. 推荐的CSS选择器（同样优先级）
3. 备选的其他选择器方案

请分析页面结构并给出最稳定和可靠的选择器。
"""

        response = self.llm.invoke(prompt)

        return {
            'element_description': element_description,
            'analysis_result': analysis_result,
            'generated_selectors': response.content,
            'context_used': context
        }

    def _build_context_for_selector_generation(self, analysis_result: Dict[str, Any], element_description: str) -> str:
        """构建用于选择器生成的上下文信息"""
        context_parts = []

        # 添加简化后的HTML结构
        context_parts.append("=== 简化HTML结构 ===")
        context_parts.append(analysis_result['simplified_html'][:2000])  # 限制长度

        # 添加关键内容映射（只包含相关信息）
        context_parts.append("\n=== 关键元素内容映射 ===")
        relevant_mappings = []
        for tag_id, info in analysis_result['content_mapping'].items():
            if info['text_content'] or info['attributes']:
                relevant_mappings.append(f"{tag_id}: {info['tag']} - {info['text_content'][:100]}")

        context_parts.append("\n".join(relevant_mappings[:20]))  # 限制数量

        # 添加简化统计信息
        stats = analysis_result['simplification_stats']
        context_parts.append(f"\n=== 简化统计 ===")
        context_parts.append(f"移除了 {stats['text_nodes']} 个文本节点")
        context_parts.append(f"移除了 {stats['script_tags']} 个脚本标签")
        context_parts.append(f"移除了 {stats['style_tags']} 个样式标签")
        context_parts.append(f"移除了 {stats['img_tags']} 个图片标签")
        context_parts.append(f"移除了 {stats['comments']} 个注释")

        return "\n".join(context_parts)

    def get_element_info(self, html_content: str, selector: str, selector_type: str = 'xpath') -> Dict[str, Any]:
        """
        根据选择器获取元素信息

        Args:
            html_content: HTML内容
            selector: 选择器（XPath或CSS）
            selector_type: 选择器类型 ('xpath' 或 'css')

        Returns:
            元素信息
        """
        # 先分析HTML结构
        analysis_result = self.analyze_html_with_simplification(html_content)

        # 使用原始HTML进行元素定位
        soup = BeautifulSoup(html_content, 'html.parser')

        try:
            if selector_type == 'xpath':
                # 简化版XPath查找
                if '[@id=' in selector:
                    # 提取ID值
                    id_match = re.search(r"@id='([^']*)'", selector)
                    if id_match:
                        element = soup.find(attrs={'id': id_match.group(1)})
                        elements = [element] if element else []
                    else:
                        elements = []
                else:
                    elements = []
            else:
                # CSS选择器查找
                if selector.startswith('#'):
                    # ID选择器
                    element_id = selector[1:]
                    element = soup.find(attrs={'id': element_id})
                    elements = [element] if element else []
                elif selector.startswith('.'):
                    # 类选择器
                    class_name = selector[1:]
                    element = soup.find(attrs={'class': lambda x: x and class_name in x})
                    elements = [element] if element else []
                else:
                    elements = []
        except Exception as e:
            elements = []

        if elements:
            element = elements[0]  # 取第一个匹配的元素
            return {
                'found': True,
                'selector': selector,
                'selector_type': selector_type,
                'text_content': element.get_text(strip=True),
                'attributes': dict(element.attrs),
                'tag_name': element.name,
                'analysis_result': analysis_result
            }
        else:
            return {
                'found': False,
                'selector': selector,
                'selector_type': selector_type,
                'analysis_result': analysis_result
            }
