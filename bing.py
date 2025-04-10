from typing import Dict, Any, List
try:
    from autotask.nodes import Node, register_node
    from autotask.api_keys import get_api_key
except:
    from ..stub import Node, register_node, get_api_key
import requests


BING_API_KEY = get_api_key(provider="bing.microsoft.com", key_name="BING_API_KEY")


@register_node
class BingNewsSearchNode(Node):
    NAME = "Bing News Search"
    DESCRIPTION = "使用 Bing 搜索新闻，返回新闻标题和描述"

    INPUTS = {
        "query": {
            "label": "搜索关键词",
            "description": "输入要搜索的新闻关键词",
            "type": "STRING",
            "required": True
        },
        "count": {
            "label": "结果数量",
            "description": "返回的新闻数量（1-100）",
            "type": "INT",
            "default": 10,
            "required": False
        }
    }

    OUTPUTS = {
        "news_results": {
            "label": "新闻结果",
            "description": "包含新闻标题和描述的列表",
            "type": "LIST"
        }
    }

    def __init__(self):
        self.base_url = "https://api.bing.microsoft.com/v7.0/news/search"
        self.api_key = BING_API_KEY

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        try:
            print(f"Bing News Search Node 执行中...")
            query = node_inputs["query"]
            count = int(node_inputs.get("count", 10))
            count = min(max(count, 1), 100)  # 限制在1-100之间
            

            api_key = self.api_key

            headers = {"Ocp-Apim-Subscription-Key": api_key}
            params = {
                "q": query,
                "count": count,
                "textDecorations": True,
                "textFormat": "HTML"
            }

            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            response_data = response.json()

            news_list = response_data.get('value', [])
            formatted_results = self._format_news_results(news_list)

            return {
                "success": True,
                "news_results": formatted_results
            }

        except Exception as e:
            workflow_logger.error(f"Bing News 搜索失败: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def _format_news_results(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """格式化新闻搜索结果"""
        formatted_results = []
        for news in news_list:
            formatted_results.append({
                "title": news.get("name", "无标题"),
                "description": news.get("description", "无描述"),
                "url": news.get("url", ""),
                "date_published": news.get("datePublished", ""),
                "provider": news.get("provider", [{}])[0].get("name", "")
            })
        return formatted_results
