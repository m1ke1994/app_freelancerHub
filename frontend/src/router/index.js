// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/userStore'

const routes = [
  // Публичные
  { path: '/', name: 'home', component: () => import('@/view/HomePage.vue'), meta: { title: 'FreelanceHub — Главная' } },
  { path: '/tasks', name: 'tasks', component: () => import('@/view/TasksPage.vue'), meta: { title: 'Задачи' } },
  // Доступно гостю и заказчику (исполнителю запрещаем в навигационном гардe)
  { path: '/services', name: 'services', component: () => import('@/view/ServicesPage.vue'), meta: { title: 'Исполнители', allowExecutor: false } },
  { path: '/create-task', name: 'create-task', component: () => import('@/view/CreateTasks.vue'), meta: { title: 'Разместить задание', allowExecutor: false } },
  { path: '/how-it-works', name: 'how-it-works', component: () => import('@/view/HowItWorks.vue'), meta: { title: 'Как это работает' } },
  { path: '/tips-for-freelancers', name: 'tips-for-freelancers', component: () => import('@/view/TipsForFreelancers.vue'), meta: { title: 'Советы фрилансерам' } },

  // Аутентификация (гостевые страницы)
  { path: '/login', name: 'login', component: () => import('@/view/LoginPage.vue'), meta: { title: 'Вход', guestOnly: true } },
  { path: '/register', name: 'register', component: () => import('@/view/RegisterPage.vue'), meta: { title: 'Регистрация', guestOnly: true } },

  // Кабинеты (только авторизованные, разделяем по ролям)
  { path: '/dashboard/profile', name: 'profile', component: () => import('@/view/FreelancerProfile.vue'), meta: { title: 'Профиль фрилансера', requiresAuth: true, onlyRole: 'executor' } },
  { path: '/dashboard/customer-profile', name: 'customer-profile', component: () => import('@/view/CustomerProfile.vue'), meta: { title: 'Анкета заказчика', requiresAuth: true, onlyRole: 'customer' } },

  // 404
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/view/NotFound.vue'), meta: { title: 'Страница не найдена' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  // Заголовок страницы
  if (to.meta?.title) document.title = to.meta.title

  const store = useUserStore()

  // Если есть токен, но ещё не подгружен профиль — подгрузим (чтобы гварды знали роль)
  if (store.access && !store.user && !store.loading) {
    try { await store.fetchProfile() } catch (e) { /* ignore */ }
  }

  const isAuth = store.isAuth
  const role = store.user?.role

  // 1) Гостевые страницы: если авторизован — редирект в свой кабинет
  if (to.meta?.guestOnly && isAuth) {
    return role === 'executor' ? { name: 'profile' } : { name: 'customer-profile' }
  }

  // 2) Приватные страницы: требуется авторизация
  if (to.meta?.requiresAuth && !isAuth) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 3) Ролевые ограничения
  if (to.meta?.onlyRole && isAuth && role !== to.meta.onlyRole) {
    // Если роль не совпала — отправим в корректный кабинет
    return role === 'executor' ? { name: 'profile' } : { name: 'customer-profile' }
  }

  // 4) Запрет для исполнителя на некоторые публичные страницы
  //    (гостям и заказчикам можно)
  if (typeof to.meta?.allowExecutor === 'boolean') {
    if (isAuth && role === 'executor' && to.meta.allowExecutor === false) {
      // отправляем исполнителя в его кабинет
      return { name: 'profile' }
    }
  }

  return true
})

export default router
