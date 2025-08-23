<!-- src/pages/MyAssignments.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'

const router = useRouter()
const userStore = useUserStore()

/** База API */
const API_BASE = (import.meta?.env?.VITE_API_BASE || 'http://127.0.0.1:8000').replace(/\/$/, '')

/** Статусы и цвета (с чуть более выразительными стилями) */
const STATUS_META = {
  pending: {
    label: 'Активно',
    cls: 'bg-amber-50 dark:bg-amber-500/15 text-amber-700 dark:text-amber-300 ring-1 ring-amber-200/70 dark:ring-amber-400/30'
  },
  canceled_by_customer: {
    label: 'Архив',
    cls: 'bg-slate-50 dark:bg-slate-500/15 text-slate-700 dark:text-slate-300 ring-1 ring-slate-200/70 dark:ring-slate-400/30'
  },
}

const tabs = [
  { key: 'all', label: 'Все' },
  { key: 'pending', label: STATUS_META.pending.label },
  { key: 'canceled_by_customer', label: STATUS_META.canceled_by_customer.label },
]

/* Состояния */
const loading = ref(true)
const error = ref('')
const selectedTab = ref('all')
const search = ref('')
const sortBy = ref('created_desc')
const tasks = ref([])
const cancelingId = ref(null)

/* Утилиты */
async function parseJsonOrThrow(resp) {
  const ct = (resp.headers.get('content-type') || '').toLowerCase()
  if (ct.includes('application/json')) return await resp.json()
  const text = await resp.text().catch(() => '')
  const short = text.slice(0, 400).replace(/\s+/g, ' ').trim()
  throw new Error(`Ожидался JSON, но получен "${ct || 'неизвестный тип'}". Фрагмент: ${short}`)
}
const statusPill = (s) => STATUS_META[s] || { label: s, cls: 'bg-gray-50 text-gray-700 ring-1 ring-gray-200' }
const formatMoney = (v) => v == null ? '—'
  : new Intl.NumberFormat('ru-RU',{style:'currency',currency:'RUB',maximumFractionDigits:0}).format(v)
const formatDate = (dt) => dt ? new Intl.DateTimeFormat('ru-RU',{day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date(dt)) : '—'

/* Мапперы */
const deriveBudget = (job) => {
  if (job?.budget_type === 'fixed') return Number(job?.budget_fixed) || null
  const mn = Number(job?.budget_min) || 0
  const mx = Number(job?.budget_max) || 0
  if (mn > 0 && mx > 0) return Math.round((mn + mx) / 2)
  return null
}

/* Загрузка (с фильтром owner=me на сервере) */
async function fetchTasks() {
  loading.value = true
  error.value = ''
  try {
    const resp = await fetch(`${API_BASE}/api/jobs/?owner=me`, {
      headers: {
        Accept: 'application/json',
        ...(userStore.access ? { Authorization: `Bearer ${userStore.access}` } : {})
      }
    })
    if (!resp.ok) {
      const data = await parseJsonOrThrow(resp).catch(() => ({}))
      throw new Error(data?.detail || `Ошибка ${resp.status}`)
    }
    const data = await parseJsonOrThrow(resp)
    const items = Array.isArray(data) ? data : (data?.results || [])

    tasks.value = items.map(j => ({
      id: j.id,
      title: j.title,
      category: j.category || null,
      city: j.location || null,
      budget: deriveBudget(j),
      created_at: j.created_at || j.created,
      status: j.status || (j.is_active ? 'pending' : 'canceled_by_customer'),
      tools: Array.isArray(j.skills) ? j.skills.filter(Boolean) : [],
      canceled_reason: j.canceled_reason || '',
      canceled_at: j.canceled_at || null,
    }))
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)

/* Фильтрация/сортировка */
const filtered = computed(() => {
  let list = [...tasks.value]
  if (selectedTab.value !== 'all') list = list.filter(t => t.status === selectedTab.value)
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(t =>
      (t.title || '').toLowerCase().includes(q) ||
      (t.category || '').toLowerCase().includes(q) ||
      (t.city || '').toLowerCase().includes(q) ||
      (t.tools || []).some(tag => String(tag).toLowerCase().includes(q))
    )
  }
  switch (sortBy.value) {
    case 'created_asc': list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)); break
    case 'budget_desc': list.sort((a, b) => (b.budget ?? -1) - (a.budget ?? -1)); break
    case 'budget_asc': list.sort((a, b) => (a.budget ?? Infinity) - (b.budget ?? Infinity)); break
    default: list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
  return list
})

