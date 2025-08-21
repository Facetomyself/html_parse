"""
HTML简化工具类

将HTML文档简化为只包含结构信息的简化版本，
移除实际内容但保留标签结构、属性和层次关系。
"""

from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
import re
from pathlib import Path


class HTMLSimplifier:
    """HTML简化工具类"""

    def __init__(self):
        """初始化HTML简化器"""
        self.removed_content_stats = {
            'text_nodes': 0,
            'script_tags': 0,
            'style_tags': 0,
            'img_tags': 0,
            'comments': 0
        }

    def simplify_html_file(self, file_path: str) -> str:
        """
        简化HTML文件

        Args:
            file_path: HTML文件路径

        Returns:
            简化后的HTML字符串
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return self.simplify_html_string(html_content)

    def simplify_html_string(self, html_content: str) -> str:
        """
        简化HTML字符串

        Args:
            html_content: HTML内容字符串

        Returns:
            简化后的HTML字符串
        """
        # 重置统计信息
        self.removed_content_stats = {
            'text_nodes': 0,
            'script_tags': 0,
            'style_tags': 0,
            'img_tags': 0,
            'comments': 0
        }

        # 解析HTML
        soup = BeautifulSoup(html_content, 'lxml')

        # 简化处理
        self._remove_content(soup)
        self._clean_attributes(soup)
        self._normalize_structure(soup)

        return str(soup)

    def _remove_content(self, soup: BeautifulSoup) -> None:
        """移除内容，保留结构"""

        # 移除script标签
        for script in soup.find_all('script'):
            self.removed_content_stats['script_tags'] += 1
            script.decompose()

        # 移除style标签
        for style in soup.find_all('style'):
            self.removed_content_stats['style_tags'] += 1
            style.decompose()

        # 移除img标签
        for img in soup.find_all('img'):
            self.removed_content_stats['img_tags'] += 1
            img.decompose()

        # 移除注释
        for comment in soup.find_all(string=lambda string: isinstance(string, type(soup.parser.make_comment("")) if soup.parser else str)):
            self.removed_content_stats['comments'] += 1
            comment.extract()

        # 清理文本内容
        self._clean_text_content(soup)

    def _clean_text_content(self, element) -> None:
        """递归清理文本内容"""
        if hasattr(element, 'children'):
            for child in list(element.children):
                if isinstance(child, Tag):
                    # 递归处理子标签
                    self._clean_text_content(child)
                elif hasattr(child, 'strip') and child.strip():
                    # 处理文本节点
                    self.removed_content_stats['text_nodes'] += 1
                    # 保留结构标记，但移除具体内容
                    if len(child.strip()) > 50:  # 长文本用简短占位符
                        child.replace_with('[TEXT_CONTENT]')
                    else:
                        child.replace_with('[TEXT]')
                elif str(child).strip():
                    # 处理其他类型的文本节点
                    self.removed_content_stats['text_nodes'] += 1
                    if len(str(child).strip()) > 50:
                        child.replace_with('[TEXT_CONTENT]')
                    else:
                        child.replace_with('[TEXT]')

    def _clean_attributes(self, soup: BeautifulSoup) -> None:
        """清理和简化属性"""

        # 需要保留的重要属性
        important_attrs = {
            'id', 'class', 'name', 'type', 'value',
            'href', 'src', 'alt', 'title', 'data-*'
        }

        for tag in soup.find_all():
            if isinstance(tag, Tag):
                attrs_to_remove = []
                for attr, value in tag.attrs.items():
                    should_keep = False

                    # 检查是否是重要属性
                    if attr in important_attrs:
                        should_keep = True
                    elif attr.startswith('data-'):
                        should_keep = True
                    elif attr in ['style', 'onclick', 'onload']:
                        # 移除样式和事件属性
                        pass
                    elif len(str(value)) > 200:
                        # 移除过长的属性值
                        pass
                    else:
                        should_keep = True

                    if not should_keep:
                        attrs_to_remove.append(attr)

                # 移除不需要的属性
                for attr in attrs_to_remove:
                    del tag.attrs[attr]

    def _normalize_structure(self, soup: BeautifulSoup) -> None:
        """标准化HTML结构"""
        # 确保HTML文档结构完整
        if not soup.html:
            html_tag = soup.new_tag('html')
            soup.wrap(html_tag)

        if not soup.head:
            head_tag = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head_tag)

        if not soup.body:
            body_tag = soup.new_tag('body')
            if soup.html:
                soup.html.append(body_tag)

    def get_simplification_stats(self) -> Dict[str, int]:
        """
        获取简化统计信息

        Returns:
            统计信息字典
        """
        return self.removed_content_stats.copy()

    def extract_structure_tree(self, html_content: str) -> Dict[str, Any]:
        """
        提取HTML结构树

        Args:
            html_content: HTML内容

        Returns:
            结构树字典
        """
        soup = BeautifulSoup(html_content, 'lxml')
        return self._build_structure_tree(soup)

    def _build_structure_tree(self, element, depth: int = 0) -> Dict[str, Any]:
        """构建结构树"""
        if not isinstance(element, Tag):
            return None

        tree = {
            'tag': element.name,
            'attributes': dict(element.attrs),
            'depth': depth,
            'children': []
        }

        for child in element.children:
            if isinstance(child, Tag):
                child_tree = self._build_structure_tree(child, depth + 1)
                if child_tree:
                    tree['children'].append(child_tree)

        return tree
