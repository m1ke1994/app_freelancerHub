<!-- src/view/CustomerProfile.vue -->
<script setup>
import { ref, reactive, onMounted, computed } from "vue"
import { useUserStore } from "@/store/userStore"

const userStore = useUserStore()

/* Read-only из регистрации */
const locked = reactive({
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
})

/* Расширенные поля профиля */
const avatar_url        = ref("")
const availability      = ref(true)
const location          = ref("")
const timezone          = ref("")
const about             = ref("")
const preferred_contact = ref("email")  // email | phone | telegram
const contact_handle    = ref("")

const budget_range   = ref("")
const urgency        = ref("normal")
const nda_required   = ref(false)
const contact_time   = ref("anytime")   // anytime | morning | day | evening

/* Загрузка профиля */
onMounted(async () => {
  if (!userStore.user) {
    try { await userStore.fetchProfile?.() } catch {}
  }
  const u = userStore.user || {}

  locked.first_name = u.first_name || ""
  locked.last_name  = u.last_name  || ""
  locked.email      = u.email      || ""
  locked.phone      = u.phone || ""

  avatar_url.value        = u.avatar_url || ""
  availability.value      = u.availability ?? true
  location.value          = u.location || ""
  timezone.value          = u.timezone || ""
  about.value             = u.about || ""
  preferred_contact.value = u.preferred_contact || "email"
  contact_handle.value    = u.contact_handle || ""

  budget_range.value = u.budget_range || ""
  urgency.value      = u.urgency || "normal"
  nda_required.value = !!u.nda_required
  contact_time.value = u.contact_time || "anytime"
})

/* Сохранение */
const saving = ref(false)
const saved  = ref(false)

async function onSaveProfile() {
  saving.value = true
  saved.value = false
  try {
    const payload = {
      avatar_url: avatar_url.value,
      availability: !!availability.value,
      location: location.value?.trim(),
      timezone: timezone.value?.trim(),
      about: about.value?.trim(),
      preferred_contact: preferred_contact.value,
      contact_handle: contact_handle.value?.trim(),
      budget_range: budget_range.value,
      urgency: urgency.value,
      nda_required: !!nda_required.value,
      contact_time: contact_time.value,
    }

    // API вызов сюда (пример):
    // await api.patch("/api/customer/profile/", payload)

    userStore.setUser?.({ ...(userStore.user || {}), ...payload })
    saved.value = true
  } finally {
    saving.value = false
    setTimeout(() => (saved.value = false), 2200)
  }
}

/* Загрузка аватара (превью) */
async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  avatar_url.value = URL.createObjectURL(file)
  userStore.setUser?.({ ...(userStore.user || {}), avatar_url: avatar_url.value })
}

const headerBadgeClass = computed(() =>
  availability.value
    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-400/20 dark:text-emerald-300"
    : "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
)
const LockIcon = defineComponent({
  name: "LockIcon",
  setup() {
    return () =>
      h(
        "svg",
        {
          class:
            "w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400",
          viewBox: "0 0 24 24",
          fill: "none",
          stroke: "currentColor",
          "stroke-width": "1.5",
        },
        [
          h("rect", { x: "4", y: "11", width: "16", height: "9", rx: "2" }),
          h("path", { d: "M8 11V8a4 4 0 0 1 8 0v3" }),
        ]
      )
  },
})
</script>

