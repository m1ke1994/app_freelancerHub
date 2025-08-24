<!-- src/view/JobsCatalog.vue -->
<script setup>
import { ref, computed, watch, onMounted } from "vue"

/* === CONFIG === */
const API_BASE = (import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "")
const PAGE_SIZE = 20

/* === UI state === */
const loading = ref(false)
const error = ref("")

/* === Фильтры === */
const searchQuery = ref("")
const selectedCategory = ref("")
const budgetRange = ref([0, 200000]) // [min, max]
const remoteOnly = ref(false)
const urgentOnly = ref(false)
const sortBy = ref("newest") // newest | budget-high | budget-low | responses

/* === Данные === */
const categories = ref([])
const jobs = ref([])
const total = ref(0)
const page = ref(1)

/* === Служебное === */
const budgetMin = 0
const budgetMax = 200000
const budgetStep = 5000

const orderingMap = {
  newest: "-created_at",
  "budget-high": "-bmax",
  "budget-low": "bmin",
  responses: "responses_count_annot",
}

/* ===== helpers ===== */
function setBudgetMin(e) {
  const val = Math.min(Number(e.target.value), budgetRange.value[1])
  budgetRange.value = [val, budgetRange.value[1]]
}
function setBudgetMax(e) {
  const val = Math.max(Number(e.target.value), budgetRange.value[0])
  budgetRange.value = [budgetRange.value[0], val]
}

function buildQuery() {
  const params = new URLSearchParams()
  const q = searchQuery.value.trim()
  if (q) params.set("q", q)
  if (selectedCategory.value) params.set("category", selectedCategory.value)
  if (remoteOnly.value) params.set("remote", "true")
  if (urgentOnly.value) params.set("urgent", "true")

  const [mn, mx] = budgetRange.value || []
  if (Number.isFinite(+mn)) params.set("budget_min", String(+mn))
  if (Number.isFinite(+mx)) params.set("budget_max", String(+mx))

  params.set("ordering", orderingMap[sortBy.value] || "-created_at")
  params.set("page", String(page.value || 1))
  params.set("page_size", String(PAGE_SIZE))
  return params.toString()
}

function normalizeClientName(owner) {
  const full = owner?.full_name?.trim?.()
  if (full) return full
  const join = [owner?.first_name, owner?.last_name].filter(Boolean).join(" ").trim()
  if (join) return join
  if (owner?.username) return owner.username
  if (owner?.email && owner.email.includes("@")) return owner.email.split("@")[0]
  if (Number.isFinite(owner?.id)) return `ID ${owner.id}`
  return "Клиент"
}

function normalizeClientUsername(owner) {
  if (owner?.username?.trim?.()) return owner.username.trim()
  if (owner?.email && owner.email.includes("@")) return owner.email.split("@")[0]
  if (Number.isFinite(owner?.id)) return `user${owner.id}`
  return "user"
}

