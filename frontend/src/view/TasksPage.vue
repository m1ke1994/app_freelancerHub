<!-- src/view/JobsCatalog.vue -->
<script setup>
import { ref, computed } from "vue"

/* Категории (замени при необходимости) */
const categories = [
  "Веб-разработка",
  "Мобильные приложения",
  "Дизайн",
  "Копирайтинг",
  "SEO и маркетинг",
  "Переводы",
]

/* Состояние фильтров */
const searchQuery = ref("")
const selectedCategory = ref("")
const budgetRange = ref([0, 200000]) // [min, max]
const remoteOnly = ref(false)
const urgentOnly = ref(false)
const sortBy = ref("newest") // newest | budget-high | budget-low | responses

/* Демоданные */
const jobs = ref([
  {
    id: 1,
    title: "Разработка интернет-магазина на Vue",
    deadline: "2 недели",
    location: "Удаленно",
    responses: 12,
    views: 340,
    budget: { min: 120000, max: 180000, currency: "₽" },
    clientName: "ООО «ТехМарт»",
    clientRating: 4.8,
    urgent: true,
    category: "Веб-разработка",
    skills: ["Vue 3", "Pinia", "Node.js"],
    description: "Нужно собрать интернет-магазин с каталогом, фильтрами и оплатой.",
    postedAt: "2025-08-10T10:00:00Z",
    remote: true,
  },
  {
    id: 2,
    title: "Дизайн мобильного приложения",
    deadline: "10 дней",
    location: "Москва/удаленно",
    responses: 8,
    views: 210,
    budget: { min: 70000, max: 90000, currency: "₽" },
    clientName: "Startup Labs",
    clientRating: 4.5,
    urgent: false,
    category: "Дизайн",
    skills: ["Figma", "UI/UX"],
    description: "Нужно продумать UX и отрисовать UI для iOS и Android.",
    postedAt: "2025-08-14T12:00:00Z",
    remote: true,
  },
  {
    id: 3,
    title: "SEO оптимизация корпоративного сайта",
    deadline: "1 месяц",
    location: "Санкт-Петербург",
    responses: 15,
    views: 480,
    budget: { min: 40000, max: 60000, currency: "₽" },
    clientName: "Digital Plus",
    clientRating: 4.2,
    urgent: false,
    category: "SEO и маркетинг",
    skills: ["SEO", "GA4", "Контент"],
    description: "Аудит, кластеризация, оптимизация контента и мета-данных.",
    postedAt: "2025-08-09T09:00:00Z",
    remote: false,
  },
])

/* Фильтрация + сортировка */
const filteredJobs = computed(() => {
  let list = jobs.value.slice()

  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(j =>
      j.title.toLowerCase().includes(q) ||
      j.description.toLowerCase().includes(q) ||
      j.skills.some(s => s.toLowerCase().includes(q))
    )
  }

  if (selectedCategory.value) {
    list = list.filter(j => j.category === selectedCategory.value)
  }

  const [minB, maxB] = budgetRange.value
  list = list.filter(j => j.budget.max >= minB && j.budget.min <= maxB)

  if (remoteOnly.value) list = list.filter(j => j.remote)
  if (urgentOnly.value) list = list.filter(j => j.urgent)

  switch (sortBy.value) {
    case "budget-high":
      list.sort((a, b) => b.budget.max - a.budget.max); break
    case "budget-low":
      list.sort((a, b) => a.budget.min - b.budget.min); break
    case "responses":
      list.sort((a, b) => a.responses - b.responses); break
    default: // newest
      list.sort((a, b) => new Date(b.postedAt) - new Date(a.postedAt))
  }

  return list
})

/* Двойной слайдер бюджета — чистый JS */
const budgetMin = 0
const budgetMax = 200000
const budgetStep = 5000
function setBudgetMin(e) {
  const val = Math.min(Number(e.target.value), budgetRange.value[1])
  budgetRange.value = [val, budgetRange.value[1]]
}
function setBudgetMax(e) {
  const val = Math.max(Number(e.target.value), budgetRange.value[0])
  budgetRange.value = [budgetRange.value[0], val]
}

