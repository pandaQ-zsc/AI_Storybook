<template>
  <div class="app-container">
    <el-config-provider :locale="zhCn">
      <router-view v-if="isLoggedIn" />
      <Login v-else />
    </el-config-provider>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import Login from './views/Login.vue' // 导入登录组件

const router = useRouter()
const isLoggedIn = ref(false)

onMounted(() => {
  // 检查用户是否已登录（这里只是一个示例，实际应根据实际情况判断）
  const storedIsLoggedIn = localStorage.getItem('isLoggedIn')
  if (storedIsLoggedIn === 'true') {
    isLoggedIn.value = true
  } else {
    router.push('/login')
  }
})

// 登录成功后的回调函数
const loginSuccess = () => {
  isLoggedIn.value = true
  router.push('/')
}
</script>

<style scoped>
.app-container {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

body {
  margin: 0;
  padding: 0;
  background-color: #f5f7fa;
}
</style>
