<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <a href="https://www.uic.edu.cn" target="_blank">
          <img src="../assets/images/BNBU_log.png" alt="BNBU Logo" class="login-logo">
        </a>
        <h2 class="login-title">基于AIGC的绘本生成器</h2>
      </div>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="login-tabs">
        <el-tab-pane label="扫码登录" name="qrCode">
          <div class="qr-container">
            <qrcode-vue :value="qrCodeValue" :size="200" level="L"></qrcode-vue>
            <p class="qr-tip">请使用手机扫描二维码登录</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="账号密码登录" name="password">
          <el-form :model="form" status-icon :rules="rules" ref="ruleFormRef" class="login-form">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" autocomplete="off" placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input type="password" v-model="form.password" autocomplete="off" placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-form-item class="form-buttons">
              <el-button type="primary" @click="submitForm(ruleFormRef)" class="submit-btn">登录</el-button>
              <el-button @click="resetForm(ruleFormRef)">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import QrcodeVue from 'qrcode.vue' // 引入二维码生成库
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('password')
const qrCodeValue = ref('https://www.uic.edu.cn') // 示例二维码链接

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const ruleFormRef = ref()

const handleTabClick = (tab) => {}


const submitForm = async (formEl) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      // 这里可以添加账号密码验证逻辑
      // const envUsername = "xq"
      const envUsername = ["xq","fukun","admin","lyy","syy"]
      const envPassword = "123123"
      if (envUsername.includes(form.username) && form.password === envPassword) {
        ElMessage.success('登录成功')
        localStorage.setItem('isLoggedIn', 'true') // 设置登录状态
        localStorage.setItem('username', form.username) // 保存用户名
        router.push('/') // 重定向到主页
      } else {
        ElMessage.error('用户名或密码错误')
      }
    } else {
      console.log('error submit!', valid)
    }
  })
}

const resetForm = (formEl) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 450px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.login-logo {
  width: 120px;
  margin-bottom: 15px;
}

.login-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
  text-align: center;
}

.login-tabs {
  margin-top: 20px;
}

.login-form {
  padding: 10px;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.qr-tip {
  margin-top: 15px;
  color: #909399;
  font-size: 14px;
}

.form-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.submit-btn {
  width: 45%;
}

:deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
}

:deep(.el-tabs__item) {
  flex: 1;
  text-align: center;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
