import axios from 'axios'

/**
 * 生成新绘本
 * @param {Object} params 生成参数
 * @returns {Promise}
 */
export function generateBook(params) {
  return axios.post('/api/generate', params)
}

/**
 * 获取所有绘本列表
 * @returns {Promise}
 */
export function getBooksList() {
  return axios.get('/api/books')
}

/**
 * 获取图片URL
 * @param {string} theme 绘本主题
 * @param {string} filename 图片文件名
 * @returns {string} 图片URL
 */
export function getImageUrl(theme, filename) {
  return `/api/books/${encodeURIComponent(theme)}/images/${encodeURIComponent(filename)}`
}

/**
 * 获取PDF下载链接
 * @param {string} theme 绘本主题
 * @returns {string} PDF链接
 */
export function getPdfUrl(theme) {
  return `/api/books/${encodeURIComponent(theme)}/pdf`
}