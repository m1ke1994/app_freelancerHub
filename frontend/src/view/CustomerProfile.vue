<!-- src/view/CustomerProfile.vue -->
<script setup>
import { ref, reactive, onMounted, watch } from "vue"
import { useUserStore } from "@/store/userStore.js"

const userStore = useUserStore()

/* ---------- Вспомогательный локальный компонент ---------- */
const LockIcon = {
  name: "LockIcon",
  template: `
    <svg class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"
         viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <rect x="4" y="10" width="16" height="10" rx="2"></rect>
      <path d="M8 10V8a4 4 0 1 1 8 0v2"></path>
    </svg>
  `,
}

/* ---------- Read-only из регистрации ---------- */
const requiredFields = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
})

/* ---------- Публичный профиль (как у фрилансера, но без навыков) ---------- */
const genderOptions = ["Мужской", "Женский", "Не указывать"]
const educationOptions = [
  "Среднее",
  "Среднее специальное",
  "Незаконченное высшее",
  "Высшее",
  "Магистр/Аспирантура",
  "Другое",
]
const statusOptions = [
  { value: "individual", label: "Физлицо" },
  { value: "company", label: "Компания/ИП" },
]

const form = reactive({
  title: "",            // Заголовок профиля *
  location: "",         // Город/регион
  gender: "",           // select
  education: "",        // select
  status: "individual", // select
  bio: "",              // О себе *
  availability: true,   // чекбокс
})

const errors = reactive({
  title: "",
  bio: "",
})

/* ---------- Аватар ---------- */
const avatarPreview = ref("")
const avatarUploading = ref(false)
const avatarError = ref("")

/* ---------- UI ---------- */
const openPublic = ref(true)

/* ---------- Инициализация из стора ---------- */
function hydrateFromUser(u) {
  if (!u) return
  requiredFields.first_name = u.first_name || ""
  requiredFields.last_name  = u.last_name  || ""
  requiredFields.email      = u.email      || ""
  requiredFields.phone      = u.phone      || ""

  form.title       = u.title ?? ""
  form.location    = u.location ?? ""
  form.gender      = u.gender ?? ""
  form.education   = u.education ?? ""
  form.status      = u.status ?? "individual"
  form.bio         = u.bio ?? ""
  form.availability = u.availability ?? true

  avatarPreview.value = u.avatar_url || ""
}

onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchProfile?.().catch(() => {})
  }
  hydrateFromUser(userStore.user)
})

watch(() => userStore.user, (u) => hydrateFromUser(u), { deep: true })

/* ---------- Сохранение + авто-погасание статуса ---------- */
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref("")
let statusTimer = null

function clearStatusAfter(ms = 3000) {
  if (statusTimer) {
    clearTimeout(statusTimer)
    statusTimer = null
  }
  statusTimer = setTimeout(() => {
    saveSuccess.value = false
    saveError.value = ""
  }, ms)
}

function validate() {
  errors.title = form.title.trim() ? "" : "Заполните заголовок профиля"
  errors.bio   = form.bio.trim()   ? "" : "Расскажите кратко о себе/компании"
  return !errors.title && !errors.bio
}

async function onSave() {
  // сбрасываем статусы перед новой попыткой
  saveSuccess.value = false
  saveError.value = ""

  if (!validate()) {
    // если валидация не прошла — показать «ошибку» на кнопке и погасить статус
    saveError.value = "Заполните обязательные поля"
    clearStatusAfter()
    return
  }

  saving.value = true
  try {
    const payload = {
      title: form.title.trim(),
      location: form.location.trim(),
      gender: form.gender,
      education: form.education,
      status: form.status,
      bio: form.bio.trim(),
      availability: !!form.availability,
    }
    if (userStore.updateProfile) {
      await userStore.updateProfile(payload)
    } else {
      userStore.setUser?.({ ...(userStore.user || {}), ...payload })
    }
    saveSuccess.value = true
  } catch (e) {
    saveError.value = e?.message || "Не удалось сохранить изменения"
  } finally {
    saving.value = false
    // авто-погасание статуса через 3 секунды
    clearStatusAfter(3000)
  }
}

/* ---------- Загрузка аватара ---------- */
function toDataUrl(file) {
  return new Promise((res, rej) => {
    const r = new FileReader()
    r.onload = () => res(r.result)
    r.onerror = rej
    r.readAsDataURL(file)
  })
}

async function onAvatarChange(e) {
  avatarError.value = ""
  const file = e.target.files?.[0]
  if (!file) return

  try {
    // локальный предпросмотр
    avatarPreview.value = await toDataUrl(file)
  } catch { /* ignore */ }

  if (!userStore.uploadAvatar) return

  avatarUploading.value = true
  try {
    const data = await userStore.uploadAvatar(file)
    avatarPreview.value = data?.avatar_url || avatarPreview.value
  } catch (err) {
    avatarError.value = err?.message || "Ошибка загрузки файла"
  } finally {
    avatarUploading.value = false
    e.target.value = "" // сброс input
  }
}
</script>

