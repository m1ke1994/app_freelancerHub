<template>
  <div class="mx-auto max-w-6xl">
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
          <span v-if="task?.urgent" class="chip warn">Срочно</span>
          <span v-if="hasBudget" class="price-badge" :title="budgetDisplay.title">
            {{ budgetDisplay.value }}
          </span>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <h1 class="text-2xl sm:text-3xl font-semibold leading-tight">
          {{ task?.title || '—' }}
        </h1>
        <p class="text-slate-600 dark:text-slate-300 text-sm sm:text-base">#{{ task?.id ?? '—' }}</p>
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
        <!-- Описание -->
        <div class="rounded-2xl border p-4 sm:p-6">
          <h2 class="mb-3 text-lg font-semibold">Описание</h2>
          <p class="whitespace-pre-wrap text-slate-700 dark:text-slate-200">
            {{ task?.description || 'Описание не указано' }}
          </p>
        </div>

        <!-- Владелец: отклики (без shortlist и без статуса "отправлен") -->
        <div v-if="isOwner" class="rounded-2xl border p-4 sm:p-6">
          <div class="mb-4 flex items-center justify-between gap-3">
            <h2 class="text-lg font-semibold">Отклики исполнителей</h2>
            <div v-if="stats" class="text-sm text-slate-500 dark:text-slate-400">
              Всего: <b>{{ stats.total }}</b>
              <template v-if="Number(stats.accepted) || Number(stats.rejected)">
                • Принято: <b>{{ stats.accepted }}</b>
                • Отклонено: <b>{{ stats.rejected }}</b>
              </template>
            </div>
          </div>

          <div v-if="proposalsLoading" class="text-sm text-slate-500">Загрузка откликов…</div>
          <div v-else-if="proposalsError" class="text-sm text-rose-600">{{ proposalsError }}</div>

          <template v-else>
            <div v-if="safeProposals.length === 0" class="text-sm text-slate-500">Пока нет откликов</div>

            <div
              v-for="(p, index) in safeProposals"
              :key="p?.id ?? ('p-' + index)"
              class="group mb-3 rounded-2xl border p-4 sm:p-5 transition-all hover:shadow-md"
            >
              <div class="flex flex-col gap-4">
                <!-- Шапка отклика -->
                <div class="flex items-start justify-between gap-4">
                  <div class="min-w-0 flex items-center gap-3">
                    <img
                      :src="avatarSrc(p.executor?.avatar || p.executor?.avatar_url)"
                      alt=""
                      class="h-10 w-10 rounded-full ring-1 ring-black/5 object-cover"
                      loading="lazy"
                    />
                    <div class="min-w-0">
                      <div class="flex flex-wrap items-center gap-2">
                        <span class="truncate font-semibold text-slate-900 dark:text-slate-100">
                          {{ p.executor?.full_name || ('Исполнитель #' + (p.executor?.id ?? '—')) }}
                        </span>
                        <span
                          v-if="isVerified(p.executor)"
                          class="chip chip--indigo"
                          title="Проверенный исполнитель"
                        >✔ Проверен</span>

                        <!-- Показываем бейдж статуса только если это accepted/rejected -->
                        <span
                          v-if="p.status === 'accepted'"
                          class="chip chip--emerald"
                          title="Отклик принят"
                        >Принят</span>
                        <span
                          v-else-if="p.status === 'rejected'"
                          class="chip chip--rose"
                          title="Отклик отклонён"
                        >Отклонён</span>
                      </div>

                      <div class="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                        <span v-if="isFiniteNum(p.executor?.rating)">
                          ★ {{ toFixedSafe(p.executor?.rating, 1) }} <span class="opacity-60">/ 5</span>
                        </span>
                        <span v-if="isFiniteNum(p.executor?.reviews_count)">
                          {{ p.executor.reviews_count }} отзыв(ов)
                        </span>
                        <span v-if="p.created_at" :title="isoToLocal(p.created_at)">
                          подан: {{ dateFromNow(p.created_at) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="flex shrink-0 items-center gap-2">
                    <button class="btn primary" @click="onAccept(p)" :disabled="actionBusy === p?.id">Принять</button>
                    <button class="btn danger" @click="onReject(p)" :disabled="actionBusy === p?.id">Отклонить</button>
                  </div>
                </div>

                <!-- Тело отклика -->
                <div v-if="p.cover_letter" class="text-sm whitespace-pre-wrap text-slate-700 dark:text-slate-200">
                  {{ p.cover_letter }}
                </div>

                <div class="flex flex-wrap items-center gap-3 text-sm">
                  <span>Ставка: <b>{{ money(p.bid_amount) }}</b></span>
                  <span v-if="p.days">• Срок: <b>{{ p.days }} дн.</b></span>
                  <span v-if="skills(p).length" class="hidden sm:inline">•</span>
                  <div v-if="skills(p).length" class="flex flex-wrap gap-1">
                    <span v-for="s in skills(p)" :key="s" class="chip chip--slate text-xs">{{ s }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Исполнитель: мой отклик (показываем статус только если принят/отклонён) -->
        <div v-if="isExecutor" class="rounded-2xl border p-4 sm:p-6">
          <h2 class="mb-3 text-lg font-semibold">Мой отклик</h2>

          <div v-if="myProposalLoading" class="text-sm text-slate-500">Проверяем наличие вашего отклика…</div>
          <div v-else-if="myProposalError" class="text-sm text-rose-600">{{ myProposalError }}</div>

          <template v-else>
            <!-- уже подан -->
            <div v-if="myProposal && !editMode" class="space-y-3">
              <div class="flex flex-wrap items-center gap-2 text-sm">
                <span v-if="myProposal.status === 'accepted'" class="chip chip--emerald">Принят</span>
                <span v-else-if="myProposal.status === 'rejected'" class="chip chip--rose">Отклонён</span>
                <span v-if="myProposal.updated_at" class="text-slate-500 dark:text-slate-400">
                  • обновлён: {{ dateFromNow(myProposal.updated_at) }}
                </span>
              </div>
              <div class="text-sm">
                Ставка: <b>{{ money(myProposal.bid_amount) }}</b>
                <span v-if="myProposal.days"> • Срок: <b>{{ myProposal.days }} дн.</b></span>
              </div>
              <p v-if="myProposal.cover_letter" class="whitespace-pre-wrap text-slate-700 dark:text-slate-200">
                {{ myProposal.cover_letter }}
              </p>

              <div class="flex gap-2">
                <button class="btn ghost" @click="editMode = true">Изменить</button>
                <button class="btn danger" @click="removeMyProposal" :disabled="actionBusy === myProposal?.id">
                  Удалить
                </button>
              </div>
            </div>

            <!-- нет отклика / режим редактирования -->
            <div v-if="!myProposal || editMode" class="space-y-4">
              <div>
                <label class="label">Сопроводительное письмо</label>
                <textarea
                  v-model="form.cover_letter"
                  rows="5"
                  class="input"
                  placeholder="Коротко опишите опыт и подход…"
                ></textarea>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="label">Ставка</label>
                  <input v-model.number="form.bid_amount" type="number" min="0" class="input" placeholder="Напр. 30000" />
                </div>
                <div>
                  <label class="label">Срок (дней)</label>
                  <input v-model.number="form.days" type="number" min="1" class="input" placeholder="Напр. 7" />
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-3">
                <button class="btn primary" @click="submitProposal" :disabled="submitBusy">
                  {{ myProposal ? 'Сохранить изменения' : 'Отправить отклик' }}
                </button>
                <span v-if="submitError" class="text-sm text-rose-600">{{ submitError }}</span>
                <span v-if="submitOk" class="text-sm text-emerald-600">Сохранено</span>
                <button v-if="editMode" class="btn ghost" @click="cancelEdit" :disabled="submitBusy">Отмена</button>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Правая колонка -->
      <aside class="space-y-4">
        <div class="rounded-2xl border p-4 sm:p-6">
          <h3 class="mb-2 font-semibold">Детали</h3>
          <dl class="text-sm space-y-2">
            <div class="flex justify-between">
              <dt class="text-slate-500">Бюджет</dt>
              <dd>{{ hasBudget ? budgetDisplay.value : '—' }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-slate-500">Срочность</dt>
              <dd>{{ task?.urgent ? 'Срочно' : 'Обычная' }}</dd>
            </div>
          </dl>
        </div>

        <!-- Кто откликнулся: компактный список -->
        <div v-if="isOwner" class="rounded-2xl border p-4 sm:p-6">
          <div class="mb-2 flex items-center justify-between">
            <h3 class="font-semibold">Кто откликнулся</h3>
            <span class="text-xs text-slate-500" v-if="safeProposals.length">{{ safeProposals.length }}</span>
          </div>
          <div v-if="proposalsLoading" class="text-sm text-slate-500">Загрузка…</div>
          <div v-else-if="!safeProposals.length" class="text-sm text-slate-500">Пока пусто</div>

          <ul v-else class="space-y-2">
            <li
              v-for="(p, index) in safeProposals"
              :key="'mini-' + (p?.id ?? index)"
              class="flex items-center gap-3"
            >
              <img
                :src="avatarSrc(p.executor?.avatar || p.executor?.avatar_url)"
                alt=""
                class="h-7 w-7 rounded-full ring-1 ring-black/5 object-cover"
                loading="lazy"
              />

              <div class="min-w-0">
                <div class="truncate text-sm font-medium">
                  {{ p.executor?.full_name || ('Исполнитель #' + (p.executor?.id ?? '—')) }}
                </div>
                <div class="text-xs text-slate-500">
                  {{ money(p.bid_amount) }} <span v-if="p.days">• {{ p.days }} дн.</span>
                </div>
              </div>

              <!-- Кнопка "Посмотреть профиль" -->
              <button
                class="btn ghost xs ml-auto"
                @click="viewExecutorProfile(p.executor?.id)"
                :disabled="!p?.executor?.id"
                title="Посмотреть профиль исполнителя"
              >
                Посмотреть профиль
              </button>

              <!-- Финальные статусы (если нужны) -->
              <span v-if="p.status === 'accepted'" class="chip text-[10px] chip--emerald">Принят</span>
              <span v-else-if="p.status === 'rejected'" class="chip text-[10px] chip--rose">Отклонён</span>
            </li>
          </ul>
        </div>

      </aside>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import {
  listProposals,
  createProposal,
  updateProposal,
  deleteProposal,
  acceptProposal,
  rejectProposal,
  proposalsStats,
} from '@/api/proposalsApi'

/* ==== ROUTER / STORE ==== */
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const jobId = computed(() => Number(route.params.id))

/* ==== NAV TO EXECUTOR PROFILE (фиксированный алгоритм) ==== */
function viewExecutorProfile(id) {
  if (!id) return
  // 1) пробуем именованный маршрут (рекомендованный способ)
  if (typeof router.hasRoute === 'function' ? router.hasRoute('executor-offer') : true) {
    router.push({ name: 'executor-profile', params: { id } })
    return
  }
  // 2) безопасный fallback — прямой путь
  router.push(`/executors/${id}`)
}

/* ==== TASK LOAD ==== */
const API_BASE = (import.meta?.env?.VITE_API_BASE || import.meta?.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const task = ref(null)
const loading = ref(true)
const error = ref('')

async function fetchTask() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/jobs/${jobId.value}/`)
    if (!res.ok) throw new Error('Не удалось получить задание')
    task.value = await res.json()
  } catch (e) {
    error.value = e.message || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

/* ==== ROLES ==== */
const me = computed(() => userStore?.user || null)
const jobOwnerIds = computed(() => {
  const j = task.value || {}
  const raw = j.owner || j.customer || j.user || j.author || j.created_by || j.client || null
  const u = raw && typeof raw === 'object' ? (raw.id || raw.user_id || raw.pk) : raw
  return [u].filter(Boolean)
})
const isOwner = computed(() => !!(me.value && jobOwnerIds.value.includes(me.value.id)))
const isExecutor = computed(() => !!(me.value && !jobOwnerIds.value.includes(me.value.id)))

/* ==== BUDGET ==== */
const hasBudget = computed(() => {
  const j = task.value || {}
  return j.budget || j.bmin || j.bmax
})
const budgetDisplay = computed(() => {
  const j = task.value || {}
  const money = (v) => new Intl.NumberFormat('ru-RU').format(Number(v || 0))
  if (j.budget) return { title: 'Фикс', value: `${money(j.budget)} ₽` }
  if (j.bmin || j.bmax) return { title: 'Диапазон', value: `${j.bmin ? money(j.bmin) : '—'} — ${j.bmax ? money(j.bmax) : '—'} ₽` }
  return { title: '', value: '—' }
})

/* ==== OWNER: PROPOSALS & STATS ==== */
const proposals = ref([])
const proposalsLoading = ref(false)
const proposalsError = ref('')
const stats = ref(null)
const actionBusy = ref(null)

/** Преобразование любого формата ответа в массив + фильтр мусора */
function toArray(data) {
  const arr = Array.isArray(data) ? data : (Array.isArray(data?.results) ? data.results : [])
  return arr.filter((p) => p && typeof p === 'object')
}
const safeProposals = computed(() => toArray(proposals.value))

async function fetchProposals() {
  if (!isOwner.value) return
  proposalsLoading.value = true
  proposalsError.value = ''
  try {
    const data = await listProposals({ job: jobId.value })
    proposals.value = toArray(data)
    stats.value = await proposalsStats(jobId.value)
  } catch (e) {
    proposalsError.value = e.message || 'Ошибка загрузки откликов'
  } finally {
    proposalsLoading.value = false
  }
}

async function onAccept(p) {
  try {
    actionBusy.value = p?.id ?? null
    if (!actionBusy.value) return
    await acceptProposal(actionBusy.value)
    await fetchProposals()
  } catch (e) {
    alert(e.message || 'Не удалось принять отклик')
  } finally {
    actionBusy.value = null
  }
}
async function onReject(p) {
  try {
    actionBusy.value = p?.id ?? null
    if (!actionBusy.value) return
    await rejectProposal(actionBusy.value)
    await fetchProposals()
  } catch (e) {
    alert(e.message || 'Не удалось отклонить отклик')
  } finally {
    actionBusy.value = null
  }
}

/* ==== EXECUTOR: MY PROPOSAL ==== */
const myProposal = ref(null)
const myProposalLoading = ref(false)
const myProposalError = ref('')
const editMode = ref(false)
const form = ref({ cover_letter: '', bid_amount: null, days: null })
const submitBusy = ref(false)
const submitError = ref('')
const submitOk = ref(false)

async function fetchMyProposal() {
  if (!isExecutor.value) return
  myProposalLoading.value = true
  myProposalError.value = ''
  try {
    const data = await listProposals({ job: jobId.value })
    const list = toArray(data)
    const mine = list.find(p =>
      Number(p?.job) === jobId.value &&
      Number(p?.executor?.id) === Number(me.value?.id)
    ) || null
    myProposal.value = mine
    if (myProposal.value) {
      form.value = {
        cover_letter: myProposal.value.cover_letter || '',
        bid_amount: Number(myProposal.value.bid_amount || 0),
        days: myProposal.value.days || null,
      }
    }
  } catch (e) {
    myProposalError.value = e.message || 'Не удалось получить ваш отклик'
  } finally {
    myProposalLoading.value = false
  }
}

async function submitProposal() {
  submitBusy.value = true
  submitError.value = ''
  submitOk.value = false
  try {
    const payload = {
      job: jobId.value,
      cover_letter: String(form.value.cover_letter || '').trim(),
      bid_amount: Number(form.value.bid_amount || 0),
      days: form.value.days ? Number(form.value.days) : null,
    }
    if (myProposal.value?.id) {
      await updateProposal(myProposal.value.id, payload)
      editMode.value = false
    } else {
      await createProposal(payload)
    }
    submitOk.value = true
    await Promise.all([fetchMyProposal(), fetchProposals()])
  } catch (e) {
    submitError.value = e.message || 'Не удалось сохранить отклик'
  } finally {
    submitBusy.value = false
    setTimeout(() => (submitOk.value = false), 1500)
  }
}

async function removeMyProposal() {
  if (!myProposal.value?.id) return
  if (!confirm('Удалить ваш отклик?')) return
  try {
    actionBusy.value = myProposal.value.id
    await deleteProposal(actionBusy.value)
    myProposal.value = null
    editMode.value = true
    await fetchProposals()
  } catch (e) {
    alert(e.message || 'Не удалось удалить отклик')
  } finally {
    actionBusy.value = null
  }
}

function cancelEdit() {
  editMode.value = false
  if (myProposal.value) {
    form.value = {
      cover_letter: myProposal.value.cover_letter || '',
      bid_amount: Number(myProposal.value.bid_amount || 0),
      days: myProposal.value.days || null,
    }
  }
}

/* ==== UTILS ==== */
function goBack() {
  if (history?.length > 1) router.back()
  else router.push({ name: 'tasks' })
}
function money(v) {
  const n = Number(v || 0)
  return new Intl.NumberFormat('ru-RU').format(Number.isFinite(n) ? n : 0) + ' ₽'
}
function isFiniteNum(v) { return Number.isFinite(Number(v)) }

/* ===== АВАТАРЫ / ПРОФИЛЬ ИСПОЛНИТЕЛЯ ===== */
function isVerified(ex) {
  return Boolean(ex?.verified || ex?.is_verified || ex?.kyc_verified)
}
function placeholderAvatar() {
  return 'https://api.dicebear.com/7.x/identicon/svg?seed=executor'
}
function isAbsoluteUrl(u) {
  return /^https?:\/\//i.test(String(u || ''))
}
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
    .map(seg => {
      if (!seg || seg.toLowerCase() === 'media') return seg
      return alreadyEncoded(seg) ? seg : encodeURIComponent(seg)
    })
    .join('/')
  return joinUrl(API_BASE, encoded) + (query ? `?${query}` : '')
}

function skills(p) {
  const s = p?.executor?.skills || p?.skills || []
  return Array.isArray(s) ? s.slice(0, 6) : []
}
function toFixedSafe(num, digits = 1) {
  const n = Number(num)
  return Number.isFinite(n) ? n.toFixed(digits) : '—'
}
function isoToLocal(iso) {
  try { return new Date(iso).toLocaleString() } catch { return '' }
}
function dateFromNow(iso) {
  const d = new Date(iso)
  const diff = (Date.now() - d.getTime()) / 1000
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`
  return d.toLocaleDateString()
}

/* ==== LIFECYCLE ==== */
onMounted(async () => {
  await fetchTask()
  if (isOwner.value) {
    await fetchProposals()
  } else if (isExecutor.value) {
    await fetchMyProposal()
  }
})
</script>

<style scoped>
/* утилиты под tailwind-классы из проекта */
.btn-back {
  @apply text-slate-700 dark:text-slate-200 hover:text-indigo-600 transition;
}

.btn {
  @apply inline-flex items-center justify-center rounded-xl px-3 py-2 text-sm border;
}

.btn.primary {
  @apply bg-indigo-600 text-white border-indigo-600 hover:bg-indigo-700;
}

.btn.ghost {
  @apply bg-transparent text-slate-700 dark:text-slate-200 border-slate-300 dark:border-slate-700 hover:bg-slate-50/60 dark:hover:bg-slate-800/40;
}

.btn.danger {
  @apply bg-rose-600 text-white border-rose-600 hover:bg-rose-700;
}

.chip {
  @apply inline-flex items-center rounded-full px-2 py-0.5 text-xs border;
}

.chip.warn {
  @apply bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-400/15 dark:text-amber-300;
}

.chip--slate {
  @apply bg-slate-100 text-slate-700 border-slate-200 dark:border-slate-700 dark:text-slate-300 dark:bg-slate-400/15;
}

.chip--indigo {
  @apply bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-400/15 dark:text-indigo-300;
}

.chip--emerald {
  @apply bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-400/15 dark:text-emerald-300;
}

.chip--rose {
  @apply bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-400/15 dark:text-rose-300;
}

.input {
  @apply w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500/40;
}

.label {
  @apply mb-1 block text-sm text-slate-600 dark:text-slate-300;
}

.price-badge {
  @apply inline-flex items-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-400/15 dark:text-emerald-300 px-2 py-1 text-xs border border-emerald-200;
}
.btn.xs { @apply px-2 py-1 text-xs rounded-lg; }
</style>
