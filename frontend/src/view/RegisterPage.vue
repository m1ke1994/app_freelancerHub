<!-- components/RegisterForm.vue -->
<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/store/userStore"

const router = useRouter()
const userStore = useUserStore()

const firstName = ref("")
const lastName  = ref("")
const email     = ref("")
const phone     = ref("+7 ")
const phoneRaw  = ref("+7")
const password  = ref("")
const confirm   = ref("")
const role      = ref("executor")

const errorMessage = ref("")
const successMessage = ref("")
const loading = ref(false)

const slides = [
  "FreelanceHub — это маркетплейс фриланс-услуг, где можно купить услугу как товар в магазине или создать индивидуальный заказ на бирже.",
  "Тысячи проверенных специалистов готовы взяться за ваш проект прямо сейчас.",
  "Получите результат быстрее: опишите задачу, выберите исполнителя — и всё готово!"
]
const currentIndex = ref(0)
let interval = null

onMounted(() => {
  interval = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % slides.length
  }, 5000)
})
onUnmounted(() => clearInterval(interval))

function prettify(raw) {
  const d = raw.slice(2)
  const p = [ d.slice(0,3), d.slice(3,6), d.slice(6,8), d.slice(8,10) ].filter(Boolean)
  return "+7" +
    (p[0] ? " " + p[0] : "") +
    (p[1] ? " " + p[1] : "") +
    (p[2] ? "-" + p[2] : "") +
    (p[3] ? "-" + p[3] : "")
}

function onPhoneInput(e) {
  let raw = e.target.value.replace(/[^\d+]/g, "")
  if (!raw.startsWith("+")) raw = "+" + raw
  if (!raw.startsWith("+7")) raw = "+7" + raw.replace(/^\+?\d*/, "")
  raw = raw.slice(0, 12)
  phoneRaw.value = raw
  phone.value = prettify(raw)
}

const isPasswordMismatch = computed(() => confirm.value && password.value !== confirm.value)

