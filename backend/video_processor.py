"""视频处理模块"""
import cv2
import os
from typing import Optional, Generator, Tuple
from .config import VIDEO_UPLOAD_FOLDER


class VideoProcessor:
    """视频处理器，支持视频文件和摄像头输入"""
    
    def __init__(self, source: str):
        """
        初始化视频处理器
        
        Args:
            source: 视频源，可以是文件路径或摄像头索引（整数）
        """
        self.source = source
        self.cap = None
        self.is_camera = False
        
        # 判断是摄像头还是视频文件
        if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
            self.is_camera = True
            self.cap = cv2.VideoCapture(int(source))
        elif isinstance(source, str) and os.path.exists(source):
            self.cap = cv2.VideoCapture(source)
        else:
            raise ValueError(f"无效的视频源: {source}")
        
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频源: {source}")
    
    def get_video_info(self) -> dict:
        """获取视频信息"""
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        return {
            'fps': fps,
            'width': width,
            'height': height,
            'frame_count': frame_count,
            'duration': duration,
            'is_camera': self.is_camera
        }
    
    def read_frames(self) -> Generator[Tuple[int, any], None, None]:
        """
        读取视频帧的生成器
        
        Yields:
            (frame_number, frame): 帧编号和帧数据
        """
        frame_number = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame_number, frame
            frame_number += 1
    
    def read_frame(self) -> Optional[Tuple[any, int]]:
        """
        读取单帧（用于实时摄像头）
        
        Returns:
            (frame, frame_number) 或 None
        """
        ret, frame = self.cap.read()
        if ret:
            frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            return frame, frame_number
        return None
    
    def reset(self):
        """重置视频到开始位置"""
        if not self.is_camera:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def release(self):
        """释放资源"""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()



