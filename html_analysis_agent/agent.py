"""
HTML Analysis Agent - 主要的Agent类

提供统一的接口来使用各种HTML分析功能
"""

from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os

from .html_parser import HTMLParser
from .data_analyzer import DataAnalyzer
from .element_locator import ElementLocator
from .change_detector import ChangeDetector
from .selector_agent import SelectorAgent

# 加载环境变量
load_dotenv()


class HTMLAnalysisAgent:
    """HTML分析Agent主类"""

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
        初始化Agent

        Args:
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            api_key: API密钥（可选，从环境变量读取）
            api_base: API基础URL（可选，从环境变量读取）
        """
        # 配置LLM
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        api_base = api_base or os.getenv("OPENAI_API_BASE")

        if not api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY in environment or pass api_key parameter.")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            api_key=api_key,
            base_url=api_base
        )

        # 初始化工具类
        self.html_parser = HTMLParser()
        self.data_analyzer = DataAnalyzer()
        self.element_locator = ElementLocator()
        self.change_detector = ChangeDetector()
        self.selector_agent = SelectorAgent(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            api_key=api_key,
            api_base=api_base
        )

        # 创建LangGraph Agent
        self._setup_agent()

    def _setup_agent(self):
        """设置LangGraph Agent"""
        tools = [
            self.parse_html,
            self.analyze_data_containers,
            self.analyze_element_positions,
            self.detect_changes,
            self.generate_selectors,
            self.analyze_html_with_simplification,
            self.get_element_info,
            self.search_html_content,
            self.find_elements_by_xpath,
            self.find_elements_by_css
        ]

        checkpointer = InMemorySaver()

        prompt = """你是一个专业的HTML解析和分析助手，能够：
1. 解析HTML内容并提取关键元素的xpath和css选择器
2. 记住用户传入的HTML内容，可以在后续交互中参考
3. 提供准确的元素定位信息

基础功能：
- parse_html_elements: 基础的HTML元素解析
- get_stored_html_info: 获取已存储HTML的统计信息
- analyze_data_containers: 专门分析表格和列表结构
- analyze_element_positions: 分析元素位置关系和层级结构
- detect_changes: 检测HTML内容的版本变化

使用建议：
- 解析新的HTML时，使用parse_html获取基础信息
- 需要深入分析数据结构时，使用analyze_data_containers
- 查找特定元素位置时，使用analyze_element_positions
- 比较不同HTML版本时，使用detect_changes

