"""Flask API服务"""
from flask import Flask, request, jsonify, send_file, url_for
from flask_cors import CORS
import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from .video_processor import VideoProcessor
from .yolo_detector import YOLODetector
from .analyzer import TrafficAnalyzer
from .config import (
    VIDEO_UPLOAD_FOLDER, 
    VIDEO_PROCESSED_FOLDER,
    ALLOWED_VIDEO_EXTENSIONS,
    API_HOST,
    API_PORT,
    API_DEBUG
)
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# 全局对象
detector = YOLODetector()
analyzer = TrafficAnalyzer()
latest_preview_cache = {}
latest_class_index = {}
latest_video_info = {}
latest_representative_frames = []


def encode_preview_image(frame, max_width: int = 640) -> str:
    """将帧压缩为可视化预览图"""
    height, width = frame.shape[:2]
    if width > max_width:
        scale = max_width / width
        frame = cv2.resize(frame, (int(width * scale), int(height * scale)))
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buffer).decode('utf-8')


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    if 'video' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(VIDEO_UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return jsonify({
            'message': '上传成功',
            'filename': filename,
            'filepath': filepath
        }), 200
    
    return jsonify({'error': '不支持的文件类型'}), 400


@app.route('/api/process', methods=['POST'])
def process_video():
    """处理视频并进行分析"""
    data = request.json
    video_path = data.get('video_path')
    use_camera = data.get('use_camera', False)
    camera_index = data.get('camera_index', 0)
    
    if not video_path and not use_camera:
        return jsonify({'error': '需要提供视频路径或启用摄像头'}), 400
    
    try:
        global latest_preview_cache, latest_class_index, latest_video_info, latest_representative_frames
        # 重置分析器
        analyzer.reset()
        latest_preview_cache = {}
        latest_class_index = {}
        latest_representative_frames = []
        
        # 创建视频处理器
        source = camera_index if use_camera else video_path
        processor = VideoProcessor(source)
        video_info = processor.get_video_info()
        latest_video_info = video_info
        video_writer = None
        annotated_video_filename = None
        annotated_video_url = None

        def create_annotated_writer():
            """尽量使用浏览器友好的编码（优先H.264，其次mp4v）"""
            nonlocal annotated_video_filename
            os.makedirs(VIDEO_PROCESSED_FOLDER, exist_ok=True)
            original_name = Path(video_path).stem
            annotated_video_filename = f"{original_name}_annotated.mp4"
            annotated_path = os.path.join(VIDEO_PROCESSED_FOLDER, annotated_video_filename)
            fps = video_info['fps'] if video_info['fps'] and video_info['fps'] > 0 else 25.0
            frame_size = (video_info['width'], video_info['height'])

            # 依次尝试多种编码，优先浏览器支持较好的H.264
            for codec in ('avc1', 'H264', 'mp4v'):
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    writer = cv2.VideoWriter(annotated_path, fourcc, fps, frame_size)
                    if writer.isOpened():
                        print(f'使用编码 {codec} 生成标注视频: {annotated_path}')
                        return writer, annotated_path
                    writer.release()
                except Exception as exc:
                    print(f'创建编码 {codec} 的视频失败: {exc}')
            print('所有视频编码尝试失败，将不生成标注视频')
            return None, None

        if not use_camera and video_path:
            video_writer, annotated_path = create_annotated_writer()
            if video_writer and annotated_path:
                annotated_video_url = url_for(
                    'get_annotated_video',
                    filename=annotated_video_filename,
                    _external=True
                )
        
        # 处理视频帧
        frame_results = []
        max_frames = 1000  # 限制处理帧数，避免处理时间过长
        representative_candidates = []
        
        frame_count = 0
        for frame_number, frame in processor.read_frames():
            if frame_count >= max_frames:
                break
            
            # 检测
            detections = detector.detect(frame)
            
            # 添加到分析器并获取带track信息的检测
            processed_detections = analyzer.add_frame_detections(frame_number, detections)
            
            # 绘制检测结果
            annotated_frame = detector.draw_detections(frame.copy(), processed_detections)
            
            detection_count = len(processed_detections)
            frame_summary = {
                'frame_number': frame_number,
                'detection_count': detection_count,
                'detections': processed_detections
            }
            frame_results.append(frame_summary)

            if detection_count > 0:
                preview_image = encode_preview_image(annotated_frame)
                latest_preview_cache[frame_number] = preview_image
                representative_candidates.append({
                    'frame_number': frame_number,
                    'detection_count': detection_count,
                    'classes': list({det['class_name'] for det in processed_detections}),
                    'timestamp': round(
                        frame_number / video_info['fps'], 2
                    ) if video_info.get('fps') else 0,
                    'preview_image': preview_image
                })
            
            if video_writer:
                try:
                    video_writer.write(annotated_frame)
                except Exception as write_exc:
                    print(f"写入标注视频失败: {write_exc}")
                    video_writer = None
            frame_count += 1
        
        processor.release()
        if video_writer:
            video_writer.release()
        
        # 分析数据
        analysis_result = analyzer.analyze()
        class_frame_index = analysis_result.get('class_frame_index', {})

        # 代表性帧：选择检测数量最多的若干帧
        representative_candidates.sort(key=lambda x: x['detection_count'], reverse=True)
        latest_representative_frames = representative_candidates[:6]

        # 丰富类别索引，附带预览
        enriched_class_index = {}
        for class_name, entries in class_frame_index.items():
            enriched_entries = []
            for entry in entries:
                preview = latest_preview_cache.get(entry['frame_number'])
                enriched_entries.append({
                    **entry,
                    'preview_image': preview
                })
            enriched_class_index[class_name] = enriched_entries
        latest_class_index = enriched_class_index
        
        return jsonify({
            'success': True,
            'video_info': video_info,
            'analysis': analysis_result,
            'frame_results': frame_results[:100],  # 只返回前100帧的结果
            'representative_frames': latest_representative_frames,
            'class_frame_index': enriched_class_index,
            'annotated_video_url': annotated_video_url
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['GET'])
def get_analysis():
    """获取分析结果"""
    analysis_result = analyzer.analyze()
    return jsonify(analysis_result), 200


@app.route('/api/search_frames', methods=['GET'])
def search_frames():
    """按类别检索包含目标的帧"""
    class_name = request.args.get('class')
    if not class_name:
        return jsonify({'error': '需要提供class参数'}), 400
    frames = latest_class_index.get(class_name, [])
    return jsonify({
        'class_name': class_name,
        'frames': frames
    }), 200


@app.route('/api/video/annotated/<path:filename>', methods=['GET'])
def get_annotated_video(filename):
    """提供标注后的视频文件"""
    safe_path = os.path.normpath(filename)
    if safe_path.startswith('..'):
        return jsonify({'error': '非法路径'}), 400
    full_path = os.path.join(VIDEO_PROCESSED_FOLDER, safe_path)
    if not os.path.exists(full_path):
        return jsonify({'error': '文件不存在'}), 404
    return send_file(full_path, mimetype='video/mp4')


@app.route('/api/detect_frame', methods=['POST'])
def detect_frame():
    """实时检测单帧（用于摄像头）"""
    data = request.json
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'error': '没有提供图像数据'}), 400
    
    try:
        # 解码base64图像
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(BytesIO(image_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 检测
        detections = detector.detect(frame)
        
        # 绘制检测结果
        annotated_frame = detector.draw_detections(frame.copy(), detections)
        
        # 转换回base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'detections': detections,
            'detection_count': len(detections),
            'annotated_image': f'data:image/jpeg;base64,{annotated_base64}'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """启动摄像头实时检测"""
    data = request.json
    camera_index = data.get('camera_index', 0)
    
    try:
        processor = VideoProcessor(camera_index)
        video_info = processor.get_video_info()
        
        return jsonify({
            'success': True,
            'message': '摄像头已启动',
            'video_info': video_info
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 使用 run_backend.py 启动服务

