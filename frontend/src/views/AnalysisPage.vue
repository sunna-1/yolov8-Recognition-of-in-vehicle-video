<template>
  <div class="analysis-page">
    <header class="app-header-bar">
      <nav class="nav-bar">
        <router-link to="/" class="nav-logo">动态路况分析系统</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">项目介绍</router-link>
          <router-link to="/analysis" class="nav-link" exact-active-class="active">开始分析</router-link>
        </div>
      </nav>
    </header>

    <main class="main-content">
      <section class="control-section">
        <div class="card">
          <h2>视频输入</h2>
          <div class="input-group">
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              accept="video/*"
              class="file-input"
            />
            <button @click="triggerFileInput" class="btn btn-primary">选择视频文件</button>
            <button @click="toggleCamera" class="btn btn-secondary">
              {{ isCameraActive ? '停止摄像头' : '启动摄像头' }}
            </button>
          </div>
          <div v-if="uploadedFile" class="file-info">
            <span>已选择: {{ uploadedFile }}</span>
            <button @click="processVideo" class="btn btn-success" :disabled="processing">
              {{ processing ? '处理中...' : '开始分析' }}
            </button>
          </div>
        </div>
      </section>

      <section v-if="videoPreview" class="preview-section">
        <div class="card">
          <h2>视频预览</h2>
          <video ref="videoPlayer" :src="videoPreview" controls class="video-player"></video>
        </div>
      </section>

      <section v-if="annotatedVideoUrl" class="preview-section">
        <div class="card">
          <h2>检测结果视频（含标注）</h2>
          <video
            v-if="annotatedVideoUrl && !annotatedVideoError"
            :src="annotatedVideoUrl"
            controls
            class="video-player annotated-video"
            preload="metadata"
            @error="annotatedVideoError = true"
          ></video>
          <p v-if="annotatedVideoError" class="video-error">
            视频在页面中播放失败，请点击下面链接在新标签页中打开查看。
          </p>
          <p class="video-tip">
            该视频基于最近一次分析生成，包含YOLO标注框。
            <a :href="annotatedVideoUrl" target="_blank" rel="noopener noreferrer">在新标签页打开标注视频</a>
          </p>
        </div>
      </section>

      <section v-if="isCameraActive" class="camera-section">
        <div class="card">
          <h2>实时检测</h2>
          <div class="camera-container">
            <video ref="cameraVideo" autoplay playsinline class="camera-video"></video>
            <canvas ref="cameraCanvas" class="camera-canvas"></canvas>
          </div>
          <div class="camera-stats" v-if="cameraStats">
            <span>检测数量: {{ cameraStats.detection_count }}</span>
          </div>
        </div>
      </section>

      <section v-if="analysisResult" class="analysis-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-content">
              <h3>总帧数</h3>
              <p class="stat-value">{{ analysisResult.total_frames }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3>总检测数</h3>
              <p class="stat-value">{{ analysisResult.total_detections }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3>唯一目标数</h3>
              <p class="stat-value">{{ uniqueDetectionTotal }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3>平均检测/帧</h3>
              <p class="stat-value">{{ analysisResult.avg_detections_per_frame }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <h3>交通密度</h3>
              <p class="stat-value">{{ analysisResult.traffic_density_level }}</p>
            </div>
          </div>
        </div>

        <section v-if="representativeFrames.length" class="sample-section">
          <div class="card">
            <h2>代表性检测帧</h2>
            <div class="sample-grid">
              <div class="sample-item" v-for="frame in representativeFrames" :key="frame.frame_number">
                <img
                  v-if="frame.preview_image"
                  :src="`data:image/jpeg;base64,${frame.preview_image}`"
                  :alt="`帧${frame.frame_number}`"
                  @click="openPreview(frame.preview_image)"
                />
                <div class="sample-meta">
                  <p>帧 {{ frame.frame_number }} · {{ formatTimestamp(frame.timestamp) }}</p>
                  <p>检测数量：{{ frame.detection_count }}</p>
                  <p>类别：{{ (frame.classes && frame.classes.length) ? frame.classes.join(' / ') : '—' }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="card chart-card">
          <h2>类别分布</h2>
          <div ref="classChart" class="chart-container"></div>
        </div>

        <div class="card">
          <h2>车辆统计</h2>
          <p class="vehicle-desc">各类车辆在出现帧中的平均每帧数量</p>
          <div class="vehicle-grid">
            <div
              class="vehicle-item"
              v-for="(count, type) in (analysisResult.vehicle_statistics_avg_per_frame || analysisResult.vehicle_statistics)"
              :key="type"
            >
              <span class="vehicle-type">{{ getVehicleName(type) }}</span>
              <span class="vehicle-count">{{ formatVehicleCount(count, type) }}</span>
            </div>
          </div>
        </div>

        <div class="card">
          <h2>交通设施</h2>
          <div class="facility-grid">
            <div
              class="facility-item"
              v-for="(count, facility) in analysisResult.traffic_facilities"
              :key="facility"
            >
              <span class="facility-name">{{ getFacilityName(facility) }}</span>
              <span class="facility-count">{{ count }}</span>
            </div>
          </div>
        </div>

        <div class="card chart-card">
          <h2>密度趋势</h2>
          <div ref="trendChart" class="chart-container"></div>
        </div>

        <section v-if="Object.keys(classFrameIndex).length" class="search-section">
          <div class="card">
            <h2>按类别查找帧</h2>
            <div class="search-controls">
              <select v-model="classFilter" @change="handleClassSearch">
                <option value="">选择类别</option>
                <option
                  v-for="(items, className) in classFrameIndex"
                  :key="className"
                  :value="className"
                >
                  {{ translateClass(className) }} ({{ items.length }})
                </option>
              </select>
              <button class="btn btn-secondary" @click="handleClassSearch">搜索</button>
            </div>
            <p v-if="!classFilter" class="empty-hint">请选择一个类别查看对应帧。</p>
            <p v-else-if="classFilter && !classSearchResults.length" class="empty-hint">
              暂无检测到该类别的帧。
            </p>
            <div v-else class="search-results">
              <div
                class="result-card"
                v-for="entry in classSearchResults"
                :key="`${classFilter}-${entry.frame_number}`"
              >
                <img
                  v-if="entry.preview_image"
                  :src="`data:image/jpeg;base64,${entry.preview_image}`"
                  :alt="`帧${entry.frame_number}`"
                  @click="openPreview(entry.preview_image)"
                />
                <div class="result-meta">
                  <p>帧 {{ entry.frame_number }}</p>
                  <p>检测数量：{{ entry.detection_count }} · 平均置信度 {{ entry.avg_confidence }}</p>
                  <p>追踪ID：{{ entry.track_ids?.length ? entry.track_ids.join(', ') : '—' }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </section>
    </main>
  </div>

  <div v-if="isPreviewOpen" class="preview-modal">
    <div class="preview-toolbar">
      <button class="btn btn-secondary" @click="zoomOut">-</button>
      <span class="zoom-label">{{ Math.round(previewZoom * 100) }}%</span>
      <button class="btn btn-secondary" @click="zoomIn">+</button>
      <button class="btn" @click="resetZoom">重置</button>
      <button class="btn btn-secondary" @click="closePreview">关闭</button>
    </div>
    <div class="preview-content">
      <img
        v-if="activePreview"
        :src="`data:image/jpeg;base64,${activePreview}`"
        :style="{ transform: `scale(${previewZoom})` }"
        alt="放大预览"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const API_BASE = '/api'
const resolveApiUrl = (url) => {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  return new URL(url, window.location.origin).href
}

export default {
  name: 'AnalysisPage',
  setup() {
    const fileInput = ref(null)
    const videoPlayer = ref(null)
    const cameraVideo = ref(null)
    const cameraCanvas = ref(null)
    const classChart = ref(null)
    const trendChart = ref(null)

    const uploadedFile = ref(null)
    const videoPreview = ref(null)
    const isCameraActive = ref(false)
    const processing = ref(false)
    const analysisResult = ref(null)
    const cameraStats = ref(null)
    const representativeFrames = ref([])
    const classFrameIndex = ref({})
    const classFilter = ref('')
    const classSearchResults = ref([])
    const annotatedVideoUrl = ref('')
    const annotatedVideoError = ref(false)
    const activePreview = ref(null)
    const isPreviewOpen = ref(false)
    const previewZoom = ref(1)

    let cameraStream = null
    let classChartInstance = null
    let trendChartInstance = null
    let cameraInterval = null

    const triggerFileInput = () => fileInput.value?.click()

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        uploadedFile.value = file.name
        videoPreview.value = URL.createObjectURL(file)
        annotatedVideoUrl.value = ''
        annotatedVideoError.value = false
      }
    }

    const processVideo = async () => {
      if (!uploadedFile.value) return
      processing.value = true
      try {
        const formData = new FormData()
        formData.append('video', fileInput.value.files[0])
        const uploadResponse = await axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const processResponse = await axios.post(`${API_BASE}/process`, {
          video_path: uploadResponse.data.filepath
        })
        analysisResult.value = processResponse.data.analysis
        representativeFrames.value = processResponse.data.representative_frames || []
        classFrameIndex.value = processResponse.data.class_frame_index || {}
        annotatedVideoError.value = false
        annotatedVideoUrl.value = resolveApiUrl(processResponse.data.annotated_video_url)
        handleClassSearch()
        await nextTick()
        renderCharts()
      } catch (error) {
        console.error('处理视频失败:', error)
        alert('处理视频失败: ' + (error.response?.data?.error || error.message))
      } finally {
        processing.value = false
      }
    }

    const toggleCamera = async () => {
      if (isCameraActive.value) stopCamera()
      else await startCamera()
    }

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 1280, height: 720 }
        })
        cameraStream = stream
        isCameraActive.value = true
        await nextTick()
        if (cameraVideo.value) cameraVideo.value.srcObject = stream
        cameraInterval = setInterval(captureAndDetect, 500)
      } catch (error) {
        console.error('启动摄像头失败:', error)
        alert('无法访问摄像头: ' + error.message)
      }
    }

    const stopCamera = () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
        cameraStream = null
      }
      if (cameraInterval) clearInterval(cameraInterval)
      cameraInterval = null
      isCameraActive.value = false
      cameraStats.value = null
    }

    const captureAndDetect = async () => {
      if (!cameraVideo.value || !cameraCanvas.value) return
      const video = cameraVideo.value
      const canvas = cameraCanvas.value
      const ctx = canvas.getContext('2d')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      ctx.drawImage(video, 0, 0)
      const imageData = canvas.toDataURL('image/jpeg', 0.8)
      try {
        const response = await axios.post(`${API_BASE}/detect_frame`, { image: imageData })
        if (response.data.success) {
          cameraStats.value = { detection_count: response.data.detection_count }
          const img = new Image()
          img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
          }
          img.src = response.data.annotated_image
        }
      } catch (error) {
        console.error('检测失败:', error)
      }
    }

    const renderCharts = () => {
      if (!analysisResult.value) return
      if (classChart.value && analysisResult.value.class_distribution) {
        if (classChartInstance) classChartInstance.dispose()
        classChartInstance = echarts.init(classChart.value)
        const classData = Object.entries(analysisResult.value.class_distribution).map(([name, value]) => ({
          value,
          name
        }))
        classChartInstance.setOption({
          backgroundColor: 'transparent',
          tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
          series: [{
            name: '类别分布',
            type: 'pie',
            radius: '60%',
            data: classData,
            itemStyle: {
              color: (params) => {
                const colors = ['#ff6b35', '#00d4aa', '#7c3aed', '#f59e0b', '#06b6d4', '#ec4899']
                return colors[params.dataIndex % colors.length]
              }
            },
            emphasis: {
              itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(255,107,53,0.5)' }
            }
          }]
        })
      }
      if (trendChart.value && analysisResult.value.density_trend) {
        if (trendChartInstance) trendChartInstance.dispose()
        trendChartInstance = echarts.init(trendChart.value)
        trendChartInstance.setOption({
          backgroundColor: 'transparent',
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: analysisResult.value.density_trend.map((_, i) => `帧${i + 1}`),
            axisLine: { lineStyle: { color: '#444' } },
            axisLabel: { color: '#a0a0b0' }
          },
          yAxis: {
            type: 'value',
            name: '检测数量',
            axisLine: { show: false },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
            axisLabel: { color: '#a0a0b0' }
          },
          series: [{
            name: '密度趋势',
            type: 'line',
            smooth: true,
            data: analysisResult.value.density_trend,
            lineStyle: { color: '#ff6b35' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(255,107,53,0.35)' },
                { offset: 1, color: 'rgba(255,107,53,0.05)' }
              ])
            }
          }]
        })
      }
    }

    const handleClassSearch = () => {
      if (!classFilter.value) {
        classSearchResults.value = []
        return
      }
      classSearchResults.value = classFrameIndex.value[classFilter.value] || []
    }

    const formatTimestamp = (seconds) => {
      if (!seconds && seconds !== 0) return '0s'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}分${secs.toString().padStart(2, '0')}秒`
    }

    const formatVehicleCount = (count, type) => {
      const avg = analysisResult.value?.vehicle_statistics_avg_per_frame?.[type]
      if (typeof avg === 'number') return avg
      return count
    }

    const uniqueDetectionTotal = computed(() => {
      if (!analysisResult.value?.unique_detections) return 0
      return Object.values(analysisResult.value.unique_detections).reduce((sum, val) => sum + val, 0)
    })

    const translateClass = (name) => {
      const mapping = {
        'person': '行人', 'car': '汽车', 'truck': '卡车', 'bus': '公交车',
        'motorcycle': '摩托车', 'bicycle': '自行车', 'traffic light': '交通灯',
        'stop sign': '停止标志', 'parking meter': '停车计费器'
      }
      return mapping[name] || name
    }

    const getVehicleName = (type) => {
      const names = { car: '汽车', truck: '卡车', bus: '公交车', motorcycle: '摩托车', bicycle: '自行车' }
      return names[type] || type
    }

    const getFacilityName = (facility) => {
      const names = { 'traffic light': '交通灯', 'stop sign': '停止标志', 'parking meter': '停车计费器' }
      return names[facility] || facility
    }

    const openPreview = (image) => {
      if (!image) return
      activePreview.value = image
      previewZoom.value = 1
      isPreviewOpen.value = true
    }

    const closePreview = () => {
      isPreviewOpen.value = false
      activePreview.value = null
    }

    const zoomIn = () => { previewZoom.value = Math.min(previewZoom.value + 0.2, 3) }
    const zoomOut = () => { previewZoom.value = Math.max(previewZoom.value - 0.2, 0.5) }
    const resetZoom = () => { previewZoom.value = 1 }

    onMounted(() => {
      axios.get(`${API_BASE}/health`).catch(() => console.error('API连接失败'))
    })

    watch(analysisResult, (val) => {
      if (val) {
        nextTick(() => {
          const stats = document.querySelectorAll('.stat-card')
          if (stats.length) {
            gsap.from(stats, {
              opacity: 0,
              y: 30,
              stagger: 0.08,
              duration: 0.6,
              ease: 'power2.out'
            })
          }
        })
      }
    })

    onUnmounted(() => {
      stopCamera()
      if (classChartInstance) classChartInstance.dispose()
      if (trendChartInstance) trendChartInstance.dispose()
    })

    return {
      fileInput,
      videoPlayer,
      cameraVideo,
      cameraCanvas,
      classChart,
      trendChart,
      uploadedFile,
      videoPreview,
      isCameraActive,
      processing,
      analysisResult,
      cameraStats,
      representativeFrames,
      classFrameIndex,
      classFilter,
      classSearchResults,
      annotatedVideoUrl,
      annotatedVideoError,
      activePreview,
      isPreviewOpen,
      previewZoom,
      uniqueDetectionTotal,
      triggerFileInput,
      handleFileSelect,
      processVideo,
      toggleCamera,
      getVehicleName,
      getFacilityName,
      handleClassSearch,
      formatTimestamp,
      formatVehicleCount,
      translateClass,
      openPreview,
      closePreview,
      zoomIn,
      zoomOut,
      resetZoom
    }
  }
}
</script>

<style scoped>
.analysis-page {
  min-height: 100vh;
  background: #0a0a0f;
  color: #e8e8ed;
}

.app-header-bar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(10, 10, 15, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 107, 53, 0.2);
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
}

.nav-logo {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ff6b35;
  text-decoration: none;
}

.nav-links { display: flex; gap: 24px; }
.nav-link { color: #a0a0b0; text-decoration: none; font-weight: 500; transition: color 0.25s; }
.nav-link:hover, .nav-link.active { color: #ff6b35; }

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 107, 53, 0.2);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.card h2 {
  font-size: 1.35rem;
  color: #ffffff;
  margin-bottom: 16px;
}

.vehicle-desc {
  color: #a0a0b0;
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.input-group { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
.file-input { display: none; }

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.25s;
  font-weight: 600;
}

.btn-primary {
  background: #ff6b35;
  color: #0a0a0f;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #e8e8ed;
  border: 1px solid rgba(255, 107, 53, 0.3);
}
.btn-secondary:hover { background: rgba(255, 107, 53, 0.2); }

.btn-success {
  background: #00d4aa;
  color: #0a0a0f;
  margin-left: 12px;
}
.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
}

.btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.file-info {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.video-player { width: 100%; border-radius: 8px; max-height: 480px; }
.annotated-video { border: 2px solid rgba(255, 107, 53, 0.3); }
.video-tip { margin-top: 10px; color: #a0a0b0; font-size: 0.9rem; }
.video-error { margin-top: 12px; color: #ff6b35; font-weight: 500; }

.camera-container { position: relative; width: 100%; max-width: 960px; margin: 0 auto; }
.camera-video { display: none; }
.camera-canvas { width: 100%; border-radius: 8px; background: #111; }
.camera-stats {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.2) 0%, rgba(124, 58, 237, 0.15) 100%);
  border: 1px solid rgba(255, 107, 53, 0.3);
  color: #e8e8ed;
  border-radius: 12px;
  padding: 20px;
}

.stat-content h3 { font-size: 0.9rem; color: #a0a0b0; margin-bottom: 8px; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: #ff6b35; }

.sample-grid {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
  scroll-snap-type: x mandatory;
}

.sample-item {
  flex: 0 0 260px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 107, 53, 0.2);
  scroll-snap-align: start;
}

.sample-item img { width: 100%; display: block; }
.sample-meta { padding: 14px; color: #c0c0d0; font-size: 0.9rem; line-height: 1.5; }

.chart-container { width: 100%; height: 360px; }

.vehicle-grid, .facility-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.vehicle-item, .facility-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  border-left: 4px solid #ff6b35;
}

.vehicle-type, .facility-name { font-weight: 500; color: #c0c0d0; }
.vehicle-count, .facility-count { font-size: 1.35rem; font-weight: 700; color: #ff6b35; }

.search-controls { display: flex; gap: 12px; margin-bottom: 16px; }
.search-controls select {
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 107, 53, 0.3);
  background: rgba(255, 255, 255, 0.05);
  color: #e8e8ed;
  min-width: 220px;
  font-size: 0.95rem;
}

.empty-hint { color: #a0a0b0; margin-top: 10px; }

.search-results {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.result-card {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  overflow: hidden;
  border-left: 4px solid rgba(124, 58, 237, 0.6);
}

.result-card img { width: 100%; display: block; }
.result-meta { padding: 14px; color: #c0c0d0; font-size: 0.9rem; line-height: 1.5; }

.preview-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 20px;
}

.preview-toolbar { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.zoom-label { color: #fff; min-width: 60px; text-align: center; }
.preview-content {
  max-width: 90vw;
  max-height: 80vh;
  overflow: auto;
  padding: 10px;
  background: #111;
  border-radius: 8px;
}
.preview-content img { display: block; margin: 0 auto; transition: transform 0.2s; }

@media (max-width: 768px) {
  .nav-bar { padding: 12px 20px; }
  .main-content { padding: 24px 16px; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
}
</style>
