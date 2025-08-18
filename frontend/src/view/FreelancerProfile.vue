<!-- src/view/FreelancerProfile.vue -->
<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useUserStore } from "@/store/userStore.js" // проверь путь/регистр файла

const userStore = useUserStore()

/* ===== Read-only из регистрации ===== */
const requiredFields = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
})

/* ===== Форма анкеты ===== */
const form = reactive({
  title: "",
  bio: "",
  location: "",
  gender: "",
  education: "",
  status: "",
  categories: [],
  skills: [],
  newSkill: "",

  rateType: "hour",
  hourlyRate: null,
  projectRate: null,
  availability: true,

  links: [
    { label: "Сайт", url: "" },
    { label: "GitHub", url: "" },
    { label: "Behance", url: "" },
    { label: "Dribbble", url: "" },
  ],
  socials: { telegram: "", linkedin: "" },

  portfolio: [{ title: "", url: "" }],

  // календарь занятости (массив ISO дат)
  busyDates: new Set(), // Set<string: 'YYYY-MM-DD'>
})

/* ===== Справочники ===== */
const educationOptions = [
  "Среднее",
  "Среднее профессиональное",
  "Незаконченное высшее",
  "Высшее",
  "Магистратура/Аспирантура",
]
const statusOptions = [
  { value: "open", label: "Открыт к проектам" },
  { value: "partial", label: "Частично занят" },
  { value: "busy", label: "Не доступен" },
]
const genderOptions = ["Мужской", "Женский", "Не указывать"]
const categoryOptions = [
  "Веб-разработка",
  "Мобильные приложения",
  "Дизайн",
  "Копирайтинг",
  "SEO и маркетинг",
  "Переводы",
]

/* ===== Аватар ===== */
const avatarFile = ref(null)
const avatarPreview = ref("")
function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = (ev) => (avatarPreview.value = ev.target?.result || "")
  reader.readAsDataURL(file)
}

/* ===== Навыки / Портфолио / Ссылки ===== */
function addSkill() {
  const v = form.newSkill.trim()
  if (!v) return
  if (!form.skills.includes(v)) form.skills.push(v)
  form.newSkill = ""
}
function removeSkill(s) { form.skills = form.skills.filter(x => x !== s) }
function addPortfolioRow() { form.portfolio.push({ title: "", url: "" }) }
function removePortfolioRow(i) { if (form.portfolio.length > 1) form.portfolio.splice(i, 1) }
function toggleCategory(cat) {
  const i = form.categories.indexOf(cat)
  if (i >= 0) form.categories.splice(i, 1)
  else form.categories.push(cat)
}

/* ===== Секции (сворачивание/раскрытие) ===== */
const openSkills = ref(true)
const openPayment = ref(true)
const openLinks = ref(true)
const openPortfolio = ref(true)
const openCalendar = ref(true)

/* ===== Оплата ===== */
const rateLabel = computed(() =>
  form.rateType === "hour" ? "Ставка (₽/час)" : "Ставка (₽/проект)"
)

/* ===== Валидация ===== */
const errors = reactive({ rate: "", title: "", bio: "" })
function validate() {
  errors.rate = errors.title = errors.bio = ""
  if (form.rateType === "hour" && (!form.hourlyRate || form.hourlyRate <= 0)) {
    errors.rate = "Укажи корректную почасовую ставку"
  }
  if (form.rateType === "project" && (!form.projectRate || form.projectRate <= 0)) {
    errors.rate = "Укажи корректную ставку за проект"
  }
  if (!form.title.trim()) errors.title = "Укажи заголовок профиля"
  if (!form.bio.trim()) errors.bio = "Расскажи кратко о себе"
  return !errors.rate && !errors.title && !errors.bio
}

/* ===== Календарь занятости ===== */
const today = new Date()
const calYear = ref(today.getFullYear())
const calMonth = ref(today.getMonth()) // 0-11
const weekDays = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]

function ymToLabel(y, m) {
  return new Date(y, m).toLocaleString("ru-RU", { month: "long", year: "numeric" })
}
const calLabel = computed(() => ymToLabel(calYear.value, calMonth.value))

function daysMatrix(y, m) {
  const first = new Date(y, m, 1)
  const last = new Date(y, m + 1, 0)
  // В JS неделя начинается с Вск, нам нужна Пн..Вс: сдвиг
  const startOffset = (first.getDay() + 6) % 7 // 0 для Пн
  const total = last.getDate()
  const cells = []
  for (let i = 0; i < startOffset; i++) cells.push(null) // предыдущие пустые
  for (let d = 1; d <= total; d++) cells.push(new Date(y, m, d)) // текущий месяц
  while (cells.length % 7 !== 0) cells.push(null) // добиваем до кратного 7
  return cells
}
const calCells = computed(() => daysMatrix(calYear.value, calMonth.value))

