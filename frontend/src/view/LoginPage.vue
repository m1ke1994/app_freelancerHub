<!-- src/view/LoginPage.vue -->
<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/store/userStore"

const router = useRouter()
const userStore = useUserStore()

const email = ref("")
const password = ref("")
const errorMessage = ref("")
const loading = ref(false)

const slides = [
  "FreelanceHub — ваш надёжный путь к быстрым и качественным фриланс-услугам.",
  "Тысячи проверенных специалистов готовы взяться за ваш проект прямо сейчас.",
  "Получите результат быстрее: опишите задачу, выберите исполнителя — и всё готово!",
]
const currentIndex = ref(0)
let interval = null

onMounted(() => {
  interval = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % slides.length
  }, 5000)
})
onUnmounted(() => clearInterval(interval))

async function onLogin() {
  errorMessage.value = ""
  loading.value = true
  try {
    const resp = await fetch("http://localhost:8000/api/accounts/token/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: email.value, password: password.value }),
    })
    const data = await resp.json()

    if (resp.ok && data.access) {
      localStorage.setItem("access", data.access)
      localStorage.setItem("refresh", data.refresh)
      if (typeof userStore.fetchProfile === "function") {
        await userStore.fetchProfile()
      }
      router.push("/profile")
    } else {
      errorMessage.value = data?.detail || "Неверный логин или пароль."
    }
  } catch {
    errorMessage.value = "Ошибка соединения с сервером."
  } finally {
    loading.value = false
  }
}

function onGoogleLogin() {
  alert("Google-авторизация пока не реализована")
}
</script>

<template>
  <!-- Высота = высота вьюпорта, ничего не переливается -->
  <div class="min-h-[100svh] md:min-h-[100dvh] grid grid-cols-1 md:grid-cols-2 overflow-hidden bg-white dark:bg-gray-900">
    <!-- Левая колонка: форма, свой скролл при переполнении -->
    <div class="h-full overflow-y-auto flex items-center justify-center px-4 py-8 md:py-0">
      <div
        class="w-full max-w-[520px] bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800
               rounded-2xl shadow-sm p-6 md:p-8"
      >
        <!-- Назад -->
        <router-link
          :to="{ name: 'home' }"
          class="inline-flex items-center text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition mb-3"
        >
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          На главную
        </router-link>

        <!-- Заголовки -->
        <h1 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Добро пожаловать!</h1>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Войдите в свой аккаунт</p>

        <!-- Ошибка -->
        <div
          v-if="errorMessage"
          class="mt-4 mb-2 rounded-lg bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300 px-3 py-2 text-sm"
        >
          {{ errorMessage }}
        </div>

        <!-- Форма -->
        <form @submit.prevent="onLogin" class="mt-4 space-y-4">
          <div>
            <label class="block text-sm text-gray-700 dark:text-gray-300">E-mail</label>
            <input
              v-model="email"
              type="email"
              required
              autocomplete="username"
              placeholder="you@example.com"
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                     text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <div>
            <label class="block text-sm text-gray-700 dark:text-gray-300">Пароль</label>
            <input
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
              placeholder="••••••••"
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                     text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <div class="flex items-center justify-between">
            <router-link to="/password-reset" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
              Забыли пароль?
            </router-link>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full inline-flex justify-center items-center gap-2 rounded-full bg-indigo-600 text-white
                   py-3 px-4 font-medium hover:bg-indigo-700 disabled:opacity-60 transition"
          >
            <svg v-if="loading" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
            </svg>
            <span v-else>Войти</span>
            <span v-if="loading">Входим…</span>
          </button>
        </form>

        <!-- Разделитель -->
        <div class="my-6 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <div class="h-px flex-1 bg-gray-200 dark:bg-gray-800" />
          ИЛИ
          <div class="h-px flex-1 bg-gray-200 dark:bg-gray-800" />
        </div>

        <!-- Google -->
        <button
          type="button"
          @click="onGoogleLogin"
          class="w-full inline-flex items-center justify-center gap-2 rounded-full border border-gray-300 dark:border-gray-700
                 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 py-3 px-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition"
        >
          <img src="/google-icon.svg" alt="Google" class="w-5 h-5" />
          Войти с Google
        </button>

        <!-- Регистрация -->
        <p class="text-center text-xs mt-6 text-gray-600 dark:text-gray-400">
          Нет аккаунта?
          <router-link to="/register" class="text-indigo-600 dark:text-indigo-400 hover:underline">
            Зарегистрируйтесь бесплатно
          </router-link>
        </p>
      </div>
    </div>

    <!-- Правая колонка: фон + слайдер (только десктоп), высота = контейнер -->
    <div
      class="relative hidden md:block h-full bg-cover bg-center"
      :style="{ backgroundImage: `url('/bg-login1.png')` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600/40 to-indigo-900/40"></div>

      <div
        class="absolute bottom-10 left-1/2 -translate-x-1/2 w-[min(560px,90%)]
               bg-white/90 dark:bg-gray-900/80 backdrop-blur rounded-xl p-4 shadow-lg"
      >
        <p class="text-gray-800 dark:text-gray-100 text-sm transition-all duration-300 min-h-[44px]">
          {{ slides[currentIndex] }}
        </p>
        <div class="flex justify-center mt-3">
          <span
            v-for="(_, i) in slides"
            :key="i"
            class="w-2 h-2 rounded-full mx-1 transition"
            :class="i === currentIndex ? 'bg-indigo-500' : 'bg-indigo-300/60 dark:bg-indigo-200/30'"
          />
        </div>
      </div>
    </div>
  </div>
</template>
