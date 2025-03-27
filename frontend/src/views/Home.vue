<template>
  <div class="home-container">
    <el-card class="header-card">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div class="header-left" style="display: flex; align-items: center;">
          <img src="../assets/images/BNBU_log.png" alt="Logo" class="header-logo">
          <div class="header-text">
            <h1>BNBU-IMS</h1>
            <h1>XQ</h1>
            <h1>基于AIGC的绘本生成器</h1>
            <p>输入创作主题，自动生成精美儿童绘本</p>
          </div>
        </div>
        <div class="user-info">
          <span class="welcome-text">欢迎，{{ username }}</span>
          <el-button type="danger" size="small" @click="logout">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 生成表单 -->
    <el-card class="form-card">
      <el-form :model="form" label-width="120px" @submit.prevent="submitForm">
        <el-form-item label="创作主题" required>
          <el-input v-model="form.theme" placeholder="例如：森林冒险、宇宙探索、海底世界"></el-input>
        </el-form-item>
         <el-form-item label="绘本风格">
          <el-input v-model="form.style" placeholder="请输入或选择绘本风格">
            <template #append>
              <el-select v-model="form.style" placeholder="请选择绘本风格" style="width: auto; min-width: 50%;">
                <el-option v-for="item in styleOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="页数">
          <el-slider v-model="form.page_count" :min="1" :max="6" :step="1" show-stops />
          <div class="page-count-text">{{ form.page_count }} 页</div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="submit-btn">
            生成绘本
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 状态提示 -->
    <el-card v-if="loadingStatus" class="status-card">
      <el-alert type="info" :closable="false">
        <template #title>
          <div class="status-info">
            <el-icon class="status-icon"><Loading /></el-icon>
            <span>{{ loadingStatus }}</span>
          </div>
        </template>
      </el-alert>
    </el-card>

    <!-- 绘本列表 -->
    <div class="books-section" v-if="books.length > 0">
      <h2>已生成的绘本</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="book in books" :key="book.theme">
          <el-card class="book-card" shadow="hover">
            <template #header>
              <div class="book-header">
                <span>{{ book.theme }}</span>
                <div class="book-actions">
                  <el-button
                    type="danger"
                    size="small"
                    circle
                    @click.stop="confirmDelete(book)"
                    title="删除绘本"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                  <el-button
                    type="primary"
                    size="small"
                    circle
                    @click.stop="regenerateBook(book)"
                    title="重新生成"
                    :loading="book.regenerating"
                  >
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
            <div class="book-cover" @click="viewBook(book)">
              <img :src="getImageUrl(book.theme, book.images[0])" alt="封面">
            </div>
            <div class="book-info">
              <div>风格：{{ book.metadata.params.style }}</div>
              <div>页数：{{ book.images.length }}</div>
              <el-tag v-if="book.has_pdf" type="success" size="small">PDF可下载</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除绘本"{{ bookToDelete?.theme }}"吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteBook" :loading="deleting">确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, Delete, Refresh, SwitchButton } from '@element-plus/icons-vue'
import { generateBook, getBooksList, getImageUrl, deleteBook as apiDeleteBook } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const loadingStatus = ref('')
const books = ref([])
const deleteDialogVisible = ref(false)
const bookToDelete = ref(null)
const deleting = ref(false)
const username = ref('用户')

// 检查登录状态
onBeforeMount(() => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  if (!isLoggedIn || isLoggedIn !== 'true') {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 获取用户名
  const storedUsername = localStorage.getItem('username')
  if (storedUsername) {
    username.value = storedUsername
  }
})

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

const form = ref({
  theme: '',
  style: '水彩',
  page_count: 3
})

const styleOptions = [
  { value: '水彩', label: '水彩风格' },
  { value: '卡通', label: '卡通风格' },
  { value: '油画', label: '油画风格' },
  { value: '素描', label: '素描风格' },
  { value: '赛博朋克', label: '赛博朋克' }
]