/* Действия */
const openTask = (id) => router.push(`/jobs/${id}`)
const editTask = (id) => router.push({ path: '/create-job', query: { edit: id } })

async function cancelTask(id) {
  const reason = window.prompt('Укажите причину отмены (необязательно):', '') || ''
  try {
    cancelingId.value = id
    const resp = await fetch(`${API_BASE}/api/jobs/${id}/cancel/`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(userStore.access ? { Authorization: `Bearer ${userStore.access}` } : {})
      },
      body: reason.trim() ? JSON.stringify({ reason: reason.trim() }) : '{}'
    })
    if (!resp.ok) {
      const data = await parseJsonOrThrow(resp).catch(() => ({}))
      throw new Error(data?.detail || `Ошибка ${resp.status}`)
    }
    const updated = await parseJsonOrThrow(resp)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx >= 0) {
      tasks.value[idx] = {
        ...tasks.value[idx],
        status: updated?.status || 'canceled_by_customer',
        canceled_reason: updated?.canceled_reason || reason,
        canceled_at: updated?.canceled_at || new Date().toISOString(),
      }
    }
  } catch (e) {
    alert(e instanceof Error ? e.message : String(e))
  } finally {
    cancelingId.value = null
  }
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-3 sm:px-4 lg:px-6 py-4 sm:py-8">
    <!-- Заголовок -->
    <header class="rounded-2xl border bg-gradient-to-br from-white/80 to-white/30 dark:from-gray-900/60 dark:to-gray-900/20 backdrop-blur p-4 sm:p-6 ring-1 ring-black/5 dark:ring-white/10 shadow-sm">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
            Мои задания
          </h1>
          <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400 mt-1">
            Следите за статусом, инструментами и архивом.
          </p>
        </div>
        <div class="flex flex-col sm:flex-row gap-2">
          <div class="relative">
       <input
  v-model="search"
  type="search"
  placeholder="Название, город или инструмент…"
  class="w-full sm:w-[260px] rounded-xl border border-gray-200 dark:border-white/10 bg-white/70 dark:bg-gray-900/60 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
/>

            <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">⌘K</span>
          </div>
          <select
            v-model="sortBy"
            class="rounded-xl border border-gray-200 dark:border-white/10 bg-white/70 dark:bg-gray-900/60 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="created_desc">Сначала новые</option>
            <option value="created_asc">Сначала старые</option>
            <option value="budget_desc">Бюджет: по убыв.</option>
            <option value="budget_asc">Бюджет: по возр.</option>
          </select>
          <button
            @click="fetchTasks"
            class="rounded-xl border border-gray-200 dark:border-white/10 bg-white/80 dark:bg-gray-900/60 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 hover:shadow-sm hover:-translate-y-0.5 transition"
          >
            Обновить
          </button>
        </div>
      </div>

      <!-- Вкладки: сегментный контрол -->
      <nav class="mt-4">
        <div class="inline-flex rounded-2xl border border-gray-200 dark:border-white/10 p-1 bg-white/60 dark:bg-gray-900/40">
          <button
            v-for="t in tabs" :key="t.key"
            @click="selectedTab = t.key"
            class="px-3 py-1.5 rounded-xl text-sm transition"
            :class="selectedTab === t.key
              ? 'bg-gray-900 text-white dark:bg-white dark:text-gray-900 shadow-sm'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10'">
            {{ t.label }}
          </button>
        </div>
      </nav>
    </header>

    <!-- Ошибка -->
    <div v-if="error" class="mt-4 rounded-xl border border-rose-200 bg-rose-50/80 dark:border-rose-400/25 dark:bg-rose-500/10 p-4 text-rose-700 dark:text-rose-300 shadow-sm">
      {{ error }}
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="i in 6" :key="i"
        class="h-40 rounded-2xl bg-gradient-to-r from-gray-100 via-gray-50 to-gray-100 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800 animate-pulse ring-1 ring-black/5 dark:ring-white/10"
      ></div>
    </div>

    <!-- Список -->
 <!-- Список -->
