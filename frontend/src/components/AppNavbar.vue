<!-- components/AppHeader.vue -->
<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { toggleTheme as toggleThemeUtil } from '@/utils/theme'

const router = useRouter()
const userStore = useUserStore()

const open = ref(false)
const theme = ref(document.documentElement.classList.contains('dark') ? 'dark' : 'light')

/* Авторизация */
const isAuth = computed(() => Boolean(userStore.access && userStore.user))
const fullName = computed(() => userStore.fullName)
const userEmail = computed(() => userStore.user?.email || '')
const isExecutor = computed(() => userStore.user?.role === 'executor')
const isCustomer = computed(() => userStore.user?.role === 'customer')
const roleChip = computed(() => (isExecutor.value ? 'Я исполнитель' : isCustomer.value ? 'Я заказчик' : ''))

/* Аватар */
const avatarUrl = computed(() => userStore.user?.avatar_url?.trim() || '')
const hasAvatar = computed(() => Boolean(avatarUrl.value))

/* Профильный роут */
const profileRoute = computed(() =>
  isExecutor.value ? '/dashboard/profile' : '/dashboard/customer-profile'
)

/* Показывать ссылки */
const showCustomerLinks = computed(() => !isAuth.value || isCustomer.value)

/* Автоподгрузка профиля */
watchEffect(async () => {
  if (userStore.access && !userStore.user && !userStore.loading) {
    try { await userStore.fetchProfile() } catch {}
  }
})

function onLogout() {
  userStore.logout()
  router.push('/')
}
function handleLogoutMobile() {
  onLogout()
  open.value = false
}
function closeSheet() {
  open.value = false
}
function toggleTheme() {
  theme.value = toggleThemeUtil()
}
</script>

