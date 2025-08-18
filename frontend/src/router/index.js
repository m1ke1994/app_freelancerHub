import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('@/view/HomePage.vue'), meta: { title: 'FreelanceHub — Главная' } },
  { path: '/tasks', name: 'tasks', component: () => import('@/view/TasksPage.vue'), meta: { title: 'Задачи' } },
  { path: '/services', name: 'services', component: () => import('@/view/ServicesPage.vue'), meta: { title: 'Услуги' } },
  { path: '/login', name: 'login', component: () => import('@/view/LoginPage.vue'), meta: { title: 'Вход', guest: true } },
  { path: '/create-task', name: 'create-task', component: () => import('@/view/CreateTasks.vue'), meta: { title: 'Разместить задание', guest: true } },
  { path: '/register', name: 'register', component: () => import('@/view/RegisterPage.vue'), meta: { title: 'Регистрация', guest: true } },
  { path: '/how-it-works', name: 'how-it-works', component: () => import('@/view/HowItWorks.vue'), meta: { title: 'Как это работает', guest: true } },
  { path: '/dashboard/profile', name: 'profile', component: () => import('@/view/FreelancerProfile.vue'), meta: { title: 'Профиль фрилансера' } },
  { path: '/dashboard/customer-profile', name: 'customer-profile', component: () => import('@/view/CustomerProfile.vue'), meta: { title: 'Анкета заказчика' } },
  { path: '/tips-for-freelancers', name: 'tips-for-freelancers', component: () => import('@/view/TipsForFreelancers.vue'), meta: { title: 'Советы фрилансерам', guest: true } },
  // src/router/index.js


]


const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } },
})

router.beforeEach((to) => {
  if (to.meta?.title) document.title = to.meta.title
  return true
})

export default router