<div v-if="!loading && filtered.length" class="mt-6 grid auto-rows-fr gap-5 sm:grid-cols-2 lg:grid-cols-3">
  <article
    v-for="t in filtered" :key="t.id"
    class="card group h-full overflow-hidden rounded-2xl border border-gray-200/80 dark:border-white/10 bg-white/80 dark:bg-gray-900/60 shadow-sm"
  >
    <!-- декоративная рамка-градиент -->
    <div class="card-glow pointer-events-none"></div>

    <div class="flex h-full flex-col p-4 sm:p-5">
      <!-- Заголовок + статус -->
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <h3 class="">
            {{ t.title.toUpperCase() }}
          </h3>
          <p class="mt-1 text-xs text-gray-500">
            <span v-if="t.category">{{ t.category }}</span>
            <span v-if="t.category && t.city"> • </span>
            <span>{{ t.city || 'Удалённо' }}</span>
          </p>
        </div>
        <span class="status-chip" :class="statusPill(t.status).cls">
          {{ statusPill(t.status).label }}
        </span>
      </div>

      <!-- Информация -->
      <div class="mt-4 grid grid-cols-2 gap-2 text-sm">
        <div class="info-tile">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6"/>
            </svg>
            Бюджет
          </div>
          <div class="info-value">{{ formatMoney(t.budget) }}</div>
        </div>
        <div class="info-tile">
          <div class="info-label">
            <svg xmlns="http://www.w3.org/2000/svg" class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3M3 11h18M5 19h14a2 2 0 0 0 2-2v-6H3v6a2 2 0 0 0 2 2Z"/>
            </svg>
            Создано
          </div>
          <div class="info-value">{{ formatDate(t.created_at) }}</div>
        </div>
      </div>

      <!-- Инструменты -->
      <div v-if="t.tools && t.tools.length" class="mt-3 flex flex-wrap gap-1.5">
        <span v-for="(tool, idx) in t.tools.slice(0, 8)" :key="idx" class="tool-chip" :title="tool">
          {{ tool }}
        </span>
        <span v-if="t.tools.length > 8" class="tool-chip muted">+{{ t.tools.length - 8 }}</span>
      </div>

      <!-- Действия -->
      <div class="mt-auto border-t border-gray-200 dark:border-white/10 pt-3 flex flex-wrap gap-2">
        <button @click="openTask(t.id)" class="btn-ghost">Подробнее</button>
        <!-- Редактировать — убрано -->
        <button
          v-if="t.status==='pending'"
          :disabled="cancelingId===t.id"
          @click="cancelTask(t.id)"
          class="btn-danger ml-auto"
        >
          {{ cancelingId===t.id ? 'Отмена…' : 'Отменить' }}
        </button>
      </div>
    </div>
  </article>