// 表单提交
const submitForm = async () => {
  if (!form.value.theme) {
    ElMessage.warning('请输入创作主题')
    return
  }

  try {
    loading.value = true
    loadingStatus.value = '正在生成故事内容...'

    const response = await generateBook(form.value)

    if (response.data.success) {
      ElMessage.success('绘本生成成功！')
      loadBooksList()
      router.push(`/book/${form.value.theme}`)
    } else {
      ElMessage.error(response.data.message || '生成失败')
    }
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('绘本生成失败，请重试')
  } finally {
    loading.value = false
    loadingStatus.value = ''
  }
}

// 获取绘本列表
const loadBooksList = async () => {
  try {
    const response = await getBooksList()
    if (response.data.success) {
      // 为每本书添加regenerating标记
      books.value = response.data.books.map(book => ({
        ...book,
        regenerating: false
      }))
    }
  } catch (error) {
    console.error('获取绘本列表失败:', error)
  }
}

// 查看绘本详情
const viewBook = (book) => {
  router.push(`/book/${book.theme}`)
}

// 确认删除对话框
const confirmDelete = (book) => {
  bookToDelete.value = book
  deleteDialogVisible.value = true
}

// 删除绘本
const deleteBook = async () => {
  if (!bookToDelete.value) return

  try {
    deleting.value = true
    const response = await apiDeleteBook(bookToDelete.value.theme)

    if (response.data.success) {
      ElMessage.success('绘本已删除')
      // 从列表中移除
      books.value = books.value.filter(b => b.theme !== bookToDelete.value.theme)
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除绘本失败，请重试')
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
    bookToDelete.value = null
  }
}

// 重新生成绘本
const regenerateBook = async (book) => {
  try {
    // 确认是否重新生成
    await ElMessageBox.confirm(
      `确定要重新生成绘本"${book.theme}"吗？`,
      '确认重新生成',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 设置对应书籍的regenerating状态为true
    const bookIndex = books.value.findIndex(b => b.theme === book.theme)
    if (bookIndex !== -1) {
      books.value[bookIndex].regenerating = true
    }

    // 使用原有参数重新生成
    const params = {
      theme: book.metadata.params.theme,
      style: book.metadata.params.style,
      page_count: book.metadata.params.page_count
    }

    const response = await generateBook(params)

    if (response.data.success) {
      ElMessage.success('绘本重新生成成功！')
      loadBooksList() // 重新加载列表
      router.push(`/book/${book.theme}`)
    } else {
      ElMessage.error(response.data.message || '重新生成失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新生成失败:', error)
      ElMessage.error('重新生成绘本失败，请重试')
    }
  } finally {
    // 重置所有书籍的regenerating状态
    books.value = books.value.map(b => ({
      ...b,
      regenerating: false
    }))
  }
}

// 页面加载时获取绘本列表
onMounted(() => {
  loadBooksList()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
  background-color: #f0f9ff;
  display: flex;
  justify-content: center;
  align-items: center;
}
.header-logo {
  width: 100px;
  height: 100px;
  margin-right: 100px;
}

.header-text {
  text-align: left;
}

.header-text h1 {
  color: #409EFF;
  margin-bottom: 10px;
}


.header-card h1 {
  color: #409EFF;
  margin-bottom: 10px;
}

.form-card {
  margin-bottom: 20px;
}

.status-card {
  margin-bottom: 20px;
}

.status-info {
  display: flex;
  align-items: center;
}

.status-icon {
  margin-right: 8px;
  animation: spin 1s linear infinite;
}

.w-100 {
  width: 100%;
}

.submit-btn {
  width: 100%;
}

.page-count-text {
  text-align: center;
  margin-top: 5px;
  color: #606266;
}

.books-section {
  margin-top: 30px;
}

.books-section h2 {
  margin-bottom: 20px;
  color: #303133;
  font-weight: 500;
}

.book-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-header span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: bold;
}

.book-actions {
  display: flex;
  gap: 8px;
}

.book-cover {
  height: 180px;
  overflow: hidden;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  cursor: pointer;
}

.book-cover img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.book-info {
  font-size: 14px;
  color: #606266;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 添加用户信息样式 */
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
</style>
