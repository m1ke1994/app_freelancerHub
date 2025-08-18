// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/tailwind.css'
import { getInitialTheme, applyTheme, watchSystemTheme } from '@/utils/theme'

// 1) Тема: применяем до монтирования (без мигания)
const initialTheme = getInitialTheme()
applyTheme(initialTheme)
watchSystemTheme() // убери, если не нужно реагировать на системную смену

// 2) Создаём приложение и подключаем плагины
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// 3) Инициализируем пользователя (если есть токены)
import { useUserStore } from '@/store/userStore'
const userStore = useUserStore()
userStore.init?.() // подтянет профиль при наличии access

// 4) Дождёмся готовности роутера и монтируем
router.isReady().then(() => {
  app.mount('#app')
})

// 5) Глобальная обработка ошибок (только в DEV)
app.config.errorHandler = (err) => {
  if (import.meta.env.DEV) {
    console.error('[Vue error]', err)
  }
}