function toNumOrNull(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

function formatBudget(b) {
  const cur = b?.currency || "₽"
  const hasMin = Number.isFinite(b?.min)
  const hasMax = Number.isFinite(b?.max)

  if (hasMin && hasMax) {
    if (b.min === b.max) return `${b.min.toLocaleString()} ${cur}`
    return `от ${b.min.toLocaleString()} до ${b.max.toLocaleString()} ${cur}`
  }
  if (hasMin) return `от ${b.min.toLocaleString()} ${cur}`
  if (hasMax) return `до ${b.max.toLocaleString()} ${cur}`
  return "не указан"
}

/* ===== API ===== */
async function fetchCategories() {
  try {
    const r = await fetch(`${API_BASE}/api/jobs/categories/`, { headers: { Accept: "application/json" } })
    if (!r.ok) return
    const data = await r.json()
    categories.value = Array.isArray(data) ? data : []
  } catch { /* no-op */ }
}

async function fetchJobs() {
  loading.value = true
  error.value = ""
  try {
    const qs = buildQuery()
    const res = await fetch(`${API_BASE}/api/jobs/?${qs}`, { headers: { Accept: "application/json" } })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    total.value = data?.count || 0

    jobs.value = (data?.results || []).map(it => {
      const owner = it.owner || {}

      // Определяем min/max по типу бюджета без "нулей-заменителей":
      // fixed -> min=max=fixed; range -> берем min/max; иначе null.
      let min = null
      let max = null
      if (it.budget_type === "fixed") {
        const fixed = toNumOrNull(it.budget_fixed)
        min = fixed
        max = fixed
      } else if (it.budget_type === "range") {
        min = toNumOrNull(it.budget_min)
        max = toNumOrNull(it.budget_max)
      }

      return {
        id: it.id,
        title: it.title,
        deadline: it.deadline_text || it.deadline || "",
        location: it.location || (it.remote ? "Удаленно" : ""),
        responses: it.responses_count ?? 0,
        views: it.views_count ?? 0,
        budget: { min, max, currency: "₽" },
        clientName: normalizeClientName(owner),
        clientUsername: normalizeClientUsername(owner),
        clientRating: Number(owner?.rating ?? 0),
        urgent: !!it.urgent,
        category: it.category,
        skills: Array.isArray(it.skills) ? it.skills : [],
        description: it.description || "",
        postedAt: it.created_at,
        remote: !!it.remote,
      }
    })
  } catch (e) {
    error.value = e?.message || "Ошибка загрузки"
    jobs.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

/* === Дебаунс перезагрузки при изменении фильтров === */
let t = null
function refetchDebounced() {
  clearTimeout(t)
  t = setTimeout(() => { page.value = 1; fetchJobs() }, 250)
}

onMounted(() => {
  fetchCategories()
  fetchJobs()
})
watch([searchQuery, selectedCategory, remoteOnly, urgentOnly, sortBy, budgetRange], refetchDebounced)
watch(page, fetchJobs)

/* === Вспомогательные вычисления для UI === */
const totalPages = computed(() => Math.max(1, Math.ceil((total.value || 0) / PAGE_SIZE)))
const hasResults = computed(() => (jobs.value?.length || 0) > 0)

/* Псевдо-селектор для шаблона */
const filteredJobs = computed(() => jobs.value)
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
                <input
                  class="range-thumb"
                  type="range"
                  :min="budgetMin"
                  :max="budgetMax"
                  :step="budgetStep"
                  :value="budgetRange[0]"
                  @input="setBudgetMin"
                />
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
            <p class="text-gray-500 dark:text-gray-400">
              <template v-if="loading">Загрузка…</template>
              <template v-else>Найдено {{ total }} заданий</template>
            </p>
            <p v-if="error" class="text-rose-600 text-sm mt-1">{{ error }}</p>
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
          <template v-if="!loading && !hasResults">
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
            <!-- skeleton -->
            <div v-if="loading" class="grid gap-4">
              <div v-for="n in 3" :key="n" class="h-32 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 animate-pulse"></div>
            </div>

            <div
              v-else
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
                      {{ formatBudget(job.budget) }}
                    </div>

                    <!-- Имя и юзернейм -->
                    <div class="text-sm text-gray-700 dark:text-gray-300">
                      {{ job.clientName }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      @{{ job.clientUsername }}
                    </div>

                    <!-- Рейтинг (если есть) -->
                    <div class="flex items-center gap-1 text-sm text-yellow-500 mt-1" v-if="job.clientRating > 0">
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

        <!-- Пагинация -->
        <div v-if="hasResults && !loading" class="flex items-center justify-center gap-2 mt-8">
          <button
            class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700
                   text-gray-700 dark:text-gray-200 disabled:opacity-50"
            :disabled="page <= 1"
            @click="page = Math.max(1, page - 1)"
          >
            Предыдущая
          </button>

          <span class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200">
            {{ page }} / {{ totalPages }}
          </span>

          <button
            class="px-3 py-2 rounded-md border text-sm border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200"
            :disabled="page >= totalPages"
            @click="page = Math.min(totalPages, page + 1)"
          >
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
  border: 2px solid rgb(99 102 241);
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
