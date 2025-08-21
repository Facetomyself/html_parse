"""
工具函数

提供通用的辅助功能
"""

from typing import List, Dict, Any, Union
import json
import os


class Utils:
    """工具类"""

    @staticmethod
    def save_results_to_file(results: Union[str, Dict, List], filename: str) -> bool:
        """
        将结果保存到文件

        Args:
            results: 分析结果
            filename: 文件名

        Returns:
            保存是否成功
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(results, (dict, list)):
                    json.dump(results, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(results))
            return True
        except Exception as e:
            print(f"保存文件错误: {e}")
            return False

    @staticmethod
    def load_html_file(file_path: str) -> str:
        """
        加载HTML文件

        Args:
            file_path: HTML文件路径

        Returns:
            HTML内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"读取HTML文件错误: {e}")

    @staticmethod
    def validate_html_content(html_content: str) -> bool:
        """
        验证HTML内容是否有效

        Args:
            html_content: HTML内容

        Returns:
            是否有效
        """
        if not html_content or not isinstance(html_content, str):
            return False

        html_content = html_content.strip()
        if len(html_content) < 10:
            return False

        # 检查是否包含基本的HTML标签
        basic_tags = ['<html', '<head', '<body', '<div', '<p', '<span']
        has_basic_tags = any(tag in html_content.lower() for tag in basic_tags)

        return has_basic_tags

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本内容

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 移除多余的空白字符
        text = ' '.join(text.split())

        # 移除特殊字符
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

        return text.strip()

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 文本内容
            top_n: 返回关键词数量

        Returns:
            关键词列表
        """
        try:
            # 简单的关键词提取（基于词频）
            words = text.split()
            word_count = {}

            # 统计词频（排除常见停用词）
            stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '或', '一个', '没有', '我们', '你们', '他们', '这个', '那个', '这些', '那些', '这样', '那样'}

            for word in words:
                word = word.strip('，。；：！？""''（）【】《》')
                if len(word) > 1 and word not in stop_words:
                    word_count[word] = word_count.get(word, 0) + 1

            # 返回频率最高的词
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:top_n]]

        except Exception:
            return []

    @staticmethod
    def format_output(data: Union[str, Dict, List], format_type: str = 'text') -> str:
        """
        格式化输出结果

        Args:
            data: 数据
            format_type: 格式类型 ('text', 'json', 'html')

        Returns:
            格式化后的字符串
        """
        try:
            if format_type == 'json':
                if isinstance(data, str):
                    return data
                return json.dumps(data, ensure_ascii=False, indent=2)

            elif format_type == 'html':
                if isinstance(data, str):
                    return f"<html><body><pre>{data}</pre></body></html>"
                else:
                    json_str = json.dumps(data, ensure_ascii=False, indent=2)
                    return f"<html><body><pre>{json_str}</pre></body></html>"

            else:  # text format
                if isinstance(data, str):
                    return data
                elif isinstance(data, (dict, list)):
                    return json.dumps(data, ensure_ascii=False, indent=2)
                else:
                    return str(data)

        except Exception as e:
            return f"格式化错误: {e}"

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        try:
            stat = os.stat(file_path)
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': stat.st_size,
                'modified_time': stat.st_mtime,
                'exists': True
            }
        except Exception:
            return {
                'file_path': file_path,
                'exists': False,
                'error': '无法获取文件信息'
            }