</div>



    <!-- Пусто -->
    <div v-if="!loading && !filtered.length && !error" class="mt-10">
      <div class="mx-auto max-w-md rounded-2xl border border-dashed border-gray-300 dark:border-white/10 bg-white/70 dark:bg-gray-900/40 p-8 text-center shadow-sm">
        <div class="text-5xl">🗂️</div>
        <h3 class="mt-3 text-lg font-semibold text-gray-900 dark:text-white">Заданий пока нет</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Создайте своё первое задание — и оно появится здесь.
        </p>
        <button
          class="mt-4 inline-flex items-center rounded-xl border border-gray-200 dark:border-white/10 bg-white/80 dark:bg-gray-900/60 px-4 py-2 text-sm text-gray-900 dark:text-gray-100 hover:shadow-sm transition"
          @click="$router.push('/create-task')"
        >
          + Создать задание
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Кнопки */
.btn-ghost {
  @apply inline-flex items-center rounded-xl border border-gray-200 dark:border-white/10 bg-white/70 dark:bg-gray-900/40 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 hover:shadow-sm hover:-translate-y-0.5 transition;
}
.btn-danger {
  @apply inline-flex items-center rounded-xl border border-rose-300/70 dark:border-rose-400/40 bg-rose-50/70 dark:bg-rose-500/10 px-3 py-2 text-sm text-rose-700 dark:text-rose-300 hover:shadow-sm hover:-translate-y-0.5 transition disabled:opacity-60 disabled:hover:translate-y-0;
}
/* Симметрия и уникальный акцент */
.card {
  position: relative;
  isolation: isolate;
  backdrop-filter: saturate(120%) blur(2px);
}

/* Градиентная подсветка рамки ВСЕГДА включена */
.card-glow {
  position: absolute;
  inset: -1px;
  border-radius: 1rem;
  background:
    radial-gradient(120% 120% at 0% 0%, rgba(99,102,241,0.18), transparent 60%),
    radial-gradient(120% 120% at 100% 0%, rgba(236,72,153,0.18), transparent 60%),
    radial-gradient(120% 120% at 0% 100%, rgba(34,197,94,0.16), transparent 60%);
  opacity: .9;            /* <- сразу видно */
  pointer-events: none;
  z-index: -1;
}
/* Удалили: .card:hover .card-glow { opacity: .9; } — больше не нужно */

/* Заголовок с подсветкой */
.title-accent {
  @apply font-semibold text-gray-900 dark:text-white;
  background: linear-gradient(transparent 60%, rgba(99,102,241,.15) 0) no-repeat left 70% / 100% 1.05em;
  padding-bottom: 2px;
  transition: background-size .25s ease;
}

/* Карточка больше не «подскакивает/усиливает тень» — эффекты только у кнопок */

/* Статус‑чип */
.status-chip { @apply px-2 py-0.5 rounded-full text-[11px] font-semibold shadow-sm ring-1; }

/* Инфо-тайлы */
.info-tile {
  @apply rounded-xl bg-gray-50 dark:bg-white/5 px-3 py-2 ring-1 ring-gray-200/70 dark:ring-white/10 h-full;
  display: flex; flex-direction: column; justify-content: center; gap: 2px;
}
.info-label { @apply flex items-center gap-1.5 text-[11px] text-gray-500 dark:text-gray-400; }
.info-value { @apply font-medium text-gray-900 dark:text-gray-100; }

/* Чипы инструментов */
.tool-chip {
  @apply inline-flex items-center rounded-full border border-gray-200 dark:border-white/10
         bg-white/70 dark:bg-gray-900/40 px-2.5 py-1 text-[11px] leading-none
         text-gray-700 dark:text-gray-200 shadow-sm;
}
.tool-chip.muted { @apply text-gray-500; }

/* Кнопки — hover оставляем только тут */
.btn-ghost {
  @apply inline-flex items-center rounded-xl border border-gray-200 dark:border-white/10
         bg-white/70 dark:bg-gray-900/40 px-3 py-2 text-sm text-gray-900 dark:text-gray-100
         hover:shadow-sm hover:-translate-y-0.5 transition;
}
.btn-danger {
  @apply inline-flex items-center rounded-xl border border-rose-300/70 dark:border-rose-400/40
         bg-rose-50/70 dark:bg-rose-500/10 px-3 py-2 text-sm text-rose-700 dark:text-rose-300
         hover:shadow-sm hover:-translate-y-0.5 transition disabled:opacity-60 disabled:hover:translate-y-0;
}

/* Иконки в тайлах */
.size-3_5, .size-3\.5 { width: .875rem; height: .875rem; }

</style>
