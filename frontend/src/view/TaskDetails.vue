<template>
  <div class="mx-auto max-w-6xl">
    <!-- HERO / HEADER -->
    <header
      class="rounded-2xl border bg-gradient-to-br from-white/85 to-white/40 
             dark:from-slate-900/70 dark:to-slate-900/30 backdrop-blur 
             p-4 sm:p-6 ring-1 ring-black/5 dark:ring-white/10 shadow-sm"
    >
      <div class="mb-4 flex items-center justify-between">
        <!-- Назад (подсвеченная) -->
        <button
          class="btn-back inline-flex items-center gap-2"
          @click="goBack"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Назад
        </button>
        <!-- Справа ничего лишнего -->
      </div>

      <!-- Заголовок, статус и цена -->
      <div class="flex flex-col gap-3">
        <h1 class="truncate text-2xl sm:text-3xl font-bold tracking-tight">
          {{ task?.title || 'Загрузка…' }}
        </h1>

        <div class="flex flex-wrap items-center gap-2">
          <span :class="['status-chip', statusMeta.cls]">{{ statusMeta.label }}</span>
          <span v-if="task?.category" class="chip">{{ task.category }}</span>
          <span v-if="task?.remote" class="chip">Удалённо</span>
          <span v-if="task?.urgent" class="chip warn">Срочно</span>

          <!-- Бюджет — сразу в шапке, хорошо заметный -->
          <span v-if="hasBudget" class="price-badge" :title="budgetDisplay.title">
            {{ budgetDisplay.value }}
          </span>
        </div>
      </div>
    </header>

    <!-- LOADING -->
    <section v-if="loading" class="mt-6 grid gap-6 md:grid-cols-3">
      <div class="md:col-span-2 space-y-3">
        <div class="h-7 w-1/2 animate-pulse rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-32 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-48 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700"></div>
      </div>
      <div class="space-y-3">
        <div class="h-7 w-1/2 animate-pulse rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-56 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700"></div>
      </div>
    </section>

    <!-- ERROR -->
    <section v-else-if="error" class="mt-6 rounded-2xl border border-rose-200 bg-rose-50/80 p-4 text-rose-700 dark:border-rose-400/25 dark:bg-rose-500/10 dark:text-rose-200">
      <div class="font-semibold">Не удалось загрузить задание</div>
      <div class="text-sm opacity-90">{{ error }}</div>
      <button class="btn-danger mt-3" @click="fetchTask">Повторить</button>
    </section>

    <!-- CONTENT -->
    <section v-else-if="task" class="mt-6 grid gap-6 md:grid-cols-3">
      <!-- LEFT -->
      <div class="space-y-6 md:col-span-2">
        <!-- Описание -->
        <section class="card">
          <h2 class="card-title">Описание</h2>
          <p class="whitespace-pre-line leading-relaxed text-slate-800 dark:text-slate-200">{{ task.description || '—' }}</p>
        </section>

        <!-- Навыки и категории -->
        <section class="card">
          <h2 class="card-title">Навыки и категории</h2>
          <div class="flex flex-wrap gap-2">
            <span v-for="(cat, i) in task.categories || []" :key="'cat-'+i" class="tag">{{ cat }}</span>
            <span v-for="(skill, i) in task.skills || []" :key="'sk-'+i" class="tag">{{ skill }}</span>
            <span v-if="emptyTags" class="text-sm text-slate-500">—</span>
          </div>
        </section>

        <!-- Вложения / Галерея -->
        <section class="card">
          <h2 class="card-title">Вложения</h2>
          <div v-if="task.attachments && task.attachments.length" class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="file in task.attachments" :key="file.id" class="overflow-hidden rounded-xl border dark:border-slate-700/60">
              <a :href="file.url" target="_blank" rel="noopener" class="block">
                <img v-if="isImage(file.url)" :src="file.url" :alt="file.name" class="h-40 w-full object-cover"/>
                <div v-else class="flex h-40 items-center justify-center text-sm text-slate-500">
                  {{ file.name }}
                </div>
              </a>
              <div class="border-t p-2 text-xs text-slate-600 dark:text-slate-400 truncate">{{ file.name }}</div>
            </div>
          </div>
          <p v-else class="text-sm text-slate-500">Нет вложений</p>
        </section>
      </div>

      <!-- RIGHT -->
      <aside class="space-y-6">
        <!-- Бюджет (повтор, более подробно) -->
        <section class="card">
          <h3 class="card-title">Бюджет</h3>
          <div class="stat">
            <div class="stat-label">{{ budgetDisplay.title }}</div>
            <div class="stat-value">{{ hasBudget ? budgetDisplay.value : '—' }}</div>
            <div v-if="task.deadline_text" class="stat-hint">Дедлайн: {{ task.deadline_text }} ({{ dlType }})</div>
          </div>
        </section>

        <!-- Детали -->
        <section class="card text-sm">
          <h3 class="card-title">Детали</h3>
          <dl class="space-y-2">
            <div class="row"><dt>Создано</dt><dd>{{ formatDate(task.created_at) }}</dd></div>
            <div class="row"><dt>Обновлено</dt><dd>{{ formatDate(task.updated_at) }}</dd></div>
            <div class="row" v-if="task.location"><dt>Локация</dt><dd>{{ task.location }}</dd></div>
            <div class="row" v-if="task.executor"><dt>Исполнитель</dt><dd>{{ task.executor?.full_name || '—' }}</dd></div>
            <div class="row" v-if="task.canceled_at"><dt>Отменено</dt><dd>{{ formatDate(task.canceled_at) }}</dd></div>
            <div class="row" v-if="task.canceled_reason"><dt>Причина</dt><dd class="truncate" :title="task.canceled_reason">{{ task.canceled_reason }}</dd></div>
          </dl>
        </section>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'

