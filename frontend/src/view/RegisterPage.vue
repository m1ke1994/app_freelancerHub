<!-- src/view/RegisterPage.vue -->
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
const confirm   = ref("")   // локально оставляем confirm для сравнения
const role      = ref("executor")

const errorMessage = ref("")
const loading = ref(false)

const slides = [
  "FreelanceHub — это маркетплейс фриланс-услуг...",
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
  const p = [d.slice(0,3), d.slice(3,6), d.slice(6,8), d.slice(8,10)].filter(Boolean)
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
const isPhoneInvalid = computed(() => !/^\+7\d{10}$/.test(phoneRaw.value))
const isEmailInvalid = computed(() => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))

async function onRegister() {
  errorMessage.value = ""
  if (!firstName.value || !lastName.value) return errorMessage.value = "Укажите имя и фамилию"
  if (isEmailInvalid.value) return errorMessage.value = "Некорректный e-mail"
  if (isPhoneInvalid.value) return errorMessage.value = "Телефон должен быть в формате +7XXXXXXXXXX"
  if (isPasswordMismatch.value) return errorMessage.value = "Пароли не совпадают"

  loading.value = true
  try {
    const ok = await userStore.register({
      first_name: firstName.value.trim(),
      last_name:  lastName.value.trim(),
      email:      email.value.trim().toLowerCase(),
      phone:      phoneRaw.value,
      password:   password.value,
      password2:  confirm.value,   // 🔑 ВАЖНО: используем password2
      role:       role.value,
    })

    if (ok) {
      const finalRole = userStore.user?.role || role.value
      if (finalRole === "executor") router.push("/dashboard/profile")
      else router.push("/dashboard/customer-profile")
    } else {
      errorMessage.value = userStore.error || "Ошибка регистрации"
    }
  } catch {
    errorMessage.value = "Нет связи с сервером."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[100svh] md:min-h-[100dvh] grid grid-cols-1 md:grid-cols-2 overflow-hidden">
    <div class="h-full flex items-center justify-center px-4 py-6 md:py-0 overflow-y-auto">
      <div class="w-full max-w-[520px] bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-sm p-6 md:p-8">
        <router-link to="/" class="inline-flex items-center text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition mb-3">
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
          На главную
        </router-link>

        <p class="text-xs text-gray-500 dark:text-gray-400">Давайте создадим вам аккаунт</p>
        <h1 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white mb-6">Заполните все поля</h1>

        <div v-if="errorMessage" class="mb-3 rounded-lg bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300 px-3 py-2 text-sm whitespace-pre-line">
          {{ errorMessage }}
        </div>

       <form @submit.prevent="onRegister" class="space-y-4">
  <!-- Имя -->
  <input
    v-model="firstName"
    type="text"
    placeholder="Имя"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2 
           bg-white text-gray-900 placeholder-gray-400 
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />

  <!-- Фамилия -->
  <input
    v-model="lastName"
    type="text"
    placeholder="Фамилия"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2
           bg-white text-gray-900 placeholder-gray-400
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />

  <!-- Email -->
  <input
    v-model="email"
    type="email"
    placeholder="E-mail"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2
           bg-white text-gray-900 placeholder-gray-400
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />

  <!-- Телефон -->
  <input
    v-model="phone"
    @input="onPhoneInput"
    type="tel"
    placeholder="+7 999 123-45-67"
    maxlength="18"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2
           bg-white text-gray-900 placeholder-gray-400
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />
  <p v-if="isPhoneInvalid" class="text-xs text-gray-600 dark:text-gray-400">
    Формат: +7XXXXXXXXXX
  </p>

  <!-- Пароль -->
  <input
    v-model="password"
    type="password"
    placeholder="Пароль"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2
           bg-white text-gray-900 placeholder-gray-400
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />

  <!-- Повтор -->
  <input
    v-model="confirm"
    type="password"
    placeholder="Повторите пароль"
    required
    class="w-full rounded-lg border border-gray-300 px-3 py-2
           bg-white text-gray-900 placeholder-gray-400
           dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400
           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
  />
  <p v-if="isPasswordMismatch" class="text-xs text-red-600 dark:text-red-400">
    Пароли не совпадают
  </p>

  <!-- Роль -->
  <div class="flex items-center gap-6 text-sm text-gray-700 dark:text-gray-200">
    <label class="inline-flex items-center">
      <input type="radio" value="executor" v-model="role" class="accent-indigo-600" />
      <span class="ml-2">Я исполнитель</span>
    </label>
    <label class="inline-flex items-center">
      <input type="radio" value="customer" v-model="role" class="accent-indigo-600" />
      <span class="ml-2">Я заказчик</span>
    </label>
  </div>

  <!-- Кнопка -->
  <button
    type="submit"
    :disabled="loading"
    class="w-full rounded-full bg-indigo-600 text-white py-3
           hover:bg-indigo-700 disabled:opacity-60
           dark:bg-indigo-500 dark:hover:bg-indigo-400"
  >
    {{ loading ? "Регистрируем..." : "Зарегистрироваться" }}
  </button>
</form>


        <p class="text-center text-xs mt-5">
          Уже есть аккаунт?
          <router-link to="/login" class="text-indigo-600 hover:underline">Войти</router-link>
        </p>
      </div>
    </div>

    <!-- Правая колонка -->
    <div class="relative hidden md:block h-full bg-cover bg-center" :style="{ backgroundImage: `url('/bg-login4.png')` }">
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600/40 to-indigo-900/40"></div>
      <div class="absolute bottom-10 left-1/2 -translate-x-1/2 w-[min(560px,90%)] bg-white/20 backdrop-blur rounded-xl p-4 shadow-lg">
        <p class="text-gray-700">{{ slides[currentIndex] }}</p>
      </div>
    </div>
  </div>
</template>
