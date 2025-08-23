<!-- src/view/PostJobWizard.vue -->
<script setup>
import { ref, reactive, computed } from "vue"
import { useUserStore, baseURL } from "@/store/userStore.js"

/* ===== Auth / Store ===== */
const userStore = useUserStore()

/* Шаги */
const totalSteps = 4
const currentStep = ref(1)
const progress = computed(() => (currentStep.value - 1) / (totalSteps - 1) * 100)

/* Справочники */
const categories = [
  "Веб-разработка",
  "Мобильные приложения",
  "Дизайн",
  "Копирайтинг",
  "SEO и маркетинг",
  "Переводы",
]

const popularSkills = [
  "Vue 3", "Pinia", "Tailwind", "Vite", "Nuxt",
  "Node.js", "Express", "PostgreSQL", "Figma", "UI/UX",
  "SEO", "GA4", "TypeScript", "REST", "GraphQL",
]

/* Данные формы */
const formData = reactive({
  title: "",
  category: "",
  description: "",
  skills: [],
  budgetType: "fixed",   // fixed | range
  budgetFixed: "",
  budgetMin: "",
  budgetMax: "",
  deadline: "",
  deadlineType: "flexible", // flexible | strict
  location: "",
  remote: true,
  urgent: false,
  attachments: [],       // File[]
})

/* Хелперы */
function updateFormData(key, value) {
  formData[key] = value
}

const newSkill = ref("")
function addSkill(skill) {
  const s = (skill || "").trim()
  if (!s) return
  if (!formData.skills.includes(s)) formData.skills.push(s)
  newSkill.value = ""
}
function removeSkill(skill) {
  formData.skills = formData.skills.filter((x) => x !== skill)
}

/* Навигация */
function canProceed() {
  if (currentStep.value === 1) {
    return !!(formData.title && formData.category && formData.description && formData.description.trim().length >= 10)
  }
  if (currentStep.value === 2) {
    return formData.skills.length > 0
  }
  if (currentStep.value === 3) {
    if (formData.budgetType === "fixed") return !!(formData.budgetFixed)
    return !!(formData.budgetMin && formData.budgetMax)
  }
  return true
}
function nextStep() {
  if (currentStep.value < totalSteps && canProceed()) currentStep.value++
}
function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

/* Файлы */
const fileInputRef = ref(null)
function openFileDialog() { fileInputRef.value?.click() }
function handleFileUpload(e) {
  const files = Array.from(e.target.files || [])
  formData.attachments.push(...files)
  e.target.value = "" // сброс выбора
}
function removeFile(index) { formData.attachments.splice(index, 1) }

/* ====== СТАТУС ОТПРАВКИ / АПИ ====== */
const submitting = ref(false)
const submitSuccess = ref(false)
const submitError = ref("")
const createdJobId = ref(null)
let statusTimer = null
function clearStatusAfter(ms = 3500) {
  if (statusTimer) clearTimeout(statusTimer)
  statusTimer = setTimeout(() => {
    submitSuccess.value = false
    submitError.value = ""
  }, ms)
}

async function authedFetch(url, options = {}) {
  const headers = new Headers(options.headers || {})
  const isFormData = options.body instanceof FormData
  if (!isFormData && !headers.has("Content-Type")) headers.set("Content-Type", "application/json")
  if (userStore?.access) headers.set("Authorization", `Bearer ${userStore.access}`)
  const resp = await fetch(url, { ...options, headers })
  return resp
}

