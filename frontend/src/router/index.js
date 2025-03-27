// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import BookDetail from '../views/BookDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true } // 添加requiresAuth元信息
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/book/:theme',
    name: 'BookDetail',
    component: () => import('../views/BookDetail.vue'),
    props: true,
    meta: { requiresAuth: true } // 添加requiresAuth元信息
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !isLoggedIn) {
    next('/login'); // 如果需要认证但未登录，则重定向到登录页面
  } else {
    next(); // 否则继续导航
  }
});

export default router
