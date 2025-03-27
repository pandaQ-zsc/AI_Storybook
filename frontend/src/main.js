import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = '/'

const app = createApp(App)

// 注册全局组件和插件
app.use(ElementPlus)
app.use(router)

// 挂载应用
app.mount('#app')