/* Сабмит */
async function handleSubmit() {
  submitSuccess.value = false
  submitError.value = ""
  createdJobId.value = null

  if (!userStore?.isAuth) {
    submitError.value = "Войдите в систему, чтобы разместить задание."
    clearStatusAfter()
    return
  }
  if (!userStore.user || userStore.user.role !== "customer") {
    submitError.value = "Создавать задания может только пользователь с ролью «заказчик»."
    clearStatusAfter()
    return
  }
  if (!canProceed()) {
    submitError.value = "Проверьте обязательные поля на предыдущих шагах."
    clearStatusAfter()
    return
  }

  const payload = {
    title: formData.title.trim(),
    category: formData.category,
    description: formData.description.trim(),
    skills: formData.skills.slice(),
    budget_type: formData.budgetType,
    budget_fixed: formData.budgetType === "fixed" ? Number(formData.budgetFixed) : null,
    budget_min:    formData.budgetType === "range" ? Number(formData.budgetMin) : null,
    budget_max:    formData.budgetType === "range" ? Number(formData.budgetMax) : null,
    deadline: formData.deadline.trim(),
    deadline_type: formData.deadlineType,
    location: formData.location.trim(),
    remote: !!formData.remote,
    urgent: !!formData.urgent,
  }

  submitting.value = true
  try {
    // 1) Создание задания
    const createResp = await authedFetch(`${baseURL}/api/jobs/`, {
      method: "POST",
      body: JSON.stringify(payload),
    })

    if (!createResp.ok) {
      let data = null
      try { data = await createResp.json() } catch {}
      if (createResp.status === 403) {
        submitError.value = data?.detail || "Недостаточно прав для создания задания."
      } else if (createResp.status === 400 && data) {
        const firstKey = Object.keys(data)[0]
        submitError.value = (typeof data[firstKey] === "string")
          ? data[firstKey]
          : Array.isArray(data[firstKey]) ? data[firstKey].join(" ") : "Проверьте заполнение полей."
      } else {
        submitError.value = "Не удалось создать задание. Попробуйте позже."
      }
      clearStatusAfter()
      return
    }

    const created = await createResp.json()
    createdJobId.value = created?.id

    // 2) Вложения (если есть)
    if (createdJobId.value && formData.attachments.length > 0) {
      const fd = new FormData()
      for (const f of formData.attachments) fd.append("attachments", f)

      const attResp = await authedFetch(`${baseURL}/api/jobs/${createdJobId.value}/attachments/`, {
        method: "POST",
        body: fd,
      })

      if (!attResp.ok) {
        let detail = "Файлы не удалось загрузить."
        try { const j = await attResp.json(); detail = j?.detail || detail } catch {}
        submitError.value = detail + " Задание создано без вложений."
        clearStatusAfter()
      }
    }

    submitSuccess.value = true
    clearStatusAfter()
    resetForm()
    currentStep.value = 4
  } catch (e) {
    console.error(e)
    submitError.value = "Ошибка сети. Проверьте соединение."
    clearStatusAfter()
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  formData.title = ""
  formData.category = ""
  formData.description = ""
  formData.skills = []
  formData.budgetType = "fixed"
  formData.budgetFixed = ""
  formData.budgetMin = ""
  formData.budgetMax = ""
  formData.deadline = ""
  formData.deadlineType = "flexible"
  formData.location = ""
  formData.remote = true
  formData.urgent = false
  formData.attachments = []
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <!-- Заголовок + прогресс -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Разместить задание</h1>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          Шаг {{ currentStep }} из {{ totalSteps }}
        </div>
      </div>
      <div class="h-2 w-full bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
        <div class="h-full bg-indigo-600 transition-all" :style="{ width: progress + '%' }" />
      </div>
    </div>

    <div class="grid lg:grid-cols-3 gap-8">
      <!-- Навигация по шагам -->
      <div class="lg:col-span-1">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-800">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Этапы создания</h3>
          </div>

          <div class="p-5 space-y-3">
            <div :class="['flex items-center gap-3 p-3 rounded-lg', currentStep >= 1 ? 'bg-indigo-50 dark:bg-indigo-900/20' : '']">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                           currentStep >= 1 ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-500']">1</div>
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Основная информация</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Название и описание</div>
              </div>
            </div>

            <div :class="['flex items-center gap-3 p-3 rounded-lg', currentStep >= 2 ? 'bg-indigo-50 dark:bg-indigo-900/20' : '']">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                           currentStep >= 2 ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-500']">2</div>
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Навыки</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Требуемые технологии</div>
              </div>
            </div>

            <div :class="['flex items-center gap-3 p-3 rounded-lg', currentStep >= 3 ? 'bg-indigo-50 dark:bg-indigo-900/20' : '']">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                           currentStep >= 3 ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-500']">3</div>
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Бюджет и сроки</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Оплата и дедлайны</div>
              </div>
            </div>

            <div :class="['flex items-center gap-3 p-3 rounded-lg', currentStep >= 4 ? 'bg-indigo-50 dark:bg-indigo-900/20' : '']">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                           currentStep >= 4 ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-500']">4</div>
              <div>
                <div class="font-medium text-gray-900 dark:text-white">Публикация</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">Проверка и размещение</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Контент шагов -->
      <div class="lg:col-span-2">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm">
          <div class="p-6">
            <!-- ШАГ 1 -->
            <div v-if="currentStep === 1" class="space-y-6">
              <div>
                <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Основная информация</h2>
                <p class="text-gray-500 dark:text-gray-400">Расскажите о вашем проекте</p>
              </div>

              <div class="space-y-2">
                <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Название задания *</label>
                <input
                  id="title"
                  type="text"
                  placeholder="Например: Разработка интернет-магазина на Vue"
                  :value="formData.title"
                  @input="updateFormData('title', $event.target.value)"
                  class="text-lg w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                         px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <p class="text-sm text-gray-500 dark:text-gray-400">Чётко опишите, что нужно сделать</p>
              </div>

              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Категория *</label>
                <select
                  :value="formData.category"
                  @change="updateFormData('category', $event.target.value)"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                         px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                >
                  <option value="" disabled>Выберите категорию</option>
                  <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>

              <div class="space-y-2">
                <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Подробное описание *</label>
                <textarea
                  id="description"
                  rows="8"
                  placeholder="Опишите детали проекта, требования, ожидания…"
                  :value="formData.description"
                  @input="updateFormData('description', $event.target.value)"
                  class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                         px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                />
                <p class="text-sm text-gray-500 dark:text-gray-400">Минимум 100 символов — детальнее → лучше отклики</p>
              </div>
            </div>

            <!-- ШАГ 2 -->
            <div v-else-if="currentStep === 2" class="space-y-6">
              <div>
                <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Необходимые навыки</h2>
                <p class="text-gray-500 dark:text-gray-400">Укажите технологии и навыки</p>
              </div>

              <div class="space-y-4">
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Добавить навык</label>
                  <div class="flex gap-2">
                    <input
                      type="text"
                      placeholder="Введите навык"
                      v-model="newSkill"
                      @keypress.enter.prevent="addSkill(newSkill)"
                      class="flex-1 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                             px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                    />
                    <button
                      type="button"
                      @click="addSkill(newSkill)"
                      :disabled="!newSkill.trim()"
                      class="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium disabled:opacity-60"
                    >
                      + Добавить
                    </button>
                  </div>
                </div>

                <div v-if="formData.skills.length" class="space-y-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Выбранные навыки ({{ formData.skills.length }})
                  </label>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="s in formData.skills"
                      :key="s"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-sm bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200"
                    >
                      {{ s }}
                      <button
                        type="button"
                        @click="removeSkill(s)"
                        class="ml-1 rounded p-1 hover:bg-gray-200 dark:hover:bg-gray-700"
                        aria-label="Удалить навык"
                      >
                        ×
                      </button>
                    </span>
                  </div>
                </div>

                <hr class="border-gray-200 dark:border-gray-800" />

                <div class="space-y-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Популярные навыки</label>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="s in popularSkills.filter(x => !formData.skills.includes(x)).slice(0, 15)"
                      :key="s"
                      type="button"
                      @click="addSkill(s)"
                      class="px-2.5 py-1.5 rounded-md border text-xs border-gray-300 dark:border-gray-700
                             text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      + {{ s }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- ШАГ 3 -->
            <div v-else-if="currentStep === 3" class="space-y-6">
              <div>
                <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Бюджет и сроки</h2>
                <p class="text-gray-500 dark:text-gray-400">Укажите оплату и временные рамки</p>
              </div>

              <div class="space-y-4">
                <!-- Тип бюджета -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Тип бюджета</label>
                  <div class="flex items-center gap-6">
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="radio" value="fixed" v-model="formData.budgetType" class="accent-indigo-600" />
                      Фиксированная сумма
                    </label>
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="radio" value="range" v-model="formData.budgetType" class="accent-indigo-600" />
                      Диапазон
                    </label>
                  </div>
                </div>

                <!-- Бюджет -->
                <div v-if="formData.budgetType === 'fixed'" class="space-y-2">
                  <label for="budgetFixed" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Бюджет (₽) *</label>
                  <div class="relative">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₽</span>
                    <input
                      id="budgetFixed"
                      type="number"
                      placeholder="50000"
                      :value="formData.budgetFixed"
                      @input="updateFormData('budgetFixed', $event.target.value)"
                      class="pl-8 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                             px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                    />
                  </div>
                </div>

                <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="space-y-2">
                    <label for="budgetMin" class="block text-sm font-medium text-gray-700 dark:text-gray-300">От (₽) *</label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₽</span>
                      <input
                        id="budgetMin"
                        type="number"
                        placeholder="30000"
                        :value="formData.budgetMin"
                        @input="updateFormData('budgetMin', $event.target.value)"
                        class="pl-8 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                               px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                      />
                    </div>
                  </div>
                  <div class="space-y-2">
                    <label for="budgetMax" class="block text-sm font-medium text-gray-700 dark:text-gray-300">До (₽) *</label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₽</span>
                      <input
                        id="budgetMax"
                        type="number"
                        placeholder="80000"
                        :value="formData.budgetMax"
                        @input="updateFormData('budgetMax', $event.target.value)"
                        class="pl-8 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                               px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                      />
                    </div>
                  </div>
                </div>

                <!-- Дедлайн -->
                <div class="space-y-2">
                  <label for="deadline" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Срок выполнения *</label>
                  <div class="relative">
                    <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 2v3M16 2v3M3 9h18M4 7h16a1 1 0 0 1 1 1v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a1 1 0 0 1 1-1z"/>
                    </svg>
                    <input
                      id="deadline"
                      type="text"
                      placeholder="Например: 2 недели, 1 месяц, до 15 февраля"
                      :value="formData.deadline"
                      @input="updateFormData('deadline', $event.target.value)"
                      class="pl-9 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                             px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                    />
                  </div>
                </div>

                <!-- Тип дедлайна -->
                <div class="space-y-2">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Тип дедлайна</label>
                  <div class="flex items-center gap-6">
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="radio" value="flexible" v-model="formData.deadlineType" class="accent-indigo-600" />
                      Гибкий (можно обсудить)
                    </label>
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="radio" value="strict" v-model="formData.deadlineType" class="accent-indigo-600" />
                      Строгий (не подлежит изменению)
                    </label>
                  </div>
                </div>

                <hr class="border-gray-200 dark:border-gray-800" />

                <!-- Прочее -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="space-y-2">
                    <label for="location" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Местоположение</label>
                    <input
                      id="location"
                      type="text"
                      placeholder="Москва, Санкт-Петербург или Удаленно"
                      :value="formData.location"
                      @input="updateFormData('location', $event.target.value)"
                      class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800
                             px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600"
                    />
                  </div>

                  <div class="space-y-3">
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="checkbox" v-model="formData.remote" class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-600">
                      Возможна удаленная работа
                    </label>
                    <label class="inline-flex items-center gap-2 text-sm">
                      <input type="checkbox" v-model="formData.urgent" class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-600">
                      Срочное задание
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- ШАГ 4 -->
            <div v-else-if="currentStep === 4" class="space-y-6">
              <div>
                <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Проверка и публикация</h2>
                <p class="text-gray-500 dark:text-gray-400">Убедитесь, что все данные указаны верно</p>
              </div>

              <!-- Статус отправки -->
              <div v-if="submitting || submitSuccess || submitError" class="rounded-lg p-3"
                   :class="submitting ? 'bg-indigo-50 dark:bg-indigo-900/20' : (submitSuccess ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20')">
                <p class="text-sm"
                   :class="submitting ? 'text-indigo-700 dark:text-indigo-200' : (submitSuccess ? 'text-green-700 dark:text-green-200' : 'text-red-700 dark:text-red-200')">
                  <template v-if="submitting">Отправляем…</template>
                  <template v-else-if="submitSuccess">Готово! Задание опубликовано<span v-if="createdJobId"> (ID: {{ createdJobId }})</span>.</template>
                  <template v-else>{{ submitError }}</template>
                </p>
              </div>

              <div class="space-y-6">
                <!-- Загрузка файлов -->
                <div class="space-y-4">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Дополнительные файлы (необязательно)</label>

                  <div class="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-6 text-center">
                    <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5-5 5 5M12 5v9"/>
                    </svg>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      Перетащите файлы сюда или нажмите для выбора
                    </p>

                    <input
                      ref="fileInputRef"
                      type="file"
                      multiple
                      class="hidden"
                      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
                      @change="handleFileUpload"
                    />
                    <button
                      type="button"
                      @click="openFileDialog"
                      class="inline-flex items-center gap-2 px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700
                             text-sm text-gray-800 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      Выбрать файлы
                    </button>
                  </div>

                  <div v-if="formData.attachments.length" class="space-y-2">
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Прикрепленные файлы ({{ formData.attachments.length }})
                    </label>
                    <div class="space-y-2">
                      <div
                        v-for="(file, idx) in formData.attachments"
                        :key="idx"
                        class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded"
                      >
                        <span class="text-sm text-gray-700 dark:text-gray-200 truncate max-w-[70%]">{{ file.name }}</span>
                        <button
                          type="button"
                          @click="removeFile(idx)"
                          class="px-2 py-1 rounded text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10"
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <hr class="border-gray-200 dark:border-gray-800" />

                <!-- Превью -->
                <div class="space-y-3">
                  <div class="flex items-center gap-2">
                    <svg class="w-5 h-5 text-gray-700 dark:text-gray-200" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    <span class="text-lg font-medium text-gray-900 dark:text-white">Предварительный просмотр</span>
                  </div>

                  <div class="rounded-xl border-2 border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
                    <div class="p-5 border-b border-gray-200 dark:border-gray-800">
                      <div class="flex items-start justify-between">
                        <div class="flex-1">
                          <div class="flex items-center gap-2 mb-2">
                            <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
                              {{ formData.title || "Название задания" }}
                            </h3>
                            <span
                              v-if="formData.urgent"
                              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"
                            >
                              Срочно
                            </span>
                          </div>
                          <div class="text-sm text-gray-500 dark:text-gray-400">
                            {{ formData.category || "Категория" }} • {{ formData.location || "Локация не указана" }} •
                            {{ formData.deadline || "Срок не указан" }}
                          </div>
                        </div>

                        <div class="text-right">
                          <div class="text-2xl font-bold text-indigo-600">
                            <template v-if="formData.budgetType === 'fixed'">
                              {{ formData.budgetFixed || '0' }} ₽
                            </template>
                            <template v-else>
                              {{ formData.budgetMin || '0' }} – {{ formData.budgetMax || '0' }} ₽
                            </template>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="p-5">
                      <p class="text-sm text-gray-700 dark:text-gray-300 mb-4">
                        {{ formData.description || "Описание задания…" }}
                      </p>

                      <div v-if="formData.skills.length" class="flex flex-wrap gap-2">
                        <span
                          v-for="s in formData.skills"
                          :key="s"
                          class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                        >
                          {{ s }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- ЕДИНАЯ НАВИГАЦИЯ ДЛЯ ВСЕХ ШАГОВ -->
            <div class="flex items-center justify-between pt-6 mt-6 border-t border-gray-200 dark:border-gray-800">
              <button
                type="button"
                @click="prevStep"
                :disabled="currentStep === 1"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700
                       text-sm text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900
                       hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
              >
                ← Назад
              </button>

              <template v-if="currentStep < totalSteps">
                <button
                  type="button"
                  @click="nextStep"
                  :disabled="!canProceed()"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-indigo-600 text-white text-sm font-medium
                         hover:bg-indigo-700 disabled:opacity-60"
                >
                  Далее →
                </button>
              </template>
              <template v-else>
                <button
                  type="button"
                  @click="handleSubmit"
                  :disabled="submitting"
                  :class="[
                    'inline-flex items-center gap-2 px-5 py-3 rounded-full text-white font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed',
                    'min-w-[220px] h-12',
                    submitting ? 'bg-indigo-500' : (submitSuccess ? 'bg-green-600 hover:bg-green-700' : (submitError ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'))
                  ]"
                >
                  <svg v-if="submitting" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="9" stroke-width="1.5" class="opacity-25"/>
                    <path d="M12 3a9 9 0 0 1 9 9" stroke-width="1.5"/>
                  </svg>
                  <template v-else-if="submitSuccess">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                    </svg>
                    <span>Опубликовано</span>
                  </template>
                  <template v-else-if="submitError">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                    <span>Ошибка</span>
                  </template>
                  <template v-else>
                    <span>Опубликовать задание →</span>
                  </template>
                </button>
              </template>
            </div>
            <!-- /ЕДИНАЯ НАВИГАЦИЯ -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