/* API base */
const API_BASE = (import.meta?.env?.VITE_API_BASE || 'http://127.0.0.1:8000').replace(/\/$/, '')

/* Route & store */
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/* Status palette (synced) */
const STATUS_META = {
  pending: {
    label: 'Активно',
    cls: 'bg-amber-50 dark:bg-amber-500/15 text-amber-700 dark:text-amber-300 ring-1 ring-amber-200/70 dark:ring-amber-400/30'
  },
  in_progress: {
    label: 'В работе',
    cls: 'bg-indigo-50 dark:bg-indigo-500/15 text-indigo-700 dark:text-indigo-300 ring-1 ring-indigo-200/70 dark:ring-indigo-400/30'
  },
  completed: {
    label: 'Завершён',
    cls: 'bg-emerald-50 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 ring-1 ring-emerald-200/70 dark:ring-emerald-400/30'
  },
  canceled_by_executor: {
    label: 'Отменён исполнителем',
    cls: 'bg-rose-50 dark:bg-rose-500/15 text-rose-700 dark:text-rose-300 ring-1 ring-rose-200/70 dark:ring-rose-400/30'
  },
  canceled_by_customer: {
    label: 'Архив',
    cls: 'bg-slate-50 dark:bg-slate-500/15 text-slate-700 dark:text-slate-300 ring-1 ring-slate-200/70 dark:ring-slate-400/30'
  }
}

/* State */
const task = ref(null)
const loading = ref(false)
const error = ref('')

/* Derived */
const statusMeta = computed(() => STATUS_META[task.value?.status] || { label: '—', cls: 'bg-slate-100 text-slate-700 ring-1 ring-slate-200 dark:bg-slate-800/50 dark:text-slate-200' })
const isOwner = computed(() => {
  const uid = userStore?.user?.id
  return uid && task.value?.owner_id === uid
})
const canEdit = computed(() => ['pending', 'in_progress'].includes(task.value?.status)) // оставил на будущее, но кнопки убраны

/* Бюджет: фикс или диапазон (с валютой) */
const hasBudget = computed(() => {
  const t = task.value
  if (!t) return false
  if (t.budget_type === 'fixed') return isFinite(+t.budget_fixed)
  return isFinite(+t.budget_min) || isFinite(+t.budget_max)
})
const budgetDisplay = computed(() => {
  const cur = task.value?.budget_currency || 'RUB'
  const type = task.value?.budget_type
  if (type === 'fixed') {
    const v = task.value?.budget_fixed
    return { title: 'Фиксированная цена', value: formatMoney(v, cur) }
  }
  const min = task.value?.budget_min
  const max = task.value?.budget_max
  let value = '—'
  if (isFinite(+min) && isFinite(+max)) value = `от {{}} до {{}}`.replace('{{}}', formatMoney(min, cur)).replace('{{}}', formatMoney(max, cur))
  else if (isFinite(+min)) value = `от ${formatMoney(min, cur)}`
  else if (isFinite(+max)) value = `до ${formatMoney(max, cur)}`
  return { title: 'Диапазон', value }
})

const dlType = computed(() => {
  switch (task.value?.deadline_type) {
    case 'flexible': return 'гибкий'
    case 'strict': return 'жёсткий'
    default: return '—'
  }
})
const emptyTags = computed(() => !((task.value?.categories?.length || 0) + (task.value?.skills?.length || 0)))