function shiftMonth(delta) {
  let y = calYear.value, m = calMonth.value + delta
  if (m < 0) { m = 11; y-- }
  if (m > 11) { m = 0; y++ }
  calYear.value = y; calMonth.value = m
}
function fmtISO(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `${y}-${m}-${day}`
}
function isBusy(d) { return form.busyDates.has(fmtISO(d)) }
function toggleBusy(d) {
  const key = fmtISO(d)
  if (form.busyDates.has(key)) form.busyDates.delete(key)
  else form.busyDates.add(key)
}
function clearBusy() { form.busyDates.clear() }

/* ===== Загрузка из Pinia ===== */
onMounted(async () => {
  if (!userStore.user) {
    try { await userStore.fetchProfile?.() } catch {}
  }
  if (userStore.user) {
    const u = userStore.user

    // опционально: красивое отображение телефона
    const prettyPhone = (p) =>
      (p || "").replace(/^(\+7)(\d{3})(\d{3})(\d{2})(\d{2})$/, "$1 $2 $3-$4-$5")

    requiredFields.first_name = u.first_name || ""
    requiredFields.last_name  = u.last_name  || ""
    requiredFields.email      = u.email      || ""
    requiredFields.phone      = prettyPhone(u.phone || "")   // ← добавлено

    form.title        = u.title || ""
    form.bio          = u.bio || ""
    form.location     = u.location || ""
    form.gender       = u.gender || ""
    form.education    = u.education || ""
    form.status       = u.status || "open"
    form.categories   = Array.isArray(u.categories) ? u.categories.slice() : []
    form.skills       = Array.isArray(u.skills) ? u.skills.slice() : []
    form.rateType     = u.rate_type || "hour"
    form.hourlyRate   = u.hourly_rate ?? null
    form.projectRate  = u.project_rate ?? null
    form.availability = u.availability ?? true
    form.links        = u.links?.length ? u.links.slice() : form.links
    form.socials.telegram = u.socials?.telegram || ""
    form.socials.linkedin = u.socials?.linkedin || ""
    form.portfolio    = u.portfolio?.length ? u.portfolio.slice() : form.portfolio

    if (Array.isArray(u.busy_dates)) {
      form.busyDates = new Set(u.busy_dates)
    }

    avatarPreview.value = u.avatar_url || ""
  }
})


/* ===== Сохранение ===== */
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref("")