/* Пагинация (демо) */
const page = ref(1)
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Сайдбар фильтров -->
      <aside class="lg:w-80 space-y-6">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-800">
            <h3 class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5h18M6 12h12M10 19h4"/>
              </svg>
              Фильтры
            </h3>
          </div>

          <div class="px-5 py-5 space-y-6">
            <!-- Поиск -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Поиск</label>
              <div class="relative">
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="11" cy="11" r="7" stroke-width="1.5"></circle>
                  <path d="M20 20l-3.5-3.5" stroke-width="1.5" stroke-linecap="round"></path>
                </svg>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Поиск по заданиям..."
                  class="w-full pl-10 pr-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700
                         bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                         focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
              </div>
            </div>

            <hr class="border-gray-200 dark:border-gray-800" />

            <!-- Категория -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Категория</label>
              <select
                v-model="selectedCategory"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700
                       bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-indigo-600"
              >
                <option value="">Все категории</option>
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <hr class="border-gray-200 dark:border-gray-800" />

            <!-- Бюджет -->
            <div class="space-y-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Бюджет (₽)</label>

              <div class="relative h-2 rounded bg-gray-200 dark:bg-gray-800">
                <div
                  class="absolute h-2 rounded bg-indigo-500"
                  :style="{
                    left: ((budgetRange[0] - budgetMin) / (budgetMax - budgetMin)) * 100 + '%',
                    width: ((budgetRange[1] - budgetRange[0]) / (budgetMax - budgetMin)) * 100 + '%'
                  }"
                />
                <!-- левый ползунок -->
                <input
                  class="range-thumb"
                  type="range"
                  :min="budgetMin"
                  :max="budgetMax"
                  :step="budgetStep"
                  :value="budgetRange[0]"
                  @input="setBudgetMin"
                />
                <!-- правый ползунок -->
                <input
                  class="range-thumb"
                  type="range"
                  :min="budgetMin"
                  :max="budgetMax"
                  :step="budgetStep"
                  :value="budgetRange[1]"
                  @input="setBudgetMax"
                />
              </div>

              <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>{{ Number(budgetRange[0]).toLocaleString() }} ₽</span>
                <span>{{ Number(budgetRange[1]).toLocaleString() }} ₽</span>
              </div>
            </div>

            <hr class="border-gray-200 dark:border-gray-800" />

            <!-- Доп. фильтры -->
            <div class="space-y-3">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Дополнительные фильтры</label>

              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-600"
                  v-model="remoteOnly"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">Только удаленная работа</span>
              </label>

              <label class="flex items-center gap-2">
                <input
                  type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-600"
                  v-model="urgentOnly"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">Только срочные задания</span>
              </label>
            </div>
          </div>
        </div>
      </aside>

      <!-- Основной контент -->
      <main class="flex-1">
        <!-- Заголовок + сортировка -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Каталог заданий</h1>
            <p class="text-gray-500 dark:text-gray-400">Найдено {{ filteredJobs.length }} заданий</p>
          </div>

          <div class="flex items-center gap-2">
            <label for="sort" class="text-sm text-gray-700 dark:text-gray-300">Сортировка:</label>
            <select
              id="sort"
              v-model="sortBy"
              class="w-48 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700
                     bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-indigo-600"
            >
              <option value="newest">Сначала новые</option>
              <option value="budget-high">Бюджет: по убыванию</option>
              <option value="budget-low">Бюджет: по возрастанию</option>
              <option value="responses">Меньше откликов</option>
            </select>
          </div>
        </div>

        <!-- Список заданий -->
        <div class="space-y-6">
          <template v-if="filteredJobs.length === 0">
            <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-center py-12">
              <div class="px-6">
                <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="7" stroke-width="1.5"></circle>
                    <path d="M20 20l-3.5-3.5" stroke-width="1.5" stroke-linecap="round"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Задания не найдены</h3>
                <p class="text-gray-500 dark:text-gray-400">Попробуйте изменить параметры поиска</p>
              </div>
            </div>
          </template>

          <template v-else>
            <div
              v-for="job in filteredJobs"
              :key="job.id"
              class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:shadow-lg transition-shadow"
            >
              <div class="px-5 pt-5">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <h3 class="text-xl font-semibold text-gray-900 dark:text-white hover:text-indigo-600 cursor-pointer">
                        {{ job.title }}
                      </h3>
                      <span
                        v-if="job.urgent"
                        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"
                      >Срочно</span>
                    </div>

                    <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                      <div class="flex items-center gap-1">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 2v3M16 2v3M3 9h18M4 7h16a1 1 0 0 1 1 1v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a1 1 0 0 1 1-1z"/>
                        </svg>
                        {{ job.deadline }}
                      </div>
                      <div class="flex items-center gap-1">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 21s7-4.35 7-10a7 7 0 1 0-14 0c0 5.65 7 10 7 10z"/>
                          <circle cx="12" cy="11" r="2.5"/>
                        </svg>
                        {{ job.location }}
                      </div>
                      <div class="flex items-center gap-1">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/>
                          <circle cx="9" cy="7" r="4"/>
                          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                        {{ job.responses }} откликов
                      </div>
                      <div class="flex items-center gap-1">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>
                          <circle cx="12" cy="12" r="3"/>
                        </svg>
                        {{ job.views }} просмотров
                      </div>
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="text-2xl font-bold text-indigo-600 mb-1">
                      {{ job.budget.min.toLocaleString() }} - {{ job.budget.max.toLocaleString() }} {{ job.budget.currency }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">{{ job.clientName }}</div>
                    <div class="flex items-center gap-1 text-sm text-yellow-500">
                      <span>★</span>
                      <span class="text-gray-700 dark:text-gray-300">{{ job.clientRating }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="px-5 pb-5">
                <p class="text-sm text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">
                  {{ job.description }}
                </p>

                <div class="flex flex-wrap gap-2 mb-4">
                  <span
                    v-for="skill in job.skills"
                    :key="skill"
                    class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  >
                    {{ skill }}
                  </span>
                </div>

                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <button
                      class="inline-flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium
                             bg-indigo-600 text-white hover:bg-indigo-700 transition"
                    >
                      Откликнуться
                      <svg class="w-4 h-4 ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 12h14M12 5l7 7-7 7"/>
                      </svg>
                    </button>

                    <button
                      class="inline-flex items-center justify-center w-9 h-9 rounded-md border border-gray-200 dark:border-gray-700
                             hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                      aria-label="Сохранить"
                    >
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.1 21.35a1 1 0 0 1-1.2 0C5.1 17.55 2 14.77 2 11.4A5.4 5.4 0 0 1 7.4 6a5.78 5.78 0 0 1 4.6 2.38A5.78 5.78 0 0 1 16.6 6A5.4 5.4 0 0 1 22 11.4c0 3.37-3.1 6.15-8.9 9.95z"/>
                      </svg>
                    </button>
                  </div>

                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    Опубликовано {{ new Date(job.postedAt).toLocaleDateString("ru-RU") }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Пагинация (демо) -->
        <div v-if="filteredJobs.length > 0" class="flex items-center justify-center gap-2 mt-8">
          <button
            class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700
                   text-gray-700 dark:text-gray-200 disabled:opacity-50"
            disabled
          >
            Предыдущая
          </button>
          <button class="px-3 py-2 rounded-md border text-sm border-indigo-600 bg-indigo-600 text-white">1</button>
          <button class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200">2</button>
          <button class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200">3</button>
          <button class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200">
            Следующая
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Двойной range поверх общего трека */
.range-thumb {
  position: absolute;
  inset: 0;
  width: 100%;
  appearance: none;
  background: transparent;
  pointer-events: none;
}
.range-thumb::-webkit-slider-thumb {
  appearance: none;
  pointer-events: auto;
  width: 18px;
  height: 18px;
  border-radius: 9999px;
  background: white;
  border: 2px solid rgb(99 102 241); /* indigo-500 */
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.08);
}
.range-thumb::-moz-range-thumb {
  pointer-events: auto;
  width: 18px;
  height: 18px;
  border-radius: 9999px;
  background: white;
  border: 2px solid rgb(99 102 241);
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.08);
}
.range-thumb::-webkit-slider-runnable-track { background: transparent; }
.range-thumb::-moz-range-track { background: transparent; }
</style>
