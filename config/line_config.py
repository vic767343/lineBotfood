#line config

import os

lineToken = os.getenv('LINETOKEN')    # 從環境變量中獲取 LINE Token 


getUserProfileUrl = "https://api.line.me/v2/bot/profile/{userId}"
getGroupProfileUrl = "https://api.line.me/v2/bot/group/{groupId}/summary"
sendReplyMessageUrl = "https://api.line.me/v2/bot/message/reply"
getContentURL = "https://api-data.line.me/v2/bot/message/{messageId}/content"
# LINE Bot 配置字典（方便統一管理）