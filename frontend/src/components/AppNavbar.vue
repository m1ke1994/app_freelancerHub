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
        <router-link to="/services" class="link">Исполнители</router-link>
        <router-link to="/create-task" class="link">Разместить задания</router-link>
        <router-link to="/how-it-works" class="link">Как это работает</router-link>

      </nav>

      <!-- ПРАВО -->
      <div class="flex items-center gap-2">
        <router-link to="/login" class="btn ghost hidden sm:inline">Вход</router-link>
        <router-link to="/register" class="btn primary hidden sm:inline">Регистрация</router-link>
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
            <path
              d="M12 3v2M12 19v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M3 12h2M19 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
              stroke-linecap="round" />
            <circle cx="12" cy="12" r="4" />
          </svg>

          <svg v-else xmlns="http://www.w3.org/2000/svg" class="size-5 text-gray-700 dark:text-gray-200"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
          </svg>
        </button>

        <!-- Бургер для мобилки -->
        <button @click="open = true" class="icon-btn sm:hidden" aria-label="Open menu">
          <svg xmlns="http://www.w3.org/2000/svg" class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- MOBILE SHEET -->
    <transition enter-active-class="duration-150 ease-out" leave-active-class="duration-150 ease-in"
      enter-from-class="opacity-0" enter-to-class="opacity-100" leave-from-class="opacity-100"
      leave-to-class="opacity-0">
      <div v-if="open" class="fixed inset-0 z-50 sm:hidden">
        <div class="absolute inset-0 bg-black/30" @click="open = false"></div>

        <aside
          class="absolute inset-y-0 right-0 w-full max-w-xs bg-white dark:bg-gray-900 shadow-xl p-6 flex flex-col gap-6">
          <div class="flex items-center justify-between">
            <router-link to="/" class="flex items-center gap-2 font-bold text-indigo-600 dark:text-indigo-400"
              @click="open = false">
              <img src="/logo.svg" class="h-7 w-7" alt="FreelanceHub" />
              <span>FreelanceHub</span>
            </router-link>
            <button class="icon-btn" @click="open = false" aria-label="Close menu">
              <svg xmlns="http://www.w3.org/2000/svg" class="size-6" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav class="flex flex-col gap-2">
            <router-link to="/tasks" class="nav-item" @click="open = false">Задания</router-link>
            <router-link to="/services" class="nav-item" @click="open = false">Исполнители</router-link>
            <router-link to="/create-task" class="nav-item" @click="open = false">Разместить задание</router-link>
            <router-link to="/how-it-works" class="nav-item" @click="open = false">Как это работает</router-link>
          </nav>

          <div class="mt-auto flex flex-col gap-2">
            <router-link to="/login" class="btn ghost" @click="open = false">Вход</router-link>
            <router-link to="/register" class="btn primary" @click="open = false">Регистрация</router-link>
          </div>
        </aside>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const open = ref(false)
const theme = ref('light')

onMounted(() => {
  theme.value = document.documentElement.classList.contains('dark') ? 'dark' : 'light'
})
function toggleTheme() {
  const root = document.documentElement
  if (theme.value === 'light') { root.classList.add('dark'); theme.value = 'dark' }
  else { root.classList.remove('dark'); theme.value = 'light' }
}
</script>

<style scoped>
.link {
  @apply text-gray-900 dark:text-gray-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition;
}

.btn {
  @apply px-3 py-1.5 text-sm font-medium rounded-md transition;
}

.btn.ghost {
  @apply hover:bg-gray-100 dark:hover:bg-gray-800;
}

.btn.primary {
  @apply bg-indigo-600 text-white hover:bg-indigo-700;
}

.icon-btn {
  @apply p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition;
}

.nav-item {
  @apply px-3 py-2 rounded-md text-base font-semibold text-gray-900 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800;
}

.size-5 {
  width: 1.25rem;
  height: 1.25rem;
}

.size-6 {
  width: 1.5rem;
  height: 1.5rem;
}
</style>