/* Utils */
const getId = () => String(route.params?.id || route.query?.id || '')
const isImage = (url='') => /\.(png|jpe?g|gif|webp|avif)$/i.test(url)
const makeAbs = (u) => {
  if (!u) return ''
  if (/^https?:\/\//i.test(u)) return u
  return `${API_BASE}${u.startsWith('/') ? '' : '/'}${u}`
}

function formatMoney (amount, currency = 'RUB') {
  if (amount == null || isNaN(Number(amount))) return '—'
  try { return new Intl.NumberFormat('ru-RU', { style: 'currency', currency, maximumFractionDigits: 0 }).format(Number(amount)) }
  catch { return `${Number(amount).toLocaleString('ru-RU')} ${currency}` }
}

function formatDate (value) {
  if (!value) return '—'
  try { return new Date(value).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
  catch { return String(value) }
}

/* Fetch */
async function fetchTask () {
  const id = getId()
  if (!id) { error.value = 'Не передан идентификатор задания.'; return }
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/jobs/${id}/`, {
      headers: { 'Accept': 'application/json', ...(userStore?.access ? { Authorization: `Bearer ${userStore.access}` } : {}) },
      credentials: 'include'
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    task.value = {
      id: data.id,
      title: data.title,
      description: data.description,
      status: data.status || (data.is_active ? 'pending' : 'canceled_by_customer'),
      category: data.category || null,
      categories: data.categories || (data.category ? [data.category] : []),
      skills: data.skills || [],
      attachments: (data.attachments || []).map(f => ({
        id: f.id,
        name: f.name || 'файл',
        url: makeAbs(f.url),
        uploaded_at: f.uploaded_at || null,
        size: f.size ?? null
      })),
      budget_type: data.budget_type || null,
      budget_fixed: data.budget_fixed ?? null,
      budget_min: data.budget_min ?? null,
      budget_max: data.budget_max ?? null,
      budget_currency: data.budget_currency || 'RUB',
      deadline_text: data.deadline || null,
      deadline_type: data.deadline_type || null,
      location: data.location || null,
      remote: !!data.remote,
      urgent: !!data.urgent,
      created_at: data.created_at || data.created,
      updated_at: data.updated_at || data.updated,
      owner_id: data.owner ?? data.customer?.id ?? null,
      executor: data.executor || null,
      canceled_at: data.canceled_at || null,
      canceled_reason: data.canceled_reason || ''
    }
  } catch (e) {
    error.value = e?.message || 'Ошибка сети'
  } finally { loading.value = false }
}

/* Navigation */
function goBack () { if (window.history.length > 1) router.back(); else router.push({ name: 'MyAssignments' }) }

onMounted(fetchTask)
watch(() => route.params.id, fetchTask)
</script>

<style scoped>
/* Chips */
.chip { @apply inline-flex items-center rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-900/60 px-2.5 py-1 text-xs text-slate-700 dark:text-slate-200; }
.chip.warn { @apply border-amber-300/60 bg-amber-50/80 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300; }
.status-chip { @apply inline-flex items-center gap-2 rounded-xl px-3 py-1.5 text-sm font-medium ring-1; }

/* Price in header */
.price-badge {
  @apply inline-flex items-center rounded-2xl px-3 py-1.5 text-sm font-semibold
         border border-emerald-300/70 dark:border-emerald-400/30
         bg-emerald-50/80 dark:bg-emerald-500/10
         text-emerald-700 dark:text-emerald-300;
}

/* Buttons */
.btn-back {
  @apply rounded-xl px-3 py-2 text-sm
         border border-indigo-300/60 dark:border-indigo-400/30
         bg-indigo-50/70 dark:bg-indigo-500/10
         text-indigo-700 dark:text-indigo-300
         shadow-[0_0_0_0_rgba(99,102,241,0.0)]
         hover:shadow-[0_0_0_4px_rgba(99,102,241,0.12)]
         transition;
}
.btn-danger { @apply rounded-xl bg-rose-600 px-3 py-2 text-sm text-white hover:bg-rose-700 transition; }

/* Cards / layout */
.card { @apply rounded-2xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-slate-900/60 p-4 sm:p-5 shadow-sm; }
.card-title { @apply mb-3 text-lg font-semibold; }
.row { @apply flex items-center justify-between gap-3; }
.tag { @apply rounded-full border border-slate-200 dark:border-white/10 px-3 py-1 text-xs; }

/* Stat tiles */
.stat { @apply rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/70 dark:bg-slate-900/60 p-3 shadow-sm; }
.stat-label { @apply text-xs uppercase tracking-wide text-slate-500; }
.stat-value { @apply text-xl font-semibold; }
.stat-hint { @apply text-xs text-slate-500 mt-0.5; }
</style>
