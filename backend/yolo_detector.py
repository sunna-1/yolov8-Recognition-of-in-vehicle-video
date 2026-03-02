"""YOLO目标检测模块"""
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Tuple
from .config import YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD, YOLO_IOU_THRESHOLD, TRAFFIC_RELATED_CLASSES


class YOLODetector:
    """YOLO目标检测器"""
    
    def __init__(self, model_path: str = YOLO_MODEL_PATH):
        """
        初始化YOLO检测器
        
        Args:
            model_path: YOLO模型路径
        """
        self.model = YOLO(model_path)
        self.traffic_class_ids = set(TRAFFIC_RELATED_CLASSES.values())
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        对单帧进行目标检测
        
        Args:
            frame: 输入帧（numpy数组，BGR格式）
            
        Returns:
            检测结果列表，每个结果包含：
            {
                'class_id': int,
                'class_name': str,
                'confidence': float,
                'bbox': [x1, y1, x2, y2],
                'center': (x, y)
            }
        """
        results = self.model(
            frame,
            conf=YOLO_CONFIDENCE_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # 只保留路况相关类别
                if class_id in self.traffic_class_ids:
                    class_name = result.names[class_id]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    detections.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'center': (float((x1 + x2) / 2), float((y1 + y2) / 2))
                    })
        
        return detections
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Dict]]:
        """
        批量检测多帧
        
        Args:
            frames: 帧列表
            
        Returns:
            每帧的检测结果列表
        """
        results = self.model(
            frames,
            conf=YOLO_CONFIDENCE_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False
        )
        
        all_detections = []
        for result in results:
            boxes = result.boxes
            frame_detections = []
            
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                if class_id in self.traffic_class_ids:
                    class_name = result.names[class_id]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    frame_detections.append({
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'center': (float((x1 + x2) / 2), float((y1 + y2) / 2))
                    })
            
            all_detections.append(frame_detections)
        
        return all_detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        在帧上绘制检测结果
        
        Args:
            frame: 输入帧
            detections: 检测结果列表
            
        Returns:
            绘制了检测框的帧
        """
        import cv2
        
        # 类别颜色映射
        colors = {
            'person': (0, 255, 0),      # 绿色
            'car': (255, 0, 0),         # 蓝色
            'truck': (0, 0, 255),       # 红色
            'bus': (255, 165, 0),       # 橙色
            'motorcycle': (255, 0, 255), # 紫色
            'bicycle': (0, 255, 255),   # 黄色
            'traffic light': (255, 255, 0), # 青色
            'stop sign': (128, 0, 128), # 紫色
            'parking meter': (255, 192, 203) # 粉色
        }
        
        for det in detections:
            class_name = det['class_name']
            bbox = det['bbox']
            confidence = det['confidence']
            
            color = colors.get(class_name, (255, 255, 255))
            x1, y1, x2, y2 = map(int, bbox)
            
            # 绘制边界框
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = f"{class_name} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            label_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            
            cv2.rectangle(frame, (x1, label_y - label_size[1] - 5), 
                         (x1 + label_size[0], label_y), color, -1)
            cv2.putText(frame, label, (x1, label_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame



