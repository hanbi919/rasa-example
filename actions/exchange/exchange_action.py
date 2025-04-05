# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import os
from typing import Any, Text, Dict, List
import yaml  # 新增：用于加载配置文件
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# 修复：替换 ConfigLoader，直接加载配置文件


def load_config():
    config_path = os.path.join(os.path.dirname(
        __file__), "../config.yml")  # 假设配置文件在 actions/config.yml
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()  # 加载配置


class ActionExchangeRate(Action):
    def name(self) -> Text:
        return "action_exchange_rate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        currency_map = {
            "美元": "USD",
            "日元": "JPY",
            "欧元": "EUR",
            "英镑": "GBP",
            "韩元": "KRW",  # 修复：KER -> KRW（韩元正确代码）
            "港币": "HKD",
            "卢布": "RUB",
        }

        number = tracker.get_slot("number")
        currency = tracker.get_slot("currency")

        # 检查货币是否支持
        if currency not in currency_map:
            dispatcher.utter_message(text="暂时不支持该货币的汇率查询~")
            return []

        # 从配置中获取 API 参数
        try:
            _config = next(
                item for item in config["apis"] if item["name"] == "Exchange")
            url = _config["url"]
            api_key = _config["key"]
        except (KeyError, StopIteration):
            dispatcher.utter_message(text="服务配置错误，请联系管理员。")
            return []

        # 调用汇率 API
        try:
            params = {
                "key": api_key,
                "from": currency_map[currency],
                "to": "CNY",
            }
            response = requests.get(url=url, params=params, timeout=10)
            response.raise_for_status()  # 检查 HTTP 错误
            data = response.json()

            # 检查 API 返回是否有效
            if "result" not in data or not data["result"]:
                dispatcher.utter_message(text="汇率数据解析失败，请稍后再试~")
                return []

            exchange_rate = float(data["result"][0]["exchange"])
            converted_amount = round(float(number) * exchange_rate, 2)

            info = (
                f"当前汇率：\n"
                f"{currency_map[currency]} → CNY\n"
                f"1 {currency_map[currency]} = {exchange_rate} CNY\n"
                f"换算结果：{number} {currency} ≈ {converted_amount} CNY"
            )

            dispatcher.utter_message(text=info)

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text=f"网络请求失败：{str(e)}")
        except (ValueError, KeyError, IndexError):
            dispatcher.utter_message(text="汇率数据格式错误，请稍后再试~")

        return []
