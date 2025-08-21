"""
结构化数据存储系统

基于HTML简化技术，存储标签结构和内容映射
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import pickle
from pathlib import Path
from datetime import datetime


class StructuredDataStore:
    """结构化数据存储器"""

    def __init__(self, storage_path: str = "data_store"):
        """
        初始化数据存储器

        Args:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # 内存中的数据缓存
        self.structures = {}  # 存储简化结构
        self.content_maps = {}  # 存储内容映射
        self.metadata = {}  # 存储元数据

    def store_html_data(self, source_id: str, html_data: Dict[str, Any]) -> str:
        """
        存储HTML数据

        Args:
            source_id: 数据源ID
            html_data: HTML数据（包含简化结构和内容映射）

        Returns:
            存储的文档ID
        """
        doc_id = f"{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 提取数据
        simplified_html = html_data.get('simplified_html', '')
        content_mapping = html_data.get('content_mapping', {})
        search_index = html_data.get('search_index', {})
        simplification_stats = html_data.get('simplification_stats', {})

        # 构建结构化数据
        structure_data = {
            'doc_id': doc_id,
            'source_id': source_id,
            'created_at': datetime.now().isoformat(),
            'simplified_html': simplified_html,
            'content_mapping': content_mapping,
            'search_index': search_index,
            'simplification_stats': simplification_stats
        }

        # 存储到内存
        self.structures[doc_id] = structure_data
        self.content_maps[doc_id] = content_mapping

        # 存储到文件
        self._save_to_file(doc_id, structure_data)

        return doc_id

    def _save_to_file(self, doc_id: str, data: Dict[str, Any]):
        """保存数据到文件"""
        file_path = self.storage_path / f"{doc_id}.json"

        # 转换为可序列化的格式
        serializable_data = self._make_serializable(data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)

    def _make_serializable(self, obj: Any) -> Any:
        """将对象转换为可序列化的格式"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

    def load_html_data(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        加载HTML数据

        Args:
            doc_id: 文档ID

        Returns:
            HTML数据或None
        """
        # 首先尝试从内存加载
        if doc_id in self.structures:
            return self.structures[doc_id]

        # 从文件加载
        file_path = self.storage_path / f"{doc_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.structures[doc_id] = data
                return data

        return None

    def search_content(self, keyword: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        在所有存储的数据中搜索内容

        Args:
            keyword: 搜索关键字
            search_type: 搜索类型

        Returns:
            搜索结果
        """
        results = []

        for doc_id, structure_data in self.structures.items():
            content_mapping = structure_data.get('content_mapping', {})

            for tag_id, info in content_mapping.items():
                if self._matches_search(keyword, info, search_type):
                    results.append({
                        'doc_id': doc_id,
                        'tag_id': tag_id,
                        'info': info,
                        'match_type': self._get_match_type(keyword, info)
                    })

        return results

    def _matches_search(self, keyword: str, info: Dict[str, Any], search_type: str) -> bool:
        """检查是否匹配搜索条件"""
        keyword_lower = keyword.lower()

        # 搜索标签名
        if search_type in ['all', 'tag']:
            if keyword_lower in info.get('tag', '').lower():
                return True

        # 搜索文本内容
        if search_type in ['all', 'text']:
            text_content = info.get('text_content', '')
            if text_content and keyword_lower in text_content.lower():
                return True

        # 搜索属性
        if search_type in ['all', 'attribute']:
            attributes = info.get('attributes', {})
            for attr_name, attr_value in attributes.items():
                if isinstance(attr_value, list):
                    attr_value = ' '.join(attr_value)
                if keyword_lower in str(attr_value).lower():
                    return True

        return False

    def _get_match_type(self, keyword: str, info: Dict[str, Any]) -> str:
        """获取匹配类型"""
        keyword_lower = keyword.lower()

        if keyword_lower in info.get('tag', '').lower():
            return 'tag'
        elif info.get('text_content', '') and keyword_lower in info.get('text_content', '').lower():
            return 'text'
        else:
            return 'attribute'

    def get_element_info(self, doc_id: str, tag_id: str) -> Optional[Dict[str, Any]]:
        """
        获取特定元素的详细信息

        Args:
            doc_id: 文档ID
            tag_id: 标签ID

        Returns:
            元素信息
        """
        structure_data = self.load_html_data(doc_id)
        if not structure_data:
            return None

        content_mapping = structure_data.get('content_mapping', {})
        return content_mapping.get(tag_id)

    def get_simplified_structure(self, doc_id: str) -> Optional[str]:
        """
        获取简化后的HTML结构

        Args:
            doc_id: 文档ID

        Returns:
            简化HTML字符串
        """
        structure_data = self.load_html_data(doc_id)
        if not structure_data:
            return None

        return structure_data.get('simplified_html')

    def list_documents(self) -> List[str]:
        """
        列出所有存储的文档

        Returns:
            文档ID列表
        """
        return list(self.structures.keys())

    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档ID

        Returns:
            是否成功删除
        """
        # 从内存删除
        if doc_id in self.structures:
            del self.structures[doc_id]

        if doc_id in self.content_maps:
            del self.content_maps[doc_id]

        # 从文件删除
        file_path = self.storage_path / f"{doc_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def get_storage_statistics(self) -> Dict[str, Any]:
        """
        获取存储统计信息

        Returns:
            统计信息
        """
        total_docs = len(self.structures)
        total_elements = 0
        tag_distribution = {}

        for structure_data in self.structures.values():
            content_mapping = structure_data.get('content_mapping', {})
            total_elements += len(content_mapping)

            for info in content_mapping.values():
                tag = info.get('tag', 'unknown')
                tag_distribution[tag] = tag_distribution.get(tag, 0) + 1

        return {
            'total_documents': total_docs,
            'total_elements': total_elements,
            'tag_distribution': tag_distribution,
            'storage_path': str(self.storage_path)
        }
