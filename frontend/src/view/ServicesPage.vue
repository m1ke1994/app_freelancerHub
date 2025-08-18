<!-- src/view/FreelancersCatalog.vue -->
<script setup>
import { ref, computed } from "vue"

/* Категории (замени на API при необходимости) */
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
const selectedRateType = ref("")   // '' | 'hour' | 'project'
const rateRange = ref([0, 5000])   // [min, max] ₽/час — применяется только к почасовым
const minRating = ref(0)           // 0 | 4 | 4.5 | 4.8
const sortBy = ref("rating")       // rating | rate-low | rate-high | projects

/* Демо-данные (замени на загрузку с бэка) */
const freelancers = ref([
  {
    id: 1,
    firstName: "Алексей",
    lastName: "Кузнецов",
    location: "Удаленно",
    rating: 4.9,
    completedProjects: 120,
    lastActive: "Онлайн",
    rateType: "hour",
    hourlyRate: 2500,
    projectRate: null,
    responseTime: "в течение часа",
    bio: "Frontend разработчик (Vue 3, Pinia, Tailwind). Пишу чисто, быстро, с фокусом на UX.",
    skills: ["Vue 3", "Pinia", "Tailwind", "Vite", "Nuxt", "Node.js", "REST"],
    avatar: "",
    categories: ["Веб-разработка"],
  },
  {
    id: 2,
    firstName: "Мария",
    lastName: "Иванова",
    location: "Москва",
    rating: 4.7,
    completedProjects: 80,
    lastActive: "Был(а) 2 ч назад",
    rateType: "hour",
    hourlyRate: 1800,
    projectRate: null,
    responseTime: "в течение дня",
    bio: "UI/UX дизайнер. Figma, дизайн-системы, прототипирование, мобильные интерфейсы.",
    skills: ["Figma", "UI/UX", "Design System", "Prototyping"],
    avatar: "",
    categories: ["Дизайн", "Мобильные приложения"],
  },
  {
    id: 3,
    firstName: "Дмитрий",
    lastName: "Поляков",
    location: "Санкт-Петербург",
    rating: 4.5,
    completedProjects: 60,
    lastActive: "Онлайн",
    rateType: "hour",
    hourlyRate: 900,
    projectRate: null,
    responseTime: "в течение 2 часов",
    bio: "SEO-специалист: аудит, семантика, кластеризация, контент-стратегия.",
    skills: ["SEO", "GA4", "Ahrefs", "Copywriting"],
    avatar: "",
    categories: ["SEO и маркетинг", "Копирайтинг"],
  },
  {
    id: 4,
    firstName: "Ольга",
    lastName: "Смирнова",
    location: "Новосибирск",
    rating: 4.8,
    completedProjects: 40,
    lastActive: "Онлайн",
    rateType: "project",
    hourlyRate: null,
    projectRate: 12000,
    responseTime: "в течение дня",
    bio: "Копирайтер, пишу тексты под SEO и лендинги.",
    skills: ["Copywriting", "SEO"],
    avatar: "",
    categories: ["Копирайтинг"],
  },
  {
    id: 5,
    firstName: "Игорь",
    lastName: "Сафонов",
    location: "Екатеринбург",
    rating: 4.6,
    completedProjects: 55,
    lastActive: "Был(а) 30 мин назад",
    rateType: "project",
    hourlyRate: null,
    projectRate: 35000,
    responseTime: "в течение 3 часов",
    bio: "Full-Stack (Django + Vue). Беру проекты под ключ: от бэка до фронта и деплоя.",
    skills: ["Django", "DRF", "PostgreSQL", "Vue 3", "Tailwind", "Docker"],
    avatar: "",
    categories: ["Веб-разработка"],
  },
])

/* Справочные значения для слайдера по часовой ставке */
const rateMin = 0
const rateMax = 5000
const rateStep = 100

function setRateMin(e) {
  const val = Math.min(Number(e.target.value), rateRange.value[1])
  rateRange.value = [val, rateRange.value[1]]
}
function setRateMax(e) {
  const val = Math.max(Number(e.target.value), rateRange.value[0])
  rateRange.value = [rateRange.value[0], val]
}

/* Утилита форматирования денег */
function fmt(n) {
  if (n == null) return ""
  return new Intl.NumberFormat("ru-RU").format(n)
}