async function onSave() {
  saveSuccess.value = false
  saveError.value = ""
  if (!validate()) return

  saving.value = true
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
      busy_dates: Array.from(form.busyDates), // <= календарь
    }

    // если есть экшн в сторе — используй его:
    await userStore.updateProfile(payload)

    // временно обновим локально:
    userStore.setUser?.({ ...(userStore.user || {}), ...payload, avatar_url: avatarPreview.value })
    saveSuccess.value = true
  } catch (e) {
    saveError.value = "Не удалось сохранить изменения. Попробуй ещё раз."
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="py-8 px-4">
    <div class="mx-auto max-w-5xl">
      <!-- Заголовок -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Анкета фрилансера</h1>
        <p class="text-gray-600 dark:text-gray-400">Обязательные поля недоступны для редактирования, остальное — заполни для повышения доверия и конверсии.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[280px,1fr] gap-6">
        <!-- Левая колонка -->
        <aside class="space-y-6">
          <!-- Аватар -->
          <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Аватар</h3>
            <div class="flex items-center gap-4">
              <div class="w-20 h-20 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <img v-if="avatarPreview" :src="avatarPreview" class="w-full h-full object-cover" alt="avatar" />
                <svg v-else viewBox="0 0 24 24" class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 20c0-4 4-6 8-6s8 2 8 6" stroke-linecap="round"/>
                </svg>
              </div>
              <label class="inline-flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
                Загрузить
                <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
              </label>
            </div>
          </div>

          <!-- Доступность -->
          <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Доступность</h3>
            <label class="flex items-center gap-3">
              <input type="checkbox" v-model="form.availability" class="rounded border-gray-300 dark:border-gray-700 text-indigo-600" />
              <span class="text-gray-800 dark:text-gray-200">Принимаю новые заказы</span>
            </label>
          </div>

          <!-- Календарь (collapsible — с ChevronIcon) -->
          <section class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <button @click="openCalendar = !openCalendar" class="w-full flex items-center justify-between px-5 py-4">
              <h3 class="font-semibold text-gray-900 dark:text-white">Календарь занятости</h3>
              <ChevronIcon :open="openCalendar" />
            </button>
            <div v-show="openCalendar" class="px-5 pb-5">
              <div class="flex items-center justify-between mb-3">
                <button class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800" @click="shiftMonth(-1)" aria-label="prev">
                  <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
                <div class="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">{{ calLabel }}</div>
                <button class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800" @click="shiftMonth(1)" aria-label="next">
                  <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>

              <div class="grid grid-cols-7 text-center text-xs text-gray-500 dark:text-gray-400 mb-1">
                <div v-for="w in weekDays" :key="w" class="py-1">{{ w }}</div>
              </div>

              <div class="grid grid-cols-7 gap-1">
                <div v-for="(cell, idx) in calCells" :key="idx">
                  <button
                    v-if="cell"
                    @click="toggleBusy(cell)"
                    class="w-full aspect-square rounded-md text-sm
                           border border-gray-200 dark:border-gray-800
                           hover:bg-gray-50 dark:hover:bg-gray-800
                           flex items-center justify-center"
                    :class="isBusy(cell) ? 'bg-rose-500 text-white hover:bg-rose-600' : 'bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200'"
                    :aria-pressed="isBusy(cell)"
                  >
                    {{ cell.getDate() }}
                  </button>
                  <div v-else class="w-full aspect-square"></div>
                </div>
              </div>

              <div class="mt-3 flex items-center justify-between text-sm">
                <div class="flex items-center gap-2">
                  <span class="inline-block w-4 h-4 rounded bg-rose-500"></span>
                  <span class="text-gray-600 dark:text-gray-300">Отмеченные дни — занят</span>
                </div>
                <button @click="clearBusy" class="px-3 py-1.5 rounded-md border text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                  Очистить
                </button>
              </div>
            </div>
          </section>
        </aside>

        <!-- Правая колонка -->
        <main class="space-y-6">
          <!-- Read-only поля -->
          <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Основные данные (из регистрации)</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Имя</label>
                <div class="relative">
                  <input :value="requiredFields.first_name" disabled class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                  <LockIcon />
                </div>
              </div>
              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Фамилия</label>
                <div class="relative">
                  <input :value="requiredFields.last_name" disabled class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                  <LockIcon />
                </div>
              </div>
             <!-- Email -->
<div class="sm:col-span-2">
  <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Email</label>
  <div class="relative">
    <input
      :value="requiredFields.email"
      disabled
      class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200"
    />
    <LockIcon />
  </div>
</div>

<!-- Телефон -->
<!-- Телефон -->
<div class="sm:col-span-2">
  <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Телефон</label>
  <div class="relative">
    <input
      :value="requiredFields.phone"
      disabled
      class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200"
    />
    <LockIcon />
  </div>
</div>


            </div>
          </div>

          <!-- Публичный профиль -->
          <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
            <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Публичный профиль</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="sm:col-span-2">
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Заголовок профиля *</label>
                <input v-model="form.title" placeholder="Например: Frontend-разработчик (Vue 3)" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                <p v-if="errors.title" class="mt-1 text-xs text-red-600">{{ errors.title }}</p>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Локация</label>
                <input v-model="form.location" placeholder="Город или «Удаленно»" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Пол</label>
                <select v-model="form.gender" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option value="">Не указывать</option>
                  <option v-for="g in genderOptions" :key="g" :value="g">{{ g }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Образование</label>
                <select v-model="form.education" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option value="">—</option>
                  <option v-for="e in educationOptions" :key="e" :value="e">{{ e }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Статус</label>
                <select v-model="form.status" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>

              <div class="sm:col-span-2">
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">О себе *</label>
                <textarea v-model="form.bio" rows="4" placeholder="Коротко о ключевой экспертизе, стек, фокус на результат..." class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600"></textarea>
                <p v-if="errors.bio" class="mt-1 text-xs text-red-600">{{ errors.bio }}</p>
              </div>
            </div>
          </div>

          <!-- Навыки и категории (collapsible) -->
          <section class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <button @click="openSkills = !openSkills" class="w-full flex items-center justify-between px-5 py-4">
              <h3 class="font-semibold text-gray-900 dark:text-white">Навыки и категории</h3>
              <ChevronIcon :open="openSkills" />
            </button>
            <div v-show="openSkills" class="px-5 pb-5 space-y-4">
              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">Навыки</label>
                <div class="flex gap-2 mb-3">
                  <input v-model="form.newSkill" @keyup.enter="addSkill" placeholder="Добавить навык и нажать Enter" class="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                  <button @click="addSkill" class="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700">Добавить</button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="s in form.skills" :key="s" class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                    {{ s }}
                    <button @click="removeSkill(s)" class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700" title="Удалить">
                      <svg viewBox="0 0 24 24" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 18 18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </button>
                  </span>
                </div>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">Категории</label>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                  <label v-for="cat in categoryOptions" :key="cat" class="flex items-center gap-2 p-2 rounded-lg border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
                    <input type="checkbox" :value="cat" :checked="form.categories.includes(cat)" @change="toggleCategory(cat)" class="rounded border-gray-300 dark:border-gray-700 text-indigo-600" />
                    <span class="text-sm text-gray-800 dark:text-gray-200">{{ cat }}</span>
                  </label>
                </div>
              </div>
            </div>
          </section>

          <!-- Оплата (collapsible) -->
          <section class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <button @click="openPayment = !openPayment" class="w-full flex items-center justify-between px-5 py-4">
              <h3 class="font-semibold text-gray-900 dark:text-white">Оплата</h3>
              <ChevronIcon :open="openPayment" />
            </button>
            <div v-show="openPayment" class="px-5 pb-5">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Тип</label>
                  <select v-model="form.rateType" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                    <option value="hour">Почасовая</option>
                    <option value="project">За проект</option>
                  </select>
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">{{ rateLabel }}</label>
                  <input v-if="form.rateType === 'hour'"
                         v-model.number="form.hourlyRate" type="number" min="0" step="50" placeholder="Например, 1500"
                         class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                  <input v-else
                         v-model.number="form.projectRate" type="number" min="0" step="500" placeholder="Например, 20000"
                         class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                  <p v-if="errors.rate" class="mt-1 text-xs text-red-600">{{ errors.rate }}</p>
                </div>
              </div>
            </div>
          </section>

        

          <!-- Портфолио (collapsible) -->
          <section class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <button @click="openPortfolio = !openPortfolio" class="w-full flex items-center justify-between px-5 py-4">
              <h3 class="font-semibold text-gray-900 dark:text-white">Портфолио</h3>
              <ChevronIcon :open="openPortfolio" />
            </button>
            <div v-show="openPortfolio" class="px-5 pb-5">
              <div class="flex items-center justify-between mb-4">
                <p class="text-sm text-gray-600 dark:text-gray-400">Добавляй ссылки на кейсы, GitHub-репозитории, деплои.</p>
                <button @click="addPortfolioRow" class="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700">Добавить</button>
              </div>
              <div class="space-y-3">
                <div v-for="(p, i) in form.portfolio" :key="'p-'+i" class="grid grid-cols-1 sm:grid-cols-[1fr,1fr,auto] gap-2">
                  <input v-model="p.title" placeholder="Заголовок/название проекта" class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                  <input v-model="p.url" placeholder="Ссылка (GitHub/Behance/деплой)" class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                  <button @click="removePortfolioRow(i)" class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">Удалить</button>
                </div>
              </div>
            </div>
          </section>

          <!-- Кнопки -->
          <div class="flex flex-col sm:flex-row items-center gap-3 justify-end">
            <p v-if="saveSuccess" class="text-green-600">Сохранено ✅</p>
            <p v-if="saveError" class="text-red-600">{{ saveError }}</p>
            <button :disabled="saving" @click="onSave"
                    class="inline-flex items-center gap-2 px-5 py-3 rounded-full bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-60">
              <svg v-if="saving" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="9" stroke-width="1.5" class="opacity-25"/>
                <path d="M12 3a9 9 0 0 1 9 9" stroke-width="1.5"/>
              </svg>
              Сохранить изменения
            </button>
          </div>
        </main>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  components: {
    /* маленькая иконка замка для readonly полей */
    LockIcon: {
      template: `
        <span class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="4" y="11" width="16" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>
          </svg>
        </span>`,
    },
    /* стрелка для сворачиваемых секций */
    ChevronIcon: {
      props: { open: { type: Boolean, default: true } },
      template: `
        <span class="inline-flex items-center justify-center w-6 h-6 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition"
              :class="open ? 'rotate-180' : ''" style="transform-origin:center;">
          <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>`,
    },
  },
}
</script>

<style scoped>
/* rely on Tailwind; вращение делаем через класс rotate-180 */
</style>

