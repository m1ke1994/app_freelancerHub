<!-- src/views/ExecutorProfile.vue -->
<template>
  <div class="mx-auto max-w-5xl">
    <!-- HERO -->
    <header
      class="rounded-2xl border bg-gradient-to-br from-white/85 to-white/40 dark:from-slate-900/70 dark:to-slate-900/30 backdrop-blur p-4 sm:p-6 ring-1 ring-black/5 dark:ring-white/10 shadow-sm"
    >
      <div class="mb-4 flex items-center justify-between">
        <button class="btn-back inline-flex items-center gap-2" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Назад
        </button>

        <div class="flex items-center gap-2">
          <span v-if="isVerified(user)" class="chip chip--indigo" title="Проверенный исполнитель">✔ Проверен</span>
          <span v-if="isFiniteNum(user?.rating)" class="chip chip--slate">
            ★ {{ toFixedSafe(user.rating, 1) }} <span class="opacity-60">/ 5</span>
          </span>
          <span v-if="isFiniteNum(user?.reviews_count)" class="chip chip--slate">
            {{ user.reviews_count }} отзыв(ов)
          </span>
        </div>
      </div>

      <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
        <img
          :src="avatarSrc(user?.avatar || user?.avatar_url)"
          class="h-20 w-20 rounded-full ring-1 ring-black/5 object-cover"
          alt=""
          loading="lazy"
        />
        <div class="min-w-0">
          <h1 class="text-2xl sm:text-3xl font-semibold leading-tight truncate">
            {{ user?.full_name || user?.name || user?.username || ('Исполнитель #' + id) }}
          </h1>
          <p class="text-slate-600 dark:text-slate-300 text-sm sm:text-base">
            <template v-if="user?.title || user?.headline">
              {{ user.title || user.headline }}
              <span class="opacity-50"> • </span>
            </template>
            <span v-if="user?.location">{{ user.location }}</span>
            <span v-if="memberSince">
              <span class="opacity-50" v-if="user?.location"> • </span>
              на площадке с {{ memberSince }}
            </span>
          </p>
        </div>
      </div>
    </header>

    <!-- LOADING -->
    <section v-if="loading" class="mt-6 grid gap-6 md:grid-cols-3">
      <div class="md:col-span-2 space-y-3">
        <div class="h-7 w-1/2 animate-pulse rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-32 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700"></div>
      </div>
      <aside class="space-y-3">
        <div class="h-7 w-1/3 animate-pulse rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-32 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700"></div>
      </aside>
    </section>

    <!-- ERROR -->
    <section v-else-if="error" class="mt-6">
      <div class="rounded-xl border border-rose-200 dark:border-rose-800 bg-rose-50/80 dark:bg-rose-900/20 p-4">
        <div class="font-semibold text-rose-700 dark:text-rose-300">Ошибка</div>
        <div class="text-rose-600 dark:text-rose-200 text-sm">{{ error }}</div>
      </div>
    </section>

    <!-- CONTENT -->
    <section v-else class="mt-6 grid gap-6 md:grid-cols-3">
      <!-- Левая колонка -->
      <div class="md:col-span-2 space-y-6">
        <!-- О себе -->
        <div class="rounded-2xl border p-4 sm:p-6">
          <h2 class="mb-3 text-lg font-semibold">О себе</h2>
          <p v-if="user?.bio" class="whitespace-pre-wrap text-slate-700 dark:text-slate-200">
            {{ user.bio }}
          </p>
          <p v-else class="text-slate-500 dark:text-slate-400 text-sm">Исполнитель пока не заполнил описание.</p>
        </div>

        <!-- Портфолио -->
        <div v-if="portfolio.length" class="rounded-2xl border p-4 sm:p-6">
          <h2 class="mb-3 text-lg font-semibold">Портфолио</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <a
              v-for="(item, i) in portfolio"
              :key="i"
              class="group block rounded-xl border overflow-hidden hover:shadow-md transition"
              :href="item.url || item.link || '#'"
              target="_blank"
              rel="noopener"
            >
              <img
                v-if="item.image || item.thumbnail"
                :src="item.image || item.thumbnail"
                class="h-40 w-full object-cover"
                alt=""
                loading="lazy"
              />
              <div class="p-3">
                <div class="font-medium truncate">{{ item.title || 'Проект' }}</div>
                <div class="text-xs text-slate-500 line-clamp-2" v-if="item.description">{{ item.description }}</div>
              </div>
            </a>
          </div>
        </div>
      </div>

      <!-- Правая колонка -->
      <aside class="space-y-4">
        <!-- Контакты / ставки -->
        <div class="rounded-2xl border p-4 sm:p-6">
          <h3 class="mb-2 font-semibold">Детали исполнителя</h3>
          <dl class="text-sm space-y-2">
            <div class="flex justify-between">
              <dt class="text-slate-500">Город</dt>
              <dd>{{ user?.location || '—' }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-slate-500">Ставка</dt>
              <dd>{{ rateDisplay }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-slate-500">Занятость</dt>
              <dd>{{ user?.availability || user?.status || '—' }}</dd>
            </div>
          </dl>
        </div>

        <!-- Навыки -->
        <div class="rounded-2xl border p-4 sm:p-6">
          <h3 class="mb-2 font-semibold">Навыки</h3>
          <div v-if="skills.length" class="flex flex-wrap gap-2">
            <span v-for="s in skills" :key="s" class="chip chip--slate">{{ s }}</span>
          </div>
          <div v-else class="text-sm text-slate-500">Навыки ещё не указаны</div>
        </div>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'

/* ROUTER / STORE */
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/* Derived from route (works for { name: 'executor-profile', params: { id } } and /executors/:id) */
const id = computed(() => Number(route.params.id))

/* CONFIG */
const API_BASE = (import.meta?.env?.VITE_API_BASE || import.meta?.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

/* STATE */
const loading = ref(true)
const error = ref('')
const user = ref(null)

/* VIEW MAPPERS */
const skills = computed(() => {
  const raw = user.value?.skills || user.value?.skills_list || []
  return Array.isArray(raw) ? raw.slice(0, 24) : []
})
const portfolio = computed(() => {
  const p = user.value?.portfolio || user.value?.projects || []
  return Array.isArray(p) ? p : []
})
const memberSince = computed(() => {
  const field = user.value?.member_since || user.value?.date_joined || user.value?.created_at
  if (!field) return ''
  try { return new Date(field).toLocaleDateString() } catch { return '' }
})
const rateDisplay = computed(() => {
  const v = user.value?.hourly_rate || user.value?.rate || user.value?.price
  if (!Number.isFinite(Number(v))) return '—'
  return money(v) + ' / час'
})

/* ===== API: robust loader that tries several endpoints ===== */
async function getExecutorById(executorId, token = '') {
  const headers = { 'Accept': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const endpoints = [
    `${API_BASE}/api/executors/${executorId}/`,
    `${API_BASE}/api/users/${executorId}/`,
    `${API_BASE}/api/accounts/executors/${executorId}/`,
  ]

  let lastErr = null
  for (const url of endpoints) {
    try {
      const res = await fetch(url, { headers })
      if (res.ok) {
        const data = await res.json()
        // normalize a few common fields
        return {
          ...data,
          id: data.id ?? executorId,
          full_name: data.full_name || data.name || data.username || null,
          avatar: data.avatar || data.avatar_url || data.photo || null,
          location: data.location || data.city || data.country || null,
          hourly_rate: data.hourly_rate ?? data.rate ?? data.price ?? null,
          reviews_count: data.reviews_count ?? data.reviews ?? data.feedbacks_count ?? null,
          rating: data.rating ?? data.avg_rating ?? null,
          verified: data.verified ?? data.is_verified ?? data.kyc_verified ?? false,
          portfolio: Array.isArray(data.portfolio) ? data.portfolio : (Array.isArray(data.projects) ? data.projects : []),
          skills: Array.isArray(data.skills) ? data.skills : (Array.isArray(data.skills_list) ? data.skills_list : []),
        }
      } else {
        // 404/403/etc: keep trying next endpoint
        lastErr = new Error(`HTTP ${res.status}`)
      }
    } catch (e) {
      lastErr = e
    }
  }
  throw lastErr || new Error('Профиль не найден')
}

/* LOAD */
async function load() {
  if (!id.value || Number.isNaN(id.value)) {
    error.value = 'Некорректный идентификатор исполнителя'
    user.value = null
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const token = userStore?.access || localStorage.getItem('access') || ''
    user.value = await getExecutorById(id.value, token)
  } catch (e) {
    error.value = e?.message || 'Не удалось получить профиль исполнителя'
    user.value = null
  } finally {
    loading.value = false
  }
}

/* NAV */
function goBack() {
  if (history?.length > 1) router.back()
  else router.push({ name: 'tasks' })
}

/* UTILS (совместимы со стилем проекта) */
function isVerified(ex) { return Boolean(ex?.verified || ex?.is_verified || ex?.kyc_verified) }
function money(v) {
  const n = Number(v || 0)
  return new Intl.NumberFormat('ru-RU').format(Number.isFinite(n) ? n : 0) + ' ₽'
}
function toFixedSafe(num, digits = 1) {
  const n = Number(num)
  return Number.isFinite(n) ? n.toFixed(digits) : '—'
}
function isFiniteNum(v) { return Number.isFinite(Number(v)) }
function placeholderAvatar() { return 'https://api.dicebear.com/7.x/identicon/svg?seed=executor' }
function isAbsoluteUrl(u) { return /^https?:\/\//i.test(String(u || '')) }
function joinUrl(base, path) {
  const b = String(base || '').replace(/\/+$/, '')
  const p = String(path || '').replace(/^\/+/, '')
  return `${b}/${p}`
}
function avatarSrc(url) {
  if (!url) return placeholderAvatar()
  const raw = String(url).trim()
  if (isAbsoluteUrl(raw)) return raw
  let path = raw.replace(/\\/g, '/').replace(/^\.?\/+/, '')
  if (/^avatars\//i.test(path)) path = `media/${path}`
  const [cleanPath, query = ''] = path.split('?')
  const alreadyEncoded = (s) => /%(?:[0-9A-Fa-f]{2})/.test(s)
  const encoded = cleanPath
    .split('/')
    .map(seg => (!seg || seg.toLowerCase() === 'media') ? seg : (alreadyEncoded(seg) ? seg : encodeURIComponent(seg)))
    .join('/')
  return joinUrl(API_BASE, encoded) + (query ? `?${query}` : '')
}

/* LIFECYCLE */
onMounted(load)
/* React to route param changes (when navigating from another executor without page reload) */
watch(() => route.params.id, () => load())
</script>

<style scoped>
.btn-back { @apply text-slate-700 dark:text-slate-200 hover:text-indigo-600 transition; }
.chip { @apply inline-flex items-center rounded-full px-2 py-0.5 text-xs border; }
.chip--slate { @apply bg-slate-100 text-slate-700 border-slate-200 dark:border-slate-700 dark:text-slate-300 dark:bg-slate-400/15; }
.chip--indigo { @apply bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-400/15 dark:text-indigo-300; }
</style>
