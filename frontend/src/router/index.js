// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/userStore'

const routes = [
  { path: '/', name: 'home', component: () => import('@/view/HomePage.vue'), meta: { title: 'FreelanceHub — Главная', guest: true } },
  { path: '/tasks', name: 'tasks', component: () => import('@/view/TasksPage.vue'), meta: { title: 'Задачи', guest: true } },
  { path: '/services', name: 'services', component: () => import('@/view/ServicesPage.vue'), meta: { title: 'Услуги', guest: true } },
  { path: '/login', name: 'login', component: () => import('@/view/LoginPage.vue'), meta: { title: 'Вход', guest: true } },
  { path: '/create-task', name: 'create-task', component: () => import('@/view/CreateTasks.vue'), meta: { title: 'Разместить задание', guest: true } },
  { path: '/register', name: 'register', component: () => import('@/view/RegisterPage.vue'), meta: { title: 'Регистрация', guest: true } },
  { path: '/how-it-works', name: 'how-it-works', component: () => import('@/view/HowItWorks.vue'), meta: { title: 'Как это работает', guest: true } },
{ path: '/jobs/:id', name: 'JobDetails', component: () => import('@/view/TaskDetails.vue') },
  // приватные
  { path: '/dashboard/profile', name: 'profile', component: () => import('@/view/FreelancerProfile.vue'), meta: { title: 'Профиль фрилансера', auth: true } },
  { path: '/dashboard/customer-profile', name: 'customer-profile', component: () => import('@/view/CustomerProfile.vue'), meta: { title: 'Анкета заказчика', auth: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/view/NotFound.vue'), meta: { title: 'Страница не найдена', guest: true } },
    { path: '/dashboard/my-tasks', name: 'MyAsignments', component: () => import('@/view/Customer/MyAsignments.vue'), meta: { title: 'мои задания', auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  if (to.meta?.title) document.title = to.meta.title
  const userStore = useUserStore()

  // публичные — всегда ок
  if (!to.meta?.auth) return true

  // ЕСЛИ токен уже есть — пускаем сразу, профиль дотянем в фоне
  if (userStore.access) {
    if (!userStore.user && !userStore.loading) {
      // не блокируем переход — просто запускаем загрузку
      userStore.fetchProfile().catch(() => userStore.reset?.())
    }
    return true
  }

  // токена нет — на логин
  return { name: 'login', query: { next: to.fullPath } }
})

export default router
