import logging
from flask import Flask, request
from application import app

# 設置日誌記錄器
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try: 
        app.debug = True
        app.run(host='127.0.0.1', port=1997)
    except Exception as e:
        logger.error(f"應用程式啟動失敗: {str(e)}", exc_info=True)  


