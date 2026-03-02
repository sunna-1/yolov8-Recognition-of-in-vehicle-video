"""后端服务启动脚本"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.config import API_HOST, API_PORT, API_DEBUG

if __name__ == '__main__':
    print(f"启动后端服务在 http://{API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)








