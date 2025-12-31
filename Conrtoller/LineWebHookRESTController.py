from dataclasses import dataclass
from flask import request
import logging
from application import app
from Service.lineJoinService import LineJoinService
from Service.nlpService import NLPService
from Service.ImageProcessService import ImageProcessService


# 設置日誌記錄
logger = logging.getLogger(__name__)


@dataclass
class ParsedLineEvent:
    type: str
    user_id: str | None = None
    text: str | None = None
    image_url: str | None = None
    raw_event: dict | None = None


def parse_line_event(req) -> ParsedLineEvent:
    """最小化解析 LINE webhook 事件。

    - 優先支援 text / image message
    - 支援 join 事件（群組加入）
    - 其他事件回傳 type=原始 type 或 'unknown'
    """
    payload = req.get_json(silent=True) or {}
    if isinstance(payload, dict) and isinstance(payload.get("events"), list) and payload["events"]:
        e = payload["events"][0]
    elif isinstance(payload, dict):
        e = payload
    else:
        e = {}   

    ev_type = e.get("type") or "unknown"
    source = e.get("source") or {}
    user_id = source.get("userId")

    # message event
    if ev_type == "message":
        msg = e.get("message") or {}
        msg_type = msg.get("type")
        if msg_type == "text":
            return ParsedLineEvent(type="text", user_id=user_id, text=msg.get("text"), raw_event=e)
        if msg_type == "image":
            # 先沿用既有欄位命名（image_url）。若你有 adapter 產生 image url，可再替換。
            return ParsedLineEvent(type="image", user_id=user_id, image_url=msg.get("contentProvider", {}).get("originalContentUrl"), raw_event=e)

        return ParsedLineEvent(type=msg_type or "message", user_id=user_id, raw_event=e)

    # join event
    if ev_type == "join":
        return ParsedLineEvent(type="join", user_id=user_id, raw_event=e)

    return ParsedLineEvent(type=ev_type, user_id=user_id, raw_event=e)

@dataclass
class TextMessageCommand:
    user_id: str
    text: str

class ImageMessageCommand:
    user_id: str
    image_url: str


@dataclass
class LineJoinCommand:
    line_event: dict

@app.post("/webhook")
def webhook():
    #TODO : 解析 LINE 事件
    event = parse_line_event(request)

    if event.type == "text":
        cmd = TextMessageCommand(
            user_id=event.user_id,
            text=event.text
        )
        NLPService.handle(cmd)

    elif event.type == "image":
        cmd = ImageMessageCommand(
            user_id=event.user_id,
            image_url=event.image_url
        )
        ImageProcessService.handle(cmd)
    else:
        # join 事件處理
        if getattr(event, "type", None) == "join":
            payload = request.get_json(silent=True) or {}

            # LINE webhook payload: {"events": [ { ... } ]}
            if isinstance(payload, dict) and isinstance(payload.get("events"), list) and payload["events"]:
                line_event = payload["events"][0]
            else:
                line_event = payload if isinstance(payload, dict) else {}

            cmd = LineJoinCommand(line_event=line_event)
            LineJoinService().handle_join_event(cmd.line_event)
        else:
            logger.info(f"Unsupported LINE event type: {getattr(event, 'type', None)}")

    return "ok"
