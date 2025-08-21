"""
HTML Analysis Agent - 智能HTML解析和分析工具

这个包提供了一套完整的HTML解析和分析功能，包括：
- HTML元素解析和选择器生成
- 智能数据容器识别
- 元素位置关系分析
- HTML变化检测
- 结构化报告生成
"""

from .agent import HTMLAnalysisAgent
from .html_parser import HTMLParser
from .data_analyzer import DataAnalyzer
from .element_locator import ElementLocator
from .change_detector import ChangeDetector

__version__ = "1.0.0"
__author__ = "HTML Analysis Agent Team"
__description__ = "智能HTML解析和分析工具"

__all__ = [
    'HTMLAnalysisAgent',
    'HTMLParser',
    'DataAnalyzer',
    'ElementLocator',
    'ChangeDetector'
]
