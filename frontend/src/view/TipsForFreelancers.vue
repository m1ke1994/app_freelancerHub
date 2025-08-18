<!-- src/components/FreelancerTips.vue -->
<script setup>
import { ref, computed } from "vue"
import { useUserStore } from "@/store/userStore.js"

const query = ref("")
const activeTags = ref(new Set()) // выбранные фильтры
const favorites = ref(new Set())  // локальные избранные
const userStore = useUserStore()

async function onSave() {
  saveSuccess.value = false
  saveError.value = ""
  if (!validate()) return
  try {
    const payload = {
      title: form.title.trim(),
      bio: form.bio.trim(),
      location: form.location.trim(),
      gender: form.gender || null,
      education: form.education || null,
      status: form.status || "open",
      categories: form.categories,
      skills: form.skills,
      rate_type: form.rateType,
      hourly_rate: form.rateType === "hour" ? Number(form.hourlyRate) : null,
      project_rate: form.rateType === "project" ? Number(form.projectRate) : null,
      availability: !!form.availability,
      links: form.links,
      socials: form.socials,
      portfolio: form.portfolio,
    }
    await userStore.updateProfile(payload)
    saveSuccess.value = true
  } catch (e) {
    saveError.value = "Не удалось сохранить изменения"
  }
}

async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    await userStore.uploadAvatar(file)
  } catch (e) {
    // показать ошибку
  }
}

const tags = [
  { key: "start", label: "Старт", icon: "rocket" },
  { key: "portfolio", label: "Портфолио", icon: "gallery" },
  { key: "pricing", label: "Цены", icon: "coin" },
  { key: "process", label: "Процессы", icon: "gear" },
  { key: "clients", label: "Клиенты", icon: "handshake" },
  { key: "growth", label: "Рост", icon: "growth" },
]

const tips = [
  {
    id: 1,
    title: "Соберите 3–5 сильных кейсов",
    text: "Покажите процесс: задачи, ваши решения, результат и цифры. Даже учебные проекты подойдут, если хорошо оформлены.",
    icon: "gallery",
    tag: "portfolio"
  },
  {
    id: 2,
    title: "Определите минимальную ставку",
    text: "Посчитайте желаемый доход, налоги и время. Добавьте 20–30% на форс-мажоры. Указывайте вилку и аргументируйте.",
    icon: "coin",
    tag: "pricing"
  },
  {
    id: 3,
    title: "Пишите отклики как мини-план",
    text: "1–2 конкретных гипотезы решения, срок, стоимость и следующий шаг. Без воды — с пользой для заказчика.",
    icon: "message",
    tag: "clients"
  },
  {
    id: 4,
    title: "Фиксируйте ТЗ и границы работ",
    text: "Коротко: цели, объём, критерии приёмки, сроки, способы связи. Доп. правки — отдельно, чтобы не расползалось.",
    icon: "doc",
    tag: "process"
  },
  {
    id: 5,
    title: "Работайте итерациями",
    text: "Делите задачу на этапы с демо. Это снижает риски и ускоряет обратную связь.",
    icon: "steps",
    tag: "process"
  },
  {
    id: 6,
    title: "Держите профиль живым",
    text: "Регулярно обновляйте навыки, добавляйте отзывы, показывайте текущую занятость — это повышает доверие.",
    icon: "id",
    tag: "growth"
  },
  {
    id: 7,
    title: "Стартуйте с нишевого позиционирования",
    text: "Узкая специализация понятнее: «лендинги для онлайн-курсов», «правки в Vue 3», «миграции Django → DRF».",
    icon: "target",
    tag: "start"
  },
  {
    id: 8,
    title: "Соберите шаблоны",
    text: "Шаблоны брифа, оценок, акта приёмки, чек-лист запуска — экономят время и добавляют профессионализма.",
    icon: "templates",
    tag: "process"
  },
  {
    id: 9,
    title: "Запрашивайте отзыв по структуре",
    text: "Короткий опрос: цель, что понравилось, что улучшить, цифры результата. Разрешение публиковать — сразу.",
    icon: "star",
    tag: "clients"
  },
  {
    id: 10,
    title: "Учитесь апселлить корректно",
    text: "Предлагайте смежные улучшения после базового результата: аналитика, A/B, оптимизация скорости, техподдержка.",
    icon: "up",
    tag: "growth"
  },
]

function toggleTag(key) {
  if (activeTags.value.has(key)) activeTags.value.delete(key)
  else activeTags.value.add(key)
}

function clearFilters() {
  activeTags.value.clear()
  query.value = ""
}

function toggleFav(id) {
  if (favorites.value.has(id)) favorites.value.delete(id)
  else favorites.value.add(id)
}

const filteredTips = computed(() => {
  const q = query.value.trim().toLowerCase()
  const needTag = activeTags.value.size > 0

  return tips.filter(t => {
    const textMatch = !q || `${t.title} ${t.text}`.toLowerCase().includes(q)
    const tagMatch = !needTag || activeTags.value.has(t.tag)
    return textMatch && tagMatch
  })
})
</script>