/* Фильтрация + сортировка */
const filteredFreelancers = computed(() => {
  let list = freelancers.value.slice()

  // Поиск по имени, описанию, скиллам
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(f =>
      `${f.firstName} ${f.lastName}`.toLowerCase().includes(q) ||
      f.bio.toLowerCase().includes(q) ||
      f.skills.some(s => s.toLowerCase().includes(q))
    )
  }

  // Категория
  if (selectedCategory.value) {
    list = list.filter(f => f.categories?.includes(selectedCategory.value))
  }

  // Тип оплаты
  if (selectedRateType.value) {
    list = list.filter(f => f.rateType === selectedRateType.value)
  }

  // Почасовая ставка — фильтр применяем ТОЛЬКО к rateType === 'hour'
  const [minR, maxR] = rateRange.value
  list = list.filter(f => {
    if (f.rateType === "hour") {
      return f.hourlyRate >= minR && f.hourlyRate <= maxR
    }
    return true
  })

  // Минимальный рейтинг
  if (minRating.value > 0) {
    list = list.filter(f => f.rating >= minRating.value)
  }

  // Для сортировки по ставке приведём оба типа к числу (hourlyRate | projectRate)
  const getNormRate = (f) => f.rateType === "hour" ? f.hourlyRate ?? 0 : f.projectRate ?? 0

  // Сортировка
  switch (sortBy.value) {
    case "rate-low":
      list.sort((a, b) => getNormRate(a) - getNormRate(b))
      break
    case "rate-high":
      list.sort((a, b) => getNormRate(b) - getNormRate(a))
      break
    case "projects":
      list.sort((a, b) => b.completedProjects - a.completedProjects)
      break
    default: // rating
      list.sort((a, b) => b.rating - a.rating)
  }

  return list
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Сайдбар фильтров -->
      <aside class="lg:w-80 space-y-6">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-800">
            <h3 class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-gray-100">
              <!-- icon Filter -->
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
                  placeholder="Поиск исполнителей..."
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

            <!-- Тип оплаты -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Тип оплаты</label>
              <select
                v-model="selectedRateType"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700
                       bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-indigo-600"
              >
                <option value="">Любой</option>
                <option value="hour">Почасовая</option>
                <option value="project">За проект</option>
              </select>
            </div>

            <hr class="border-gray-200 dark:border-gray-800" />

            <!-- Почасовая ставка (актуально только для 'hour') -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Почасовая ставка (₽)</label>
                <span class="text-xs text-gray-500 dark:text-gray-400"
                      :class="selectedRateType === 'project' ? 'italic opacity-70' : ''">
                  только для почасовых
                </span>
              </div>

              <div class="relative h-2 rounded bg-gray-200 dark:bg-gray-800"
                   :class="selectedRateType === 'project' ? 'opacity-60 pointer-events-none' : ''">
                <div
                  class="absolute h-2 rounded bg-indigo-500"
                  :style="{
                    left: ((rateRange[0] - rateMin) / (rateMax - rateMin)) * 100 + '%',
                    width: ((rateRange[1] - rateRange[0]) / (rateMax - rateMin)) * 100 + '%'
                  }"
                />
                <!-- левый ползунок -->
                <input
                  class="range-thumb"
                  type="range"
                  :min="rateMin"
                  :max="rateMax"
                  :step="rateStep"
                  :value="rateRange[0]"
                  @input="setRateMin"
                />
                <!-- правый ползунок -->
                <input
                  class="range-thumb"
                  type="range"
                  :min="rateMin"
                  :max="rateMax"
                  :step="rateStep"
                  :value="rateRange[1]"
                  @input="setRateMax"
                />
              </div>

              <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>{{ fmt(rateRange[0]) }} ₽</span>
                <span>{{ fmt(rateRange[1]) }} ₽</span>
              </div>
            </div>

            <hr class="border-gray-200 dark:border-gray-800" />

            <!-- Минимальный рейтинг -->
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Минимальный рейтинг</label>
              <select
                v-model.number="minRating"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700
                       bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100
                       focus:outline-none focus:ring-2 focus:ring-indigo-600"
              >
                <option :value="0">Любой рейтинг</option>
                <option :value="4">4+ звезды</option>
                <option :value="4.5">4.5+ звезды</option>
                <option :value="4.8">4.8+ звезды</option>
              </select>
            </div>
          </div>
        </div>
      </aside>

      <!-- Основной контент -->
      <main class="flex-1">
        <!-- Заголовок + сортировка -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Каталог исполнителей</h1>
            <p class="text-gray-500 dark:text-gray-400">Найдено {{ filteredFreelancers.length }} специалистов</p>
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
              <option value="rating">По рейтингу</option>
              <option value="rate-low">По ставке: ниже → выше</option>
              <option value="rate-high">По ставке: выше → ниже</option>
              <option value="projects">По количеству проектов</option>
            </select>
          </div>
        </div>

        <!-- Список исполнителей -->
        <div class="space-y-6">
          <template v-if="filteredFreelancers.length === 0">
            <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-center py-12">
              <div class="px-6">
                <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <!-- icon User -->
                  <svg class="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="8" r="4" stroke-width="1.5" />
                    <path d="M4 20c0-4 4-6 8-6s8 2 8 6" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold mb-2 text-gray-900 dark:text-white">Исполнители не найдены</h3>
                <p class="text-gray-500 dark:text-gray-400">Попробуйте изменить параметры поиска</p>
              </div>
            </div>
          </template>

          <template v-else>
            <div
              v-for="f in filteredFreelancers"
              :key="f.id"
              class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:shadow-lg transition-shadow"
            >
              <div class="p-6">
                <div class="flex items-start gap-6">
                  <!-- Аватар с фоллбеком -->
                  <div class="relative w-16 h-16 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0">
                    <img v-if="f.avatar" :src="f.avatar" alt="" class="w-full h-full object-cover" />
                    <span v-else class="text-lg font-semibold text-gray-700 dark:text-gray-200">
                      {{ f.firstName[0] }}{{ f.lastName[0] }}
                    </span>
                  </div>

                  <div class="flex-1">
                    <div class="flex items-start justify-between mb-3">
                      <div>
                        <h3 class="text-xl font-semibold mb-1 text-gray-900 dark:text-white">
                          {{ f.firstName }} {{ f.lastName }}
                        </h3>
                        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                          <div class="flex items-center gap-1">
                            <!-- icon MapPin -->
                            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 21s7-4.35 7-10a7 7 0 1 0-14 0c0 5.65 7 10 7 10z"/>
                              <circle cx="12" cy="11" r="2.5"/>
                            </svg>
                            {{ f.location }}
                          </div>
                          <div class="flex items-center gap-1">
                            <!-- icon Star -->
                            <svg class="w-4 h-4 text-yellow-400" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.172L12 18.896l-7.336 3.873 1.402-8.172L.132 9.21l8.2-1.192z"/>
                            </svg>
                            {{ f.rating }} ({{ f.completedProjects }} проектов)
                          </div>
                          <span :class="f.lastActive === 'Онлайн' ? 'text-green-600' : ''">
                            {{ f.lastActive }}
                          </span>
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="text-2xl font-bold text-indigo-600 mb-1">
                          <template v-if="f.rateType === 'hour'">
                            {{ fmt(f.hourlyRate) }} ₽/час
                          </template>
                          <template v-else>
                            {{ fmt(f.projectRate) }} ₽/проект
                          </template>
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Ответ: {{ f.responseTime }}</div>
                      </div>
                    </div>

                    <p class="text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">
                      {{ f.bio }}
                    </p>

                    <div class="flex flex-wrap gap-2 mb-4">
                      <span
                        v-for="skill in f.skills.slice(0, 6)"
                        :key="skill"
                        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                      >
                        {{ skill }}
                      </span>
                      <span
                        v-if="f.skills.length > 6"
                        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300"
                      >
                        +{{ f.skills.length - 6 }} еще
                      </span>
                    </div>

                    <div class="flex items-center gap-3">
                      <button
                        class="inline-flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
                               bg-indigo-600 text-white hover:bg-indigo-700 transition"
                      >
                        <!-- icon Message -->
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 15a4 4 0 0 1-4 4H7l-4 4V5a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v10z"/>
                        </svg>
                        Написать
                      </button>
                      <button
                        class="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium border
                               border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-100
                               hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                      >
                        Посмотреть профиль
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Пагинация (демо) -->
        <div v-if="filteredFreelancers.length > 0" class="flex items-center justify-center gap-2 mt-8">
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
