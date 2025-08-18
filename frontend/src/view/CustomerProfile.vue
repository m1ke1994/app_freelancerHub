<!-- src/view/CustomerProfile.vue -->
<script setup>
import { ref, reactive, onMounted } from "vue"
import { useUserStore } from "@/store/userStore.js"

const userStore = useUserStore()

// Обязательные данные из регистрации
const requiredFields = reactive({
  first_name: "",
  last_name: "",
  email: "",
})

// Дополнительные поля
const form = reactive({
  company: "",          // Компания или ИП
  bio: "",              // О себе / о компании
  location: "",         // Город
  socials: {
    telegram: "",
    linkedin: "",
  },
  verified: false,      // Верифицирован как заказчик (флаг, пока для вида)
  projectsCount: 0,     // Сколько уже сделал заказов
  rating: null,         // Средняя оценка (если есть)
  availability: true,   // Принимаю новых исполнителей
})

// Секция сворачивания
const sections = reactive({
  about: true,
  socials: true,
})

onMounted(async () => {
  if (userStore.user) {
    const u = userStore.user
    requiredFields.first_name = u.first_name || ""
    requiredFields.last_name  = u.last_name || ""
    requiredFields.email      = u.email || ""

    form.company   = u.company || ""
    form.bio       = u.bio || ""
    form.location  = u.location || ""
    form.socials.telegram = u.socials?.telegram || ""
    form.socials.linkedin = u.socials?.linkedin || ""
    form.projectsCount = u.projects_count ?? 0
    form.rating        = u.rating ?? null
  } else {
    try { await userStore.fetchProfile?.() } catch {}
  }
})

const saving = ref(false)
const saveSuccess = ref(false)

async function onSave() {
  saving.value = true
  saveSuccess.value = false
  try {
    const payload = {
      company: form.company.trim(),
      bio: form.bio.trim(),
      location: form.location.trim(),
      socials: form.socials,
      availability: !!form.availability,
    }
    // здесь PATCH на бэкенд
    // await api.patch("/api/customer/profile/", payload)
    userStore.setUser?.({ ...(userStore.user||{}), ...payload })
    saveSuccess.value = true
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="py-8 px-4">
    <div class="mx-auto max-w-4xl">
      <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
        Анкета заказчика
      </h1>

      <!-- Обязательные поля -->
      <div class="rounded-xl border p-5 mb-6 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800">
        <h3 class="font-semibold mb-3 text-gray-900 dark:text-white">Основные данные</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input :value="requiredFields.first_name" disabled class="px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border" />
          <input :value="requiredFields.last_name" disabled class="px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border" />
          <input :value="requiredFields.email" disabled class="sm:col-span-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border" />
        </div>
      </div>

      <!-- О себе -->
      <div class="rounded-xl border p-5 mb-6 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800">
        <button @click="sections.about = !sections.about" class="flex justify-between items-center w-full">
          <h3 class="font-semibold text-gray-900 dark:text-white">О компании/о себе</h3>
          <span>{{ sections.about ? "▲" : "▼" }}</span>
        </button>
        <div v-if="sections.about" class="mt-4 space-y-3">
          <input v-model="form.company" placeholder="Компания или ИП" class="w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-900" />
          <input v-model="form.location" placeholder="Город" class="w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-900" />
          <textarea v-model="form.bio" rows="3" placeholder="Расскажите о своей деятельности и опыте заказов" class="w-full px-3 py-2 rounded-lg border bg-white dark:bg-gray-900"></textarea>
        </div>
      </div>

      <!-- Соцсети -->
      <div class="rounded-xl border p-5 mb-6 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800">
        <button @click="sections.socials = !sections.socials" class="flex justify-between items-center w-full">
          <h3 class="font-semibold text-gray-900 dark:text-white">Контакты / соцсети</h3>
          <span>{{ sections.socials ? "▲" : "▼" }}</span>
        </button>
        <div v-if="sections.socials" class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input v-model="form.socials.telegram" placeholder="@telegram" class="px-3 py-2 rounded-lg border bg-white dark:bg-gray-900" />
          <input v-model="form.socials.linkedin" placeholder="https://linkedin.com/…" class="px-3 py-2 rounded-lg border bg-white dark:bg-gray-900" />
        </div>
      </div>

      <!-- Статистика -->
      <div class="rounded-xl border p-5 mb-6 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800">
        <h3 class="font-semibold mb-3 text-gray-900 dark:text-white">Статистика</h3>
        <p class="text-gray-700 dark:text-gray-300">Заказов создано: <b>{{ form.projectsCount }}</b></p>
        <p class="text-gray-700 dark:text-gray-300">Средняя оценка: <b>{{ form.rating ?? "—" }}</b></p>
        <label class="flex items-center gap-2 mt-3">
          <input type="checkbox" v-model="form.availability" class="rounded border-gray-300 text-indigo-600" />
          <span class="text-gray-800 dark:text-gray-200">Принимаю новых исполнителей</span>
        </label>
      </div>

      <!-- Кнопки -->
      <div class="flex justify-end items-center gap-3">
        <p v-if="saveSuccess" class="text-green-600">Сохранено ✅</p>
        <button @click="onSave" :disabled="saving" class="px-5 py-3 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
          {{ saving ? "Сохраняем..." : "Сохранить" }}
        </button>
      </div>
    </div>
  </section>
</template>