请始终提供清晰、格式化的输出，并根据用户需求选择最合适的工具。"""

        self.agent = create_react_agent(
            model=self.llm,
            tools=tools,
            checkpointer=checkpointer,
            prompt=prompt
        )

    def parse_html(self, html_content: str, element_descriptions: str = "") -> Dict[str, Any]:
        """
        解析HTML内容并提取关键元素

        Args:
            html_content: HTML内容
            element_descriptions: 元素描述（可选）

        Returns:
            解析结果字典
        """
        return self.html_parser.parse_html_elements(html_content, element_descriptions)

    def analyze_data_containers(self, html_content: str) -> Dict[str, Any]:
        """
        分析HTML中的数据容器

        Args:
            html_content: HTML内容

        Returns:
            数据容器分析结果字典
        """
        return self.data_analyzer.analyze_data_containers(html_content)

    def analyze_element_positions(self, html_content: str, target_xpath: str = "") -> Dict[str, Any]:
        """
        分析元素位置关系

        Args:
            html_content: HTML内容
            target_xpath: 目标元素XPath（可选）

        Returns:
            位置分析结果字典
        """
        return self.element_locator.analyze_element_positions(html_content, target_xpath)

    def detect_changes(self, html_content: str, previous_html: str = "") -> Dict[str, Any]:
        """
        检测HTML内容变化

        Args:
            html_content: 当前HTML内容
            previous_html: 之前的HTML内容（可选）

        Returns:
            变化检测结果字典
        """
        return self.change_detector.detect_changes(html_content, previous_html)

    def search_html_content(self, html_content: str, keywords: List[str], search_type: str = 'all') -> Dict[str, Any]:
        """
        搜索HTML内容中的关键词

        Args:
            html_content: HTML内容
            keywords: 搜索关键词列表
            search_type: 搜索类型

        Returns:
            搜索结果字典
        """
        return self.html_parser.search_and_extract(html_content, keywords, search_type)

    def find_elements_by_xpath(self, html_content: str, xpath: str) -> Dict[str, Any]:
        """
        根据XPath查找元素

        Args:
            html_content: HTML内容
            xpath: XPath表达式

        Returns:
            查找结果字典
        """
        return self.element_locator.find_elements_by_xpath(html_content, xpath)

    def find_elements_by_css(self, html_content: str, css_selector: str) -> Dict[str, Any]:
        """
        根据CSS选择器查找元素

        Args:
            html_content: HTML内容
            css_selector: CSS选择器

        Returns:
            查找结果字典
        """
        return self.element_locator.find_elements_by_css(html_content, css_selector)

    def analyze_with_agent(self, query: str, html_content: str = "", thread_id: str = "default") -> str:
        """
        使用LangGraph Agent进行智能分析

        Args:
            query: 用户查询
            html_content: HTML内容（可选）
            thread_id: 会话ID

        Returns:
            Agent响应
        """
        config = {"configurable": {"thread_id": thread_id}}

        # 如果提供了HTML内容，将其包含在查询中
        if html_content:
            full_query = f"{query}\n\nHTML内容：\n{html_content}"
        else:
            full_query = query

        result = self.agent.invoke(
            {
                "messages": [{"role": "user", "content": full_query}]
            },
            config
        )

        return result["messages"][-1].content

    def batch_analyze_html_files(self, file_paths: List[str], output_dir: str = "analysis_results"):
        """
        批量分析HTML文件

        Args:
            file_paths: HTML文件路径列表
            output_dir: 输出目录
        """
        import os

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        results = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # 基础解析
                basic_result = self.parse_html(html_content)

                # 数据容器分析
                data_result = self.analyze_data_containers(html_content)

                # 综合结果
                result = {
                    "file": file_path,
                    "file_size": len(html_content),
                    "basic_analysis": basic_result,
                    "data_analysis": data_result
                }

                results.append(result)

                # 保存单个文件结果
                filename = os.path.basename(file_path).replace('.html', '_analysis.txt')
                output_path = os.path.join(output_dir, filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"文件: {file_path}\n")
                    f.write(f"文件大小: {len(html_content):,} 字符\n")
                    f.write("=" * 60 + "\n\n")
                    f.write("基础解析结果:\n")
                    f.write(basic_result)
                    f.write("\n" + "=" * 60 + "\n\n")
                    f.write("数据容器分析:\n")
                    f.write(data_result)

            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")

        return results

    def analyze_html_with_simplification(self, html_content: str) -> Dict[str, Any]:
        """
        使用HTML简化技术分析HTML内容

        Args:
            html_content: HTML内容

        Returns:
            简化分析结果
        """
        return self.selector_agent.analyze_html_with_simplification(html_content)

    def generate_selectors(self, html_content: str, element_description: str) -> Dict[str, Any]:
        """
        为指定元素生成XPath和CSS选择器

        Args:
            html_content: HTML内容
            element_description: 元素描述

        Returns:
            生成的选择器结果
        """
        return self.selector_agent.generate_selectors_for_element(html_content, element_description)

    def get_element_info(self, html_content: str, selector: str, selector_type: str = 'xpath') -> Dict[str, Any]:
        """
        根据选择器获取元素信息

        Args:
            html_content: HTML内容
            selector: 选择器
            selector_type: 选择器类型

        Returns:
            元素信息
        """
        return self.selector_agent.get_element_info(html_content, selector, selector_type)