async function onRegister() {
  errorMessage.value = ""
  successMessage.value = ""

  if (isPasswordMismatch.value) {
    errorMessage.value = "Пароли не совпадают"
    return
  }

  loading.value = true
  const payload = {
    first_name: firstName.value,
    last_name: lastName.value,
    email: email.value,
    phone: phoneRaw.value,
    password: password.value,
    confirm: confirm.value,
    role: role.value,
  }

  try {
    const response = await fetch("http://localhost:8000/api/accounts/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    const data = await response.json()

    if (response.ok) {
      const loginResp = await fetch("http://localhost:8000/api/accounts/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: email.value, password: password.value }),
      })
      const loginData = await loginResp.json()

      if (loginResp.ok && loginData.access) {
        localStorage.setItem("access", loginData.access)
        localStorage.setItem("refresh", loginData.refresh)

        const profileResp = await fetch("http://localhost:8000/api/accounts/profile/", {
          headers: { Authorization: `Bearer ${loginData.access}` },
        })
        if (profileResp.ok) {
          const user = await profileResp.json()
          userStore.setUser(user)
        }

        firstName.value = ""
        lastName.value  = ""
        email.value     = ""
        phone.value     = "+7 "
        phoneRaw.value  = "+7"
        password.value  = ""
        confirm.value   = ""
        role.value      = "executor"

        successMessage.value = "Регистрация прошла успешно! Перенаправляем в личный кабинет…"
        setTimeout(() => router.push("/profile"), 800)
      } else {
        errorMessage.value = "Регистрация успешна, но вход не выполнен. Попробуйте войти вручную."
      }
    } else {
      if (typeof data === "object" && data) {
        errorMessage.value = Object.values(data).flat().join(" ")
      } else {
        errorMessage.value = "Ошибка регистрации!"
      }
    }
  } catch {
    errorMessage.value = "Нет связи с сервером. Попробуйте позже."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Не превышаем высоту вьюпорта, скрываем переливы -->
  <div class="min-h-[100svh] md:min-h-[100dvh] grid grid-cols-1 md:grid-cols-2 overflow-hidden">
    <!-- Левая колонка: форма (скролл внутри при нехватке высоты) -->
    <div class="h-full flex items-center justify-center px-4 py-6 md:py-0 overflow-y-auto">
      <div class="w-full max-w-[520px] bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm p-6 md:p-8">
        <!-- Назад -->
        <router-link
          to="/"
          class="inline-flex items-center text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition mb-3"
        >
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
          На главную
        </router-link>

        <p class="text-xs text-gray-500 dark:text-gray-400">Давайте создадим вам аккаунт</p>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white mb-6">Заполните все поля</h1>

        <!-- Сообщения -->
        <div v-if="errorMessage" class="mb-3 rounded-lg bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300 px-3 py-2 text-sm">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="mb-3 rounded-lg bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300 px-3 py-2 text-sm">
          {{ successMessage }}
        </div>

        <form @submit.prevent="onRegister" class="space-y-4">
          <!-- Имя -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">Ваше имя</label>
            <input
              v-model="firstName"
              type="text"
              placeholder="Имя"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <!-- Фамилия -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">Ваша фамилия</label>
            <input
              v-model="lastName"
              type="text"
              placeholder="Фамилия"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">E-mail</label>
            <input
              v-model="email"
              type="email"
              placeholder="E-mail"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <!-- Телефон -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">Телефон</label>
            <input
              v-model="phone"
              @input="onPhoneInput"
              type="tel"
              placeholder="+7 999 123-45-67"
              maxlength="18"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <!-- Пароль -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">Пароль</label>
            <input
              v-model="password"
              type="password"
              placeholder="Пароль"
              required
              class="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            />
          </div>

          <!-- Подтверждение -->
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300">Повторите пароль</label>
            <input
              v-model="confirm"
              type="password"
              placeholder="Пароль"
              required
              :class="[
                'mt-1 w-full rounded-lg border bg-white dark:bg-gray-800 text-sm px-3 py-2 focus:outline-none focus:ring-2',
                isPasswordMismatch ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 dark:border-gray-700 focus:ring-indigo-600'
              ]"
            />
            <p v-if="isPasswordMismatch" class="mt-1 text-xs text-red-600 dark:text-red-400">
              Паролы не совпадают
            </p>
          </div>

          <!-- Роль -->
          <div class="flex items-center gap-6 text-sm">
            <label class="inline-flex items-center">
              <input type="radio" value="executor" v-model="role" class="accent-indigo-600" />
              <span class="ml-2 text-gray-700 dark:text-gray-300">Я исполнитель</span>
            </label>
            <label class="inline-flex items-center">
              <input type="radio" value="customer" v-model="role" class="accent-indigo-600" />
              <span class="ml-2 text-gray-700 dark:text-gray-300">Я заказчик</span>
            </label>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full inline-flex justify-center items-center gap-2 rounded-full bg-indigo-600 text-white py-3 px-4 font-medium hover:bg-indigo-700 disabled:opacity-60 transition"
          >
            <svg v-if="loading" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
            </svg>
            {{ loading ? "Регистрируем..." : "Зарегистрироваться" }}
          </button>
        </form>

        <p class="text-center text-xs mt-5 text-gray-600 dark:text-gray-400">
          Уже есть аккаунт?
          <router-link to="/login" class="text-indigo-600 dark:text-indigo-400 hover:underline">Войти</router-link>
        </p>
      </div>
    </div>

    <!-- Правая колонка: фон + слайдер (только на десктопе), занимает ровно высоту вьюпорта -->
    <div
      class="relative hidden md:block h-full bg-cover bg-center"
      :style="{ backgroundImage: `url('/bg-login4.png')` }"
    >
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600/40 to-indigo-900/40"></div>

      <div
        class="absolute bottom-10 left-1/2 -translate-x-1/2 w-[min(560px,90%)]
               bg-white/90 dark:bg-gray-900/80 backdrop-blur rounded-xl p-4 shadow-lg"
      >
        <p class="text-gray-800 dark:text-gray-100 text-sm transition-all duration-300">
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
