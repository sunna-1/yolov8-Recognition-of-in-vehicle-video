"""数据分析模块"""
from typing import List, Dict
from collections import defaultdict, Counter
import numpy as np
from dataclasses import dataclass, field
from math import hypot


@dataclass
class Track:
    """简单跟踪器中的轨迹"""
    track_id: int
    class_name: str
    last_center: tuple
    last_frame: int


class SimpleTracker:
    """极简追踪器，用于估算唯一出现的目标数量"""

    def __init__(self, max_distance: float = 80.0, max_frame_gap: int = 5):
        self.max_distance = max_distance
        self.max_frame_gap = max_frame_gap
        self.tracks: List[Track] = []
        self.next_track_id = 1
        self.unique_counts = Counter()

    def reset(self):
        self.tracks = []
        self.next_track_id = 1
        self.unique_counts = Counter()

    def assign_tracks(self, frame_number: int, detections: List[Dict]) -> List[Dict]:
        """
        为检测结果分配track_id，并估算唯一目标数量
        """
        processed = []
        for det in detections:
            class_name = det['class_name']
            center = det.get('center')
            if center is None:
                processed.append(det)
                continue

            matched_track = None
            min_distance = self.max_distance

            for track in self.tracks:
                if track.class_name != class_name:
                    continue
                if frame_number - track.last_frame > self.max_frame_gap:
                    continue
                distance = hypot(center[0] - track.last_center[0], center[1] - track.last_center[1])
                if distance < min_distance:
                    min_distance = distance
                    matched_track = track

            if matched_track:
                matched_track.last_center = center
                matched_track.last_frame = frame_number
                det['track_id'] = matched_track.track_id
            else:
                track_id = self.next_track_id
                self.next_track_id += 1
                self.tracks.append(Track(track_id, class_name, center, frame_number))
                self.unique_counts[class_name] += 1
                det['track_id'] = track_id

            processed.append(det)

        # 清理过期轨迹
        self.tracks = [
            track for track in self.tracks
            if frame_number - track.last_frame <= self.max_frame_gap
        ]
        return processed

    def get_unique_counts(self) -> Dict[str, int]:
        return dict(self.unique_counts)


