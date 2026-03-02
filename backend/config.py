"""配置文件"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 视频相关配置
VIDEO_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'videos')
VIDEO_PROCESSED_FOLDER = os.path.join(BASE_DIR, 'uploads', 'processed')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv'}

# YOLO模型配置
YOLO_MODEL_PATH = 'yolov8n.pt'  # 使用YOLOv8 nano模型，可根据需要更换
YOLO_CONFIDENCE_THRESHOLD = 0.25
YOLO_IOU_THRESHOLD = 0.45

# 检测类别（COCO数据集的类别）
DETECTION_CLASSES = {
    'person': 0,
    'bicycle': 1,
    'car': 2,
    'motorcycle': 3,
    'airplane': 4,
    'bus': 5,
    'train': 6,
    'truck': 7,
    'boat': 8,
    'traffic light': 9,
    'fire hydrant': 10,
    'stop sign': 11,
    'parking meter': 12,
    'bench': 13,
    'bird': 14,
    'cat': 15,
    'dog': 16,
    'horse': 17,
    'sheep': 18,
    'cow': 19,
    'elephant': 20,
    'bear': 21,
    'zebra': 22,
    'giraffe': 23,
    'backpack': 24,
    'umbrella': 25,
    'handbag': 26,
    'tie': 27,
    'suitcase': 28,
    'frisbee': 29,
    'skis': 30,
    'snowboard': 31,
    'sports ball': 32,
    'kite': 33,
    'baseball bat': 34,
    'baseball glove': 35,
    'skateboard': 36,
    'surfboard': 37,
    'tennis racket': 38,
    'bottle': 39,
    'wine glass': 40,
    'cup': 41,
    'fork': 42,
    'knife': 43,
    'spoon': 44,
    'bowl': 45,
    'banana': 46,
    'apple': 47,
    'sandwich': 48,
    'orange': 49,
    'broccoli': 50,
    'carrot': 51,
    'hot dog': 52,
    'pizza': 53,
    'donut': 54,
    'cake': 55,
    'chair': 56,
    'couch': 57,
    'potted plant': 58,
    'bed': 59,
    'dining table': 60,
    'toilet': 61,
    'tv': 62,
    'laptop': 63,
    'mouse': 64,
    'remote': 65,
    'keyboard': 66,
    'cell phone': 67,
    'microwave': 68,
    'oven': 69,
    'toaster': 70,
    'sink': 71,
    'refrigerator': 72,
    'book': 73,
    'clock': 74,
    'vase': 75,
    'scissors': 76,
    'teddy bear': 77,
    'hair drier': 78,
    'toothbrush': 79
}

# 路况相关类别（重点关注）
TRAFFIC_RELATED_CLASSES = {
    'person': 0,
    'bicycle': 1,
    'car': 2,
    'motorcycle': 3,
    'bus': 5,
    'truck': 7,
    'traffic light': 9,
    'stop sign': 11,
    'parking meter': 12,
}

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = True

# 创建必要的目录
os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_PROCESSED_FOLDER, exist_ok=True)








