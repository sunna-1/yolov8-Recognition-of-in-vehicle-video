<template>
  <div class="home-page" ref="homeRef">
    <header class="home-header">
      <nav class="nav-bar">
        <router-link to="/" class="nav-logo">动态路况分析系统</router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">项目介绍</router-link>
          <router-link to="/analysis" class="nav-link" exact-active-class="active">开始分析</router-link>
        </div>
      </nav>
    </header>

    <main class="home-main">
      <section class="hero" ref="heroRef">
        <h1 class="hero-title">智能交通路况分析平台</h1>
        <p class="hero-subtitle">基于 YOLOv8 与 Vue3 的动态路况识别与数据分析系统</p>
        <router-link to="/analysis" class="hero-cta">进入分析</router-link>
      </section>

      <section class="section section-tech" ref="techRef">
        <h2 class="section-title">技术架构</h2>
        <div class="tech-grid">
          <div class="tech-card" v-for="(item, i) in techItems" :key="i" :data-index="i">
            <h3 class="tech-name">{{ item.name }}</h3>
            <p class="tech-desc">{{ item.desc }}</p>
          </div>
        </div>
      </section>

      <section class="section section-purpose" ref="purposeRef">
        <h2 class="section-title">项目作用</h2>
        <p class="purpose-text">对视频或实时摄像头画面中的车辆、行人、交通标识进行高精度检测与统计，输出密度趋势、类别分布、代表性帧等可视化结果，为交通分析、路况评估提供数据支持。</p>
      </section>

      <section class="section section-steps" ref="stepsRef">
        <h2 class="section-title">使用步骤</h2>
        <div class="steps-list">
          <div class="step-item" v-for="(step, i) in steps" :key="i" :data-index="i">
            <span class="step-num">{{ i + 1 }}</span>
            <p class="step-text">{{ step }}</p>
          </div>
        </div>
        <router-link to="/analysis" class="steps-cta">开始使用</router-link>
      </section>
    </main>

    <footer class="home-footer">
      <p>动态路况分析系统</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default {
  name: 'HomePage',
  setup() {
    const homeRef = ref(null)
    const heroRef = ref(null)
    const techRef = ref(null)
    const purposeRef = ref(null)
    const stepsRef = ref(null)

    const techItems = [
      { name: 'YOLOv8', desc: 'Ultralytics 目标检测模型，识别车辆、行人、交通设施等' },
      { name: 'Flask', desc: 'Python Web 框架，提供 RESTful API 与视频处理' },
      { name: 'Vue 3', desc: '组合式 API 前端框架，构建交互界面' },
      { name: 'ECharts', desc: '数据可视化图表，展示类别分布与密度趋势' },
      { name: 'OpenCV', desc: '视频读取、图像处理与标注绘制' },
      { name: 'GSAP', desc: '流畅动效与滚动触发交互' }
    ]

    const steps = [
      '打开前端应用并进入分析页面',
      '选择本地视频文件或启用摄像头进行实时检测',
      '点击「开始分析」并等待处理完成',
      '查看分析结果：统计卡片、代表性帧、类别分布与密度趋势'
    ]

    onMounted(() => {
      if (!heroRef.value) return

      gsap.from(heroRef.value, {
        opacity: 0,
        y: 60,
        duration: 1,
        ease: 'power3.out'
      })

      gsap.from('.tech-card', {
        scrollTrigger: {
          trigger: techRef.value,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        },
        opacity: 0,
        y: 50,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power2.out'
      })

      gsap.from(purposeRef.value, {
        scrollTrigger: {
          trigger: purposeRef.value,
          start: 'top 85%',
          toggleActions: 'play none none reverse'
        },
        opacity: 0,
        y: 40,
        duration: 0.9,
        ease: 'power2.out'
      })

      gsap.from('.step-item', {
        scrollTrigger: {
          trigger: stepsRef.value,
          start: 'top 80%',
          toggleActions: 'play none none reverse'
        },
        opacity: 0,
        x: -40,
        stagger: 0.12,
        duration: 0.7,
        ease: 'power2.out'
      })
    })

    return {
      homeRef,
      heroRef,
      techRef,
      purposeRef,
      stepsRef,
      techItems,
      steps
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #0a0a0f;
  color: #e8e8ed;
}

.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(10, 10, 15, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 107, 53, 0.2);
}

.nav-logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ff6b35;
  text-decoration: none;
  letter-spacing: 0.02em;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: #a0a0b0;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.25s;
}

.nav-link:hover,
.nav-link.active {
  color: #ff6b35;
}

.home-main {
  padding-top: 80px;
}

.hero {
  min-height: 85vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 60px 24px;
  background: radial-gradient(ellipse 80% 50% at 50% 20%, rgba(255, 107, 53, 0.12) 0%, transparent 50%);
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #ff6b35 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #a0a0b0;
  max-width: 560px;
  margin-bottom: 48px;
  line-height: 1.6;
}

.hero-cta {
  display: inline-block;
  padding: 16px 40px;
  background: #ff6b35;
  color: #0a0a0f;
  font-weight: 700;
  text-decoration: none;
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.hero-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
}

.section {
  max-width: 1000px;
  margin: 0 auto;
  padding: 100px 40px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 48px;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.tech-card {
  padding: 28px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 107, 53, 0.2);
  border-radius: 12px;
  transition: border-color 0.25s, transform 0.25s;
}

.tech-card:hover {
  border-color: rgba(255, 107, 53, 0.5);
  transform: translateY(-4px);
}

.tech-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ff6b35;
  margin-bottom: 12px;
}

.tech-desc {
  color: #a0a0b0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.purpose-text {
  font-size: 1.15rem;
  line-height: 1.8;
  color: #c0c0d0;
}

.section-purpose {
  border-top: 1px solid rgba(255, 107, 53, 0.15);
}

.steps-list {
  margin-bottom: 40px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.step-num {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ff6b35;
  color: #0a0a0f;
  font-weight: 700;
  border-radius: 8px;
}

.step-text {
  color: #c0c0d0;
  font-size: 1.05rem;
  line-height: 1.6;
}

.steps-cta {
  display: inline-block;
  padding: 14px 32px;
  border: 2px solid #ff6b35;
  color: #ff6b35;
  font-weight: 600;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.25s, color 0.25s;
}

.steps-cta:hover {
  background: #ff6b35;
  color: #0a0a0f;
}

.home-footer {
  padding: 40px;
  text-align: center;
  color: #606070;
  font-size: 0.9rem;
  border-top: 1px solid rgba(255, 107, 53, 0.15);
}

@media (max-width: 768px) {
  .nav-bar {
    padding: 16px 20px;
  }

  .section {
    padding: 60px 24px;
  }

  .tech-grid {
    grid-template-columns: 1fr;
  }
}
</style>