<template>
  <header class="border-b bg-white dark:bg-gray-900 dark:border-gray-800">
    <div class="mx-auto max-w-7xl h-14 px-4 flex items-center justify-between">
      <!-- ЛОГО -->
      <router-link to="/" class="flex items-center gap-2 font-bold text-indigo-600 dark:text-indigo-400">
        <img src="/logo.svg" alt="FreelanceHub" class="h-7 w-7" />
        <span class="sm:hidden">FH</span>
        <span class="hidden sm:inline">FreelanceHub</span>
      </router-link>

      <!-- ЦЕНТР (десктоп) -->
      <nav class="hidden sm:flex gap-6 text-sm font-medium">
        <router-link to="/tasks" class="link">Задания</router-link>
        <router-link v-if="showCustomerLinks" to="/services" class="link">Исполнители</router-link>
        <router-link v-if="showCustomerLinks" to="/create-task" class="link">Разместить задание</router-link>
        <router-link to="/how-it-works" class="link">Как это работает</router-link>
      </nav>

      <!-- ПРАВО -->
      <div class="flex items-center gap-2">
        <!-- Гость -->
        <template v-if="!isAuth">
          <router-link to="/login" class="btn ghost hidden sm:inline">Вход</router-link>
          <router-link to="/register" class="btn primary hidden sm:inline">Регистрация</router-link>
        </template>

        <!-- Авторизован -->
        <template v-else>
          <div class="hidden sm:flex items-center gap-3 pr-2">
            <div class="text-right leading-4">
              <div class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {{ fullName || userEmail }}
              </div>
              <div v-if="roleChip"
                   class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                          bg-orange-100 text-orange-700 dark:bg-orange-400/20 dark:text-orange-300 mt-0.5">
                {{ roleChip }}
              </div>
            </div>

            <!-- Аватар только если есть -->
            <router-link v-if="hasAvatar" :to="profileRoute" class="shrink-0">
              <img
                :src="avatarUrl"
                alt="Avatar"
                class="w-9 h-9 rounded-full object-cover"
              />
            </router-link>

            <!-- Выйти -->
            <button @click="onLogout" class="btn ghost">Выйти</button>
          </div>
        </template>

        <!-- ИКОНКИ (мобилка) -->
        <ul class="flex gap-2 sm:flex md:flex lg:hidden">
          <li><img src="/Chat.svg" alt="Чат" class="w-5 h-5 hover:scale-105 transition-all duration-300 cursor-pointer" /></li>
          <li><img src="/Favorite.svg" alt="Избранное" class="w-5 h-5 hover:scale-105 transition-all duration-300 cursor-pointer" /></li>
          <li><img src="/Notification.svg" alt="Уведомления" class="w-5 h-5 hover:scale-105 transition-all duration-300 cursor-pointer" /></li>
        </ul>

        <!-- Переключатель темы -->
        <button @click="toggleTheme" class="icon-btn" aria-label="Toggle theme">
          <svg v-if="theme === 'light'" xmlns="http://www.w3.org/2000/svg"
               class="size-5 text-gray-700 dark:text-gray-200" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="1.5">
            <path d="M12 3v2M12 19v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M3 12h2M19 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" stroke-linecap="round"/>
            <circle cx="12" cy="12" r="4" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="size-5 text-gray-700 dark:text-gray-200"
               viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
          </svg>
        </button>

        <!-- Бургер (мобилка) -->
        <button @click="open = true" class="icon-btn sm:hidden" aria-label="Open menu">
          <svg xmlns="http://www.w3.org/2000/svg" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- MOBILE SHEET -->
    <transition enter-active-class="duration-150 ease-out" leave-active-class="duration-150 ease-in"
               enter-from-class="opacity-0" enter-to-class="opacity-100"
               leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 sm:hidden">
        <div class="absolute inset-0 bg-black/30" @click="open = false"></div>

        <aside class="absolute inset-y-0 right-0 w-full max-w-xs bg-white dark:bg-gray-900 shadow-xl p-6 flex flex-col gap-6">
          <div class="flex items-center justify-between">
            <router-link to="/" class="flex items-center gap-2 font-bold text-indigo-600 dark:text-indigo-400" @click="closeSheet">
              <img src="/logo.svg" class="h-7 w-7" alt="FreelanceHub" />
              <span>FreelanceHub</span>
            </router-link>
            <button class="icon-btn" @click="closeSheet" aria-label="Close menu">
              <svg xmlns="http://www.w3.org/2000/svg" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Карточка пользователя -->
          <div v-if="isAuth" class="flex items-center gap-3">
            <img
              v-if="hasAvatar"
              :src="avatarUrl"
              alt="Avatar"
              class="w-12 h-12 rounded-full object-cover"
            />
            <div class="min-w-0">
              <div class="text-base font-semibold text-gray-900 dark:text-gray-100 truncate">
                {{ fullName || userEmail }}
              </div>
              <div v-if="roleChip"
                   class="inline-flex items-center mt-1 px-2 py-0.5 rounded-full text-xs font-medium
                          bg-orange-100 text-orange-700 dark:bg-orange-400/20 dark:text-orange-300">
                {{ roleChip }}
              </div>
            </div>
          </div>

          <!-- Меню -->
          <nav class="flex flex-col gap-2">
            <template v-if="isAuth && isExecutor">
              <router-link to="/tasks" class="nav-item" @click="closeSheet">Лента заданий</router-link>
              <router-link :to="profileRoute" class="nav-item" @click="closeSheet">Мой кабинет</router-link>
              <router-link to="/dashboard/orders" class="nav-item" @click="closeSheet">Мои заказы</router-link>
              <router-link to="/dashboard/settings" class="nav-item" @click="closeSheet">Мои настройки</router-link>
            </template>

            <template v-else-if="isAuth && isCustomer">
              <router-link to="/tasks" class="nav-item" @click="closeSheet">Задания</router-link>
              <router-link to="/services" class="nav-item" @click="closeSheet">Исполнители</router-link>
              <router-link to="/create-task" class="nav-item" @click="closeSheet">Разместить задание</router-link>
              <router-link :to="profileRoute" class="nav-item" @click="closeSheet">Мой кабинет</router-link>
            </template>

            <template v-else>
              <router-link to="/tasks" class="nav-item" @click="closeSheet">Задания</router-link>
              <router-link to="/services" class="nav-item" @click="closeSheet">Исполнители</router-link>
              <router-link to="/create-task" class="nav-item" @click="closeSheet">Разместить задание</router-link>
              <router-link to="/how-it-works" class="nav-item" @click="closeSheet">Как это работает</router-link>
            </template>
          </nav>

          <div class="mt-auto flex flex-col gap-2">
            <template v-if="!isAuth">
              <router-link to="/login" class="btn ghost" @click="closeSheet">Вход</router-link>
              <router-link to="/register" class="btn primary" @click="closeSheet">Регистрация</router-link>
            </template>
            <template v-else>
              <button class="btn ghost text-red-600 hover:text-red-700" @click="handleLogoutMobile">
                Выйти из аккаунта
              </button>
            </template>
          </div>
        </aside>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.link { @apply text-gray-900 dark:text-gray-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition; }
.btn { @apply px-3 py-1.5 text-sm font-medium rounded-md transition; }
.btn.ghost { @apply hover:bg-gray-100 dark:hover:bg-gray-800; }
.btn.primary { @apply bg-indigo-600 text-white hover:bg-indigo-700; }
.icon-btn { @apply p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition; }
.nav-item { @apply px-3 py-2 rounded-md text-base font-semibold text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800; }
.size-5 { width: 1.25rem; height: 1.25rem; }
.size-6 { width: 1.5rem; height: 1.5rem; }
</style>
