<template>
  <div class="book-detail-container">
    <div class="book-header">
      <div class="breadcrumb-container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>绘本详情</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="user-info">
        <span class="welcome-text">欢迎，{{ username }}</span>
        <el-button type="danger" size="small" @click="logout">
          <el-icon><SwitchButton /></el-icon> 退出登录
        </el-button>
      </div>
    </div>

    <div class="book-title">
      <h1>{{ theme }}</h1>
      <div class="book-actions">
        <el-button type="primary" size="small" @click="downloadPdf" :disabled="!bookData?.has_pdf">
          <el-icon><Download /></el-icon> 下载PDF
        </el-button>
        <el-button type="default" size="small" @click="goBack">
          <el-icon><Back /></el-icon> 返回
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 错误提示 -->
    <el-alert v-if="error" type="error" :title="error" :closable="false" show-icon />

    <!-- 绘本内容 -->
    <div v-if="bookData && !loading" class="book-content">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="metadata-header">
                <span>绘本信息</span>
              </div>
            </template>
            <div class="metadata">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="主题">{{ bookData.metadata.params.theme }}</el-descriptions-item>
                <el-descriptions-item label="风格">{{ bookData.metadata.params.style }}</el-descriptions-item>
                <el-descriptions-item label="页数">{{ bookData.images.length }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 绘本图片展示 -->
      <h2 class="pages-title">绘本页面</h2>
      <el-carousel :interval="5000" height="600px" indicator-position="outside" arrow="always" class="book-carousel">
        <el-carousel-item v-for="(image, index) in bookData.images" :key="index">
          <div class="carousel-content">
            <img :src="getImageUrl(theme, image)" alt="绘本页面" class="carousel-image">
            <div class="page-number">第 {{ index + 1 }} 页</div>
          </div>
        </el-carousel-item>
      </el-carousel>

      <!-- 缩略图展示 -->
      <div class="thumbnails">
        <el-scrollbar>
          <div class="thumbnails-container">
            <div
              v-for="(image, index) in bookData.images"
              :key="index"
              class="thumbnail-item"
              @click="currentPage = index"
            >
              <el-image
                :src="getImageUrl(theme, image)"
                fit="cover"
                lazy
                class="thumbnail-image"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="thumbnail-index">{{ index + 1 }}</div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeMount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getBooksList, getImageUrl, getPdfUrl } from '../api'
import { Download, Back, Picture, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const theme = ref(route.params.theme || '')
const bookData = ref(null)
const loading = ref(true)
const error = ref('')
const currentPage = ref(0)

// 检查登录状态
onBeforeMount(() => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  if (!isLoggedIn || isLoggedIn !== 'true') {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
})

// 获取用户名
const username = ref(localStorage.getItem('username') || '用户')

// 获取绘本数据
const fetchBookData = async () => {
  if (!theme.value) {
    error.value = '绘本主题不能为空'
    loading.value = false
    return
  }

  try {
    loading.value = true

    // 添加加载状态提示
    const loadingInstance = ElMessage({
      type: 'info',
      message: '正在获取绘本数据...',
      duration: 0
    });

    const response = await getBooksList()

    // 关闭加载提示
    loadingInstance.close();

    if (response.data.success) {
      const book = response.data.books.find(b => b.theme === theme.value)

      if (book) {
        bookData.value = book
      } else {
        error.value = '未找到该绘本'
        ElMessage.error('未找到该绘本，可能已被删除')
        setTimeout(() => {
          router.push('/')
        }, 2000)
      }
    } else {
      error.value = '获取绘本数据失败'
      ElMessage.error('获取绘本数据失败，将返回首页')
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  } catch (err) {
    console.error('获取绘本数据错误:', err)
    error.value = '连接服务器失败，请确保后端服务已启动'
    ElMessage.error({
      message: '连接服务器失败，请确保后端服务已启动',
      duration: 5000
    });
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } finally {
    loading.value = false
  }
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 下载PDF
const downloadPdf = () => {
  if (!bookData.value?.has_pdf) {
    ElMessage.warning('PDF文件不可用')
    return
  }

  const pdfUrl = getPdfUrl(theme.value)
  window.open(pdfUrl, '_blank')
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '退出提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('username')
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {
      // 取消退出
    })
}

// 页面加载时获取绘本数据
onMounted(() => {
  fetchBookData()
})
</script>

<style scoped>
.book-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-text {
  font-size: 14px;
  color: #409EFF;
  font-weight: bold;
}

.book-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.book-title h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.book-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px;
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.metadata {
  margin-bottom: 20px;
}

.metadata-header {
  font-weight: bold;
}

.pages-title {
  margin: 30px 0 20px;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.book-carousel {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.carousel-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
}

.carousel-image {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

.page-number {
  position: absolute;
  bottom: 20px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
}

.thumbnails {
  margin-top: 20px;
}

.thumbnails-container {
  display: flex;
  gap: 10px;
  padding: 10px 0;
}

.thumbnail-item {
  position: relative;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.2s;
}

.thumbnail-item:hover {
  transform: translateY(-5px);
}

.thumbnail-image {
  width: 120px;
  height: 90px;
  object-fit: cover;
}

.thumbnail-index {
  position: absolute;
  right: 5px;
  bottom: 5px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
}
</style>