class TrafficAnalyzer:
    """路况数据分析器"""
    
    def __init__(self):
        self.frame_detections = []  # 存储每帧的检测结果
        self.tracker = SimpleTracker()
    
    def add_frame_detections(self, frame_number: int, detections: List[Dict]) -> List[Dict]:
        """
        添加一帧的检测结果，并返回包含track_id的检测
        """
        processed = self.tracker.assign_tracks(frame_number, detections)
        self.frame_detections.append({
            'frame_number': frame_number,
            'detections': processed
        })
        return processed
    
    def analyze(self) -> Dict:
        """
        分析所有检测数据并生成统计报告
        
        Returns:
            分析结果字典
        """
        if not self.frame_detections:
            return self._empty_analysis()
        
        # 统计各类别数量
        class_counts = Counter()
        class_confidence_sum = defaultdict(float)
        class_confidence_count = defaultdict(int)
        
        # 统计每帧的检测数量
        frame_counts = []
        total_detections = 0
        
        # 统计车辆类型
        vehicle_types = {
            'car': 0,
            'truck': 0,
            'bus': 0,
            'motorcycle': 0,
            'bicycle': 0
        }
        
        # 统计交通设施
        traffic_facilities = {
            'traffic light': 0,
            'stop sign': 0,
            'parking meter': 0
        }
        
        # 统计人员
        person_count = 0
        
        for frame_data in self.frame_detections:
            detections = frame_data['detections']
            frame_count = len(detections)
            frame_counts.append(frame_count)
            total_detections += frame_count
            
            for det in detections:
                class_name = det['class_name']
                confidence = det['confidence']
                
                class_counts[class_name] += 1
                class_confidence_sum[class_name] += confidence
                class_confidence_count[class_name] += 1
                
                # 分类统计
                if class_name in vehicle_types:
                    vehicle_types[class_name] += 1
                elif class_name in traffic_facilities:
                    traffic_facilities[class_name] += 1
                elif class_name == 'person':
                    person_count += 1
        
        # 计算平均置信度
        avg_confidence = {}
        for class_name in class_counts.keys():
            if class_confidence_count[class_name] > 0:
                avg_confidence[class_name] = (
                    class_confidence_sum[class_name] / 
                    class_confidence_count[class_name]
                )
        
        # 计算统计指标
        avg_detections_per_frame = total_detections / len(self.frame_detections)
        max_detections_in_frame = max(frame_counts) if frame_counts else 0
        min_detections_in_frame = min(frame_counts) if frame_counts else 0
        
        # 计算密度变化（使用滑动窗口）
        density_trend = self._calculate_density_trend(frame_counts)
        
        class_frame_index = self._build_class_frame_index()
        
        # 车辆统计：总数量 / 该类型出现的帧数（平均每出现帧的数量）
        vehicle_frame_counts = {}
        vehicle_statistics_avg_per_frame = {}
        for vtype in vehicle_types:
            frames_with_type = [e for e in class_frame_index.get(vtype, [])]
            n_frames = len(frames_with_type)
            vehicle_frame_counts[vtype] = n_frames
            total = vehicle_types[vtype]
            if n_frames > 0:
                vehicle_statistics_avg_per_frame[vtype] = round(total / n_frames, 2)
            else:
                vehicle_statistics_avg_per_frame[vtype] = 0

        return {
            'total_frames': len(self.frame_detections),
            'total_detections': total_detections,
            'avg_detections_per_frame': round(avg_detections_per_frame, 2),
            'max_detections_in_frame': max_detections_in_frame,
            'min_detections_in_frame': min_detections_in_frame,
            'class_distribution': dict(class_counts),
            'avg_confidence': avg_confidence,
            'vehicle_statistics': vehicle_types,
            'vehicle_frame_counts': vehicle_frame_counts,
            'vehicle_statistics_avg_per_frame': vehicle_statistics_avg_per_frame,
            'traffic_facilities': traffic_facilities,
            'person_count': person_count,
            'density_trend': density_trend,
            'traffic_density_level': self._calculate_density_level(avg_detections_per_frame),
            'unique_detections': self.tracker.get_unique_counts(),
            'class_frame_index': class_frame_index
        }
    
    def _build_class_frame_index(self) -> Dict[str, List[Dict]]:
        """构建按类别索引的帧信息"""
        class_index: Dict[str, List[Dict]] = defaultdict(list)
        for frame_data in self.frame_detections:
            frame_number = frame_data['frame_number']
            per_class = defaultdict(list)
            for det in frame_data['detections']:
                per_class[det['class_name']].append(det)
            
            for class_name, detections in per_class.items():
                class_index[class_name].append({
                    'frame_number': frame_number,
                    'detection_count': len(detections),
                    'track_ids': [det.get('track_id') for det in detections if det.get('track_id')],
                    'avg_confidence': round(
                        sum(det['confidence'] for det in detections) / len(detections),
                        3
                    )
                })
        return class_index
    
    def _calculate_density_trend(self, frame_counts: List[int], window_size: int = 10) -> List[float]:
        """
        计算密度趋势（使用滑动平均）
        
        Args:
            frame_counts: 每帧的检测数量
            window_size: 滑动窗口大小
            
        Returns:
            趋势值列表
        """
        if len(frame_counts) < window_size:
            return [float(np.mean(frame_counts))] * len(frame_counts)
        
        trend = []
        for i in range(len(frame_counts)):
            start = max(0, i - window_size // 2)
            end = min(len(frame_counts), i + window_size // 2 + 1)
            trend.append(float(np.mean(frame_counts[start:end])))
        
        return trend
    
    def _calculate_density_level(self, avg_detections: float) -> str:
        """
        计算交通密度等级
        
        Args:
            avg_detections: 平均每帧检测数量
            
        Returns:
            密度等级字符串
        """
        if avg_detections < 2:
            return '稀疏'
        elif avg_detections < 5:
            return '正常'
        elif avg_detections < 10:
            return '较密集'
        else:
            return '非常密集'
    
    def _empty_analysis(self) -> Dict:
        """返回空分析结果"""
        return {
            'total_frames': 0,
            'total_detections': 0,
            'avg_detections_per_frame': 0,
            'max_detections_in_frame': 0,
            'min_detections_in_frame': 0,
            'class_distribution': {},
            'avg_confidence': {},
            'vehicle_statistics': {},
            'vehicle_frame_counts': {},
            'vehicle_statistics_avg_per_frame': {},
            'traffic_facilities': {},
            'person_count': 0,
            'density_trend': [],
            'traffic_density_level': '未知'
        }
    
    def reset(self):
        """重置分析器"""
        self.frame_detections = []
        self.tracker.reset()



