from typing import Dict, Any, Optional
import requests
import json
from config.line_config import lineToken, getUserProfileUrl, getGroupProfileUrl, sendReplyMessageUrl
import logging

class LineJoinService:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {lineToken}'
        }
        self.logger = logging.getLogger(__name__)

    def handle_follow_event(self, event: Dict[str, Any]) -> None:
        """處理用戶追蹤事件"""
        try:
            user_id = event['source']['userId']
            user_profile = self.get_user_profile(user_id)
            self.logger.info(f"New follower: {user_profile.get('displayName', 'Unknown')}")
            
            # 在處理 follow 事件時回覆使用者
            reply_token = event.get('replyToken')
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': "你好~~我是熱量糾察隊～糾察你的熱量攝取,你可以提供你的食物照片,讓我幫你判斷你攝取了多少熱量,也可以查詢過往紀錄以及簡單的規劃為未來幾天的熱量攝取,現在請先提供你的性別,年齡(歲),身高(cm),體重(kg)一定要有單位,以及對什麼食物過敏"
                }])
            
            # 在這裡可以加入資料庫處理邏輯
            return user_profile
        except Exception as e:
            self.logger.error(f"Error handling follow event: {str(e)}")
            return None

    def handle_unfollow_event(self, event: Dict[str, Any]) -> None:
        """處理用戶取消追蹤事件"""
        try:
            user_id = event['source']['userId']
            self.logger.info(f"User unfollowed: {user_id}")
            # TODO在這裡可以加入資料庫處理邏輯
            return user_id
        except Exception as e:
            self.logger.error(f"Error handling unfollow event: {str(e)}")
            return None

    def handle_join_event(self, event: Dict[str, Any]) -> None:
        """處理加入群組事件"""
        try:
            group_id = event['source']['groupId']
            group_summary = self.get_group_summary(group_id)
            self.logger.info(f"Joined group: {group_summary.get('groupName', 'Unknown')}")
            # 在這裡可以加入資料庫處理邏輯
            return group_summary
        except Exception as e:
            self.logger.error(f"Error handling join event: {str(e)}")
            return None

    def get_source_id(self, event: Dict[str, Any]) -> Optional[str]:
        """擷取事件來源的識別碼(用戶ID或群組ID)"""
        try:
            source_type = event['source']['type']
            if source_type == 'user':
                return event['source']['userId']
            elif source_type == 'group':
                return event['source']['groupId']
            else:
                self.logger.warning(f"Unsupported source type: {source_type}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting source ID: {str(e)}")
            return None

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """獲取用戶資料"""
        try:
            url = getUserProfileUrl.format(userId=user_id)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return None

    def get_group_summary(self, group_id: str) -> Optional[Dict[str, Any]]:
        """獲取群組資訊"""
        try:
            url = getGroupProfileUrl.format(groupId=group_id)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error getting group summary: {str(e)}")
            return None
            
# TODO send reply need trainsfer to event bus and commit to adapter pattern