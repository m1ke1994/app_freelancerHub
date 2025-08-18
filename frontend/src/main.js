// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/tailwind.css'

// 1) создаём приложение и подключаем плагины
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 2) восстанавливаем тему до mount (чтобы не мигало)
const savedTheme = localStorage.getItem('theme') // 'dark' | 'light'
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
const theme = savedTheme || (prefersDark ? 'dark' : 'light')
document.documentElement.classList.toggle('dark', theme === 'dark')

// 3) инициализируем пользователя (если есть токены) — из твоего userStore
import { useUserStore } from '@/store/userStore'
const userStore = useUserStore()
userStore.init?.() // подтянет профиль при наличии access

// 4) дождёмся готовности роутера (корректная начальная навигация)
router.isReady().then(() => {
  app.mount('#app')
}).catch(() => {
  // на крайний случай монтируем всё равно
  app.mount('#app')
})

// 5) (опционально) глобальная обработка ошибок
app.config.errorHandler = (err) => {
  if (import.meta.env.DEV) {
    console.error('[Vue error]', err)
  }
}