<template>
  <section class="py-12 px-4 bg-white dark:bg-gray-900">
    <div class="mx-auto max-w-7xl">
      <!-- Заголовок -->
      <div class="flex flex-col items-center text-center gap-2 mb-8">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white">Советы фрилансерам</h2>
        <p class="text-gray-600 dark:text-gray-400">
          Подборка практических рекомендаций: от старта и портфолио до цен, процессов и роста
        </p>
      </div>

      <!-- Панель управления -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <!-- Поиск -->
        <div class="relative w-full sm:max-w-md">
          <input
            v-model="query"
            type="text"
            placeholder="Поиск по советам…"
            class="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-2.5 pr-10 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
            <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 21l-4.35-4.35M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- Кнопка сброса -->
        <button
          @click="clearFilters"
          class="inline-flex items-center justify-center px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-800 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
        >
          Сбросить
        </button>
      </div>

      <!-- Теги -->
      <div class="mt-5 flex flex-wrap gap-2">
        <button
          v-for="t in tags"
          :key="t.key"
          @click="toggleTag(t.key)"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition border"
          :class="activeTags.has(t.key)
            ? 'bg-indigo-600 text-white border-indigo-600'
            : 'border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'"
        >
          <!-- маленькая иконка-эмодзи в стиле проекта -->
          <span class="grid place-items-center w-5 h-5">
            <svg v-if="t.icon==='rocket'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 4l6 6-6 6-4-4-6 2 2-6-4-4 6-6 6 6Z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="t.icon==='gallery'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 5h18v14H3V5Zm5 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm-2 6l5-5 3 3 3-3 3 5H6Z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="t.icon==='coin'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.66 3.13 3 7 3s7-1.34 7-3V6M5 12v6c0 1.66 3.13 3 7 3s7-1.34 7-3v-6"/>
            </svg>
            <svg v-else-if="t.icon==='gear'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm8 4h2m-18 0H2m14.95 6.95 1.41 1.41M5.64 5.64 4.22 4.22m12.73 0 1.41-1.41M5.64 18.36 4.22 19.78"/>
            </svg>
            <svg v-else-if="t.icon==='handshake'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 12l3-3a3 3 0 0 1 4 4l-4 4m-6-1 3 3m-8-9 4 4a3 3 0 0 0 4 0l1-1" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="t.icon==='growth'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 21h18M7 17V9m5 8V7m5 10V5M7 9l5-2 5-2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          {{ t.label }}
        </button>
      </div>

      <!-- Сетка карточек -->
      <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <article
          v-for="tip in filteredTips"
          :key="tip.id"
          class="group h-full rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-sm hover:shadow-md transition"
        >
          <div class="flex items-start gap-4">
            <!-- Иконка -->
            <div class="shrink-0 grid place-items-center w-14 h-14 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300">
              <svg v-if="tip.icon==='gallery'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 5h18v14H3V5Zm5 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm-2 6l5-5 3 3 3-3 3 5H6Z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='coin'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.66 3.13 3 7 3s7-1.34 7-3V6M5 12v6c0 1.66 3.13 3 7 3s7-1.34 7-3v-6"/>
              </svg>
              <svg v-else-if="tip.icon==='message'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 12c0 4.418-4.03 8-9 8-1.1 0-2.15-.18-3.1-.51L3 21l1.6-4.2C4.2 15.58 3 13.9 3 12c0-4.42 4.03-8 9-8s9 3.58 9 8Z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='doc'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M7 3h7l5 5v13H7V3Zm7 0v5h5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='steps'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 21h18M6 17h4v-4h4v-4h4V5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='id'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 5h18v14H3V5Zm6 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm8 6h-8a4 4 0 0 1 8 0Z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='target'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-5a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm0-4v4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='templates'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='star'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="m12 3 2.9 5.9L21 10.2l-4.5 4.4L17.8 21 12 18.2 6.2 21l1.3-6.4L3 10.2l6.1-1.3L12 3Z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="tip.icon==='up'" viewBox="0 0 24 24" class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 19V5m0 0 6 6M12 5 6 11" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <!-- Контент -->
            <div class="min-w-0">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center justify-center text-xs font-semibold text-white bg-indigo-600 rounded-full w-6 h-6 leading-none">
                    {{ tip.id }}
                  </span>
                  <h3 class="font-semibold text-gray-900 dark:text-white leading-tight">
                    {{ tip.title }}
                  </h3>
                </div>

                <!-- Избранное -->
                <button
                  @click="toggleFav(tip.id)"
                  class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
                  :aria-pressed="favorites.has(tip.id)"
                  :title="favorites.has(tip.id) ? 'Убрать из избранного' : 'В избранное'"
                >
                  <svg v-if="favorites.has(tip.id)" viewBox="0 0 24 24" class="w-5 h-5 text-yellow-500" fill="currentColor">
                    <path d="m12 3 2.9 5.9L21 10.2l-4.5 4.4L17.8 21 12 18.2 6.2 21l1.3-6.4L3 10.2l6.1-1.3L12 3Z" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="m12 3 2.9 5.9L21 10.2l-4.5 4.4L17.8 21 12 18.2 6.2 21l1.3-6.4L3 10.2l6.1-1.3L12 3Z" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>

              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {{ tip.text }}
              </p>

              <!-- бейдж темы -->
              <div class="mt-3">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-900">
                  <svg viewBox="0 0 24 24" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round"/>
                  </svg>
                  {{
                    tip.tag === 'start' ? 'Старт' :
                    tip.tag === 'portfolio' ? 'Портфолио' :
                    tip.tag === 'pricing' ? 'Цены' :
                    tip.tag === 'process' ? 'Процессы' :
                    tip.tag === 'clients' ? 'Клиенты' : 'Рост'
                  }}
                </span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- CTA -->
      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
        <router-link
          to="/register"
          class="inline-flex items-center justify-center px-5 py-3 rounded-full bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition w-full sm:w-auto"
        >
          Создать профиль
          <span class="ml-2" aria-hidden="true">→</span>
        </router-link>
        <router-link
          to="/tasks"
          class="inline-flex items-center justify-center px-5 py-3 rounded-full border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 transition w-full sm:w-auto"
        >
          Смотреть задания
        </router-link>
      </div>
    </div>
  </section>
</template>
