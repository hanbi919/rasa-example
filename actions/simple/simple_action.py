from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import re


class ActionValidateNameEmail(Action):
    def name(self) -> Text:
        return "action_validate_name_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 获取当前槽位值
        email = tracker.get_slot("email")
        name = tracker.get_slot("name")

        # 验证邮箱格式
        if email and not self._is_valid_email(email):
            dispatcher.utter_message(text="这个邮箱地址看起来不太对，请提供一个有效的邮箱地址。")
            return [SlotSet("email", None)]

        return []

    @staticmethod
    def _is_valid_email(email: Text) -> bool:
        """验证邮箱格式"""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None