<template>
  <section class="py-8 px-4">
    <div class="mx-auto max-w-4xl">
      <!-- Заголовок -->
      <header class="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Профиль заказчика</h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Чем подробнее заполнен профиль — тем проще исполнителям понять ваши задачи.
          </p>
        </div>
        <div class="hidden sm:flex items-center gap-2">
          <span :class="headerBadgeClass" class="px-2.5 py-1 rounded-full text-xs font-semibold">
            {{ availability ? 'Открыт к предложениям' : 'Временно не ищу' }}
          </span>
        </div>
      </header>

      <!-- Карточка профиля -->
      <div class="card">
        <div class="grid grid-cols-1 md:grid-cols-[auto,1fr] gap-6">
          <!-- Аватар -->
          <div class="flex flex-col items-center gap-3">
            <div class="relative">
              <img
                v-if="avatar_url"
                :src="avatar_url"
                alt="Фото профиля"
                class="w-28 h-28 rounded-2xl object-cover border border-gray-200 dark:border-gray-800 shadow-sm"
              />
              <div
                v-else
                class="w-28 h-28 rounded-2xl flex items-center justify-center
                       bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400
                       border border-gray-200 dark:border-gray-800"
              >
                <span class="text-xs">Нет фото</span>
              </div>
            </div>
            <label class="cursor-pointer text-xs text-indigo-600 hover:underline dark:text-indigo-400">
              Загрузить фото
              <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            </label>
          </div>

          <!-- Поля -->
          <div class="space-y-6">
            <!-- Read-only под замком -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input :value="locked.first_name" disabled class="inp muted" placeholder="Имя" />
              <input :value="locked.last_name"  disabled class="inp muted" placeholder="Фамилия" />
              <input :value="locked.email"      disabled class="inp muted" placeholder="E-mail" />
              <input :value="locked.phone"      disabled class="inp muted" placeholder="Телефон" />
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Эти данные редактируются в разделе «Аккаунт». Здесь они отображаются только для справки.
            </p>

            <!-- Локация / Часовой пояс -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input v-model.trim="location" class="inp" placeholder="Город" />
              <input v-model.trim="timezone" class="inp" placeholder="Часовой пояс (например GMT+3)" />
            </div>

            <!-- Контакты -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select v-model="preferred_contact" class="inp">
                <option value="email">Связь по e-mail</option>
                <option value="phone">По телефону</option>
                <option value="telegram">Через Telegram</option>
              </select>
              <input
                v-model.trim="contact_handle"
                class="inp"
                :placeholder="preferred_contact === 'email' ? 'Доп. e-mail (опц.)' :
                              preferred_contact === 'phone' ? 'Альтернативный номер' :
                              '@username'"
              />
            </div>

            <!-- Бюджет / Срочность / NDA -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <select v-model="budget_range" class="inp">
                <option value="">Диапазон бюджета</option>
                <option value="<10k">до 10 000 ₽</option>
                <option value="10-50k">10–50 000 ₽</option>
                <option value="50-200k">50–200 000 ₽</option>
                <option value=">200k">свыше 200 000 ₽</option>
              </select>
              <select v-model="urgency" class="inp">
                <option value="normal">Обычно в стандартные сроки</option>
                <option value="urgent">Часто срочно</option>
              </select>
              <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200">
                <input type="checkbox" v-model="nda_required" class="checkbox" />
                Нужно NDA
              </label>
            </div>

            <!-- Время для связи -->
            <select v-model="contact_time" class="inp">
              <option value="anytime">Можно писать в любое время</option>
              <option value="morning">Предпочтительно утром</option>
              <option value="day">Предпочтительно днём</option>
              <option value="evening">Предпочтительно вечером</option>
            </select>

            <!-- Описание -->
            <textarea
              v-model.trim="about"
              class="inp h-28 resize-none"
              placeholder="Расскажите о типичных задачах или проектах (до 300 символов)"
              maxlength="300"
            ></textarea>

            <!-- Кнопки -->
            <div class="mt-4 flex items-center justify-end gap-3">
              <p v-if="saved" class="text-green-600 dark:text-green-400">Сохранено ✅</p>
              <button class="btn primary disabled:opacity-50" :disabled="saving" @click="onSaveProfile">
                {{ saving ? "Сохраняем..." : "Сохранить" }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.card { @apply rounded-2xl border bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 p-5; }
.inp {
  @apply w-full px-4 py-2.5 rounded-xl border bg-white text-gray-900 placeholder-gray-400
         dark:bg-gray-900 dark:text-gray-100 dark:placeholder-gray-500
         border-gray-200 dark:border-gray-800 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
.inp.muted {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 border-gray-200 dark:border-gray-800;
}
.btn { @apply px-5 py-3 rounded-full font-medium transition; }
.btn.primary { @apply bg-indigo-600 text-white hover:bg-indigo-700; }
.checkbox {
  @apply w-5 h-5 rounded border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 cursor-pointer;
}
.checkbox:checked { @apply bg-indigo-600 border-indigo-600; }
</style>