<template>
  <section class="mx-auto max-w-4xl p-4 md:p-6">
    <!-- Вступительный блок -->
    <div class="relative overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-700 bg-white/70 dark:bg-gray-800/70 backdrop-blur shadow-sm mb-6">
      <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-emerald-500"></div>
      <div class="p-6 md:p-8">
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Анкета заказчика
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Основные данные из регистрации защищены от редактирования. Заполните публичный профиль — он виден исполнителям.
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Левая колонка -->
      <div class="space-y-6 lg:col-span-2">
        <!-- Основные данные из регистрации -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Основные данные (из регистрации)</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Имя</label>
              <div class="relative">
                <input :value="requiredFields.first_name" disabled
                       class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                <LockIcon />
              </div>
            </div>

            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Фамилия</label>
              <div class="relative">
                <input :value="requiredFields.last_name" disabled
                       class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                <LockIcon />
              </div>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Email</label>
              <div class="relative">
                <input :value="requiredFields.email" disabled
                       class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                <LockIcon />
              </div>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Телефон</label>
              <div class="relative">
                <input :value="requiredFields.phone" disabled
                       class="w-full px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200" />
                <LockIcon />
              </div>
            </div>
          </div>
        </div>

        <!-- Публичный профиль -->
        <section class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
          <button @click="openPublic = !openPublic" class="w-full flex items-center justify-between px-5 py-4">
            <h3 class="font-semibold text-gray-900 dark:text-white">Публичный профиль</h3>
            <span class="text-lg">{{ openPublic ? "▲" : "▼" }}</span>
          </button>

          <div v-show="openPublic" class="px-5 pb-5">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="sm:col-span-2">
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Заголовок профиля *</label>
                <input v-model="form.title"
                       placeholder="Например: Ищу исполнителей для маркетинговых задач"
                       class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
                <p v-if="errors.title" class="mt-1 text-xs text-red-600">{{ errors.title }}</p>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Локация</label>
                <input v-model="form.location" placeholder="Город или «Удалённо»"
                       class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600" />
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Статус</label>
                <select v-model="form.status"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Пол</label>
                <select v-model="form.gender"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option value="">Не указывать</option>
                  <option v-for="g in genderOptions" :key="g" :value="g">{{ g }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">Образование</label>
                <select v-model="form.education"
                        class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600">
                  <option value="">—</option>
                  <option v-for="e in educationOptions" :key="e" :value="e">{{ e }}</option>
                </select>
              </div>

              <div class="sm:col-span-2">
                <label class="block text-sm text-gray-600 dark:text-gray-300 mb-1">О себе *</label>
                <textarea v-model="form.bio" rows="4"
                          placeholder="Чем занимаетесь, какие задачи публикуете, как удобнее взаимодействовать с исполнителями"
                          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-600"></textarea>
                <p v-if="errors.bio" class="mt-1 text-xs text-red-600">{{ errors.bio }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Доступность -->
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Доступность</h3>
          <label class="flex items-center gap-3">
            <input type="checkbox" v-model="form.availability"
                   class="rounded border-gray-300 dark:border-gray-700 text-indigo-600" />
            <span class="text-gray-800 dark:text-gray-200">Принимаю новые заказы</span>
          </label>
        </div>

        <!-- Кнопка со статусами (как у фрилансера) -->
        <div class="flex justify-end">
          <button
            :disabled="saving"
            @click="onSave"
            :class="[
              'inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full text-white font-medium transition-colors disabled:opacity-60 disabled:cursor-not-allowed',
              'min-w-[220px] h-12',
              saveSuccess
                ? 'bg-green-600 hover:bg-green-700'
                : (saveError ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700')
            ]"
            aria-live="polite"
          >
            <svg v-if="saving" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="9" stroke-width="1.5" class="opacity-25"/>
              <path d="M12 3a9 9 0 0 1 9 9" stroke-width="1.5"/>
            </svg>

            <template v-else-if="saveSuccess">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              <span>Сохранено</span>
            </template>

            <template v-else-if="saveError">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
              <span>Ошибка</span>
            </template>

            <template v-else>
              <span>Сохранить изменения</span>
            </template>
          </button>
        </div>
      </div>

      <!-- Правая колонка (Аватар) -->
      <aside class="space-y-6">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Аватар</h3>
          <div class="flex items-center gap-4">
            <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <img v-if="avatarPreview" :src="avatarPreview" class="w-full h-full object-cover" alt="avatar" />
              <svg v-else viewBox="0 0 24 24" class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="8" r="4" />
                <path d="M4 20c0-4 4-6 8-6s8 2 8 6" stroke-linecap="round"/>
              </svg>
            </div>

            <label class="inline-flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
              <svg v-if="avatarUploading" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="9" stroke-width="1.5" class="opacity-25"/>
                <path d="M12 3a9 9 0 0 1 9 9" stroke-width="1.5"/>
              </svg>
              <span v-else>Загрузить</span>
              <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            </label>
          </div>
          <p v-if="avatarError" class="mt-2 text-sm text-red-600">{{ avatarError }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
/* плавное скрытие секции */
[ v-cloak ] { display: none; }
</style>
