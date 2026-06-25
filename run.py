"""后端启动入口。

    python run.py

默认监听 0.0.0.0:5000，提供 /api/* 接口（前后端分离，前端为独立 Vue 工程）。
旧的 app.py 已被本结构取代，可保留作参考或删除。
"""
from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
