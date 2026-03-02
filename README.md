# 动态路况分析系统

基于YOLO和Vue3的智能交通路况分析平台，支持视频文件和实时摄像头输入，对车辆、行人、交通标识等进行高精度识别和数据分析。
该项目使用yolov8n.pt，仅用于展示，如果你需要实际应用，最好准备好数据集进行训练

# 源码下载 
-前往 [Release](https://github.com/sunna-1/yolov8-Recognition-of-in-vehicle-video/releases) 页面下载源码（带有venv环境）
-**大小**:449MB

## 功能特性

- 🎥 **多源输入支持**：支持视频文件上传和实时摄像头接入
- 🎯 **高精度检测**：基于YOLOv8模型，检测车辆、行人、交通标识等
- 📊 **数据分析**：自动统计和分析路况数据
- 📈 **可视化展示**：Vue3前端提供精美的数据可视化界面
- 🚦 **实时检测**：支持摄像头实时识别和标注

## 技术栈

### 后端
- Python 3.8+
- Flask - Web框架
- Ultralytics YOLOv8 - 目标检测
- OpenCV - 视频处理
- NumPy, Pandas - 数据处理

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- ECharts - 数据可视化
- Axios - HTTP客户端

## 项目结构

```
project-part-one/
├── backend/                 # 后端服务
│   ├── app.py              # Flask API服务
│   ├── config.py           # 配置文件
│   ├── video_processor.py  # 视频处理模块
│   ├── yolo_detector.py    # YOLO检测模块
│   └── analyzer.py         # 数据分析模块
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.vue        # 主组件
│   │   ├── main.js        # 入口文件
│   │   └── style.css     # 样式文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── uploads/               # 上传文件目录（自动创建）
│   ├── videos/           # 视频文件
│   └── processed/        # 处理后的文件
├── requirements.txt       # Python依赖
└── README.md
```

## 安装和运行

### 1. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行后端服务

```bash
# 在项目根目录运行
python run_backend.py
```

后端服务将在 `http://localhost:5000` 启动。

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 运行前端开发服务器

```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动。

## 使用说明

### 视频文件分析

1. 打开前端应用（http://localhost:3000）
2. 点击"选择视频文件"按钮，选择要分析的视频
3. 点击"开始分析"按钮
4. 等待处理完成，查看分析结果

### 实时摄像头检测

1. 点击"启动摄像头"按钮
2. 允许浏览器访问摄像头权限
3. 系统将实时检测并标注画面中的目标
4. 点击"停止摄像头"结束检测

## API接口

### 健康检查
```
GET /api/health
```

### 上传视频
```
POST /api/upload
Content-Type: multipart/form-data
Body: video (file)
```

### 处理视频
```
POST /api/process
Content-Type: application/json
Body: {
  "video_path": "path/to/video.mp4"
}
```

### 实时检测单帧
```
POST /api/detect_frame
Content-Type: application/json
Body: {
  "image": "data:image/jpeg;base64,..."
}
```

## 检测类别

系统主要检测以下路况相关目标：

- **人员**：person
- **车辆**：car, truck, bus, motorcycle, bicycle
- **交通设施**：traffic light, stop sign, parking meter

## 分析指标

- 总帧数和总检测数
- 平均每帧检测数量
- 类别分布统计
- 车辆类型统计
- 交通设施统计
- 交通密度等级（稀疏/正常/较密集/非常密集）
- 密度趋势分析

## 配置说明

可以在 `backend/config.py` 中修改以下配置：

- `YOLO_MODEL_PATH`: YOLO模型路径（默认使用yolov8n.pt）
- `YOLO_CONFIDENCE_THRESHOLD`: 置信度阈值（默认0.25）
- `YOLO_IOU_THRESHOLD`: IOU阈值（默认0.45）
- `API_PORT`: API服务端口（默认5000）

## 注意事项

1. 首次运行时会自动下载YOLOv8模型（约6MB）
2. 视频处理可能需要较长时间，取决于视频长度和帧数
3. 实时摄像头检测需要浏览器支持getUserMedia API
4. 建议使用Chrome或Edge浏览器以获得最佳体验

## 开发计划

- [ ] 支持更多视频格式
- [ ] 添加视频导出功能（带标注）
- [ ] 优化实时检测性能
- [ ] 添加历史记录功能
- [ ] 支持自定义检测类别
- [ ] 添加报警功能（检测到特定目标时）

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

