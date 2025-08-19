<!-- src/view/CustomerProfile.vue -->
<script setup>
import { ref, reactive, onMounted, computed } from "vue"
import { useUserStore } from "@/store/userStore"
import CustomerIndividualForm from "@/view/CustomerProfile/CustomerIndividualForm.vue"
import CustomerCompanyForm from "@/view/CustomerProfile/CustomerCompanyForm.vue"

const userStore = useUserStore()

/* Регистрационные поля (read-only) */
const required = reactive({
  first_name: "",
  last_name: "",
  email: "",
  role: "",
})

/* Общие вещи профиля */
const avatar_url = ref("")
const availability = ref(true)

/* Тип профиля */
const profileType = ref("individual") // 'individual' | 'company'

/* Загрузка профиля */
onMounted(async () => {
  if (!userStore.user) {
    try { await userStore.fetchProfile?.() } catch {}
  }
  const u = userStore.user || {}
  required.first_name = u.first_name || ""
  required.last_name  = u.last_name  || ""
  required.email      = u.email      || ""
  required.role       = u.role       || "customer"
  avatar_url.value    = u.avatar_url || ""
  availability.value  = u.availability ?? true

  // автоопределение: если уже есть company поля — включим company
  if (u.company || u.legal_form || u.team_size) profileType.value = "company"
})

/* Сохранение (главный обработчик) */
const saving = ref(false)
const saved  = ref(false)

async function onSaveProfile(payloadFromChild) {
  saving.value = true
  saved.value = false
  try {
    const payload = {
      avatar_url: avatar_url.value,
      availability: !!availability.value,
      profile_type: profileType.value,
      ...payloadFromChild, // уникальные поля зависят от формы
    }

    // Пример API:
    // await api.patch("/api/customer/profile/", payload)

    userStore.setUser?.({ ...(userStore.user || {}), ...payload })
    saved.value = true
  } finally {
    saving.value = false
    setTimeout(() => (saved.value = false), 2200)
  }
}

/* Загрузка аватара */
async function onAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  // const fd = new FormData(); fd.append("avatar", file)
  // const res = await api.post("/api/users/upload-avatar/", fd, { headers: {"Content-Type":"multipart/form-data"} })
  // avatar_url.value = res.data.avatar_url

  // временный превью:
  avatar_url.value = URL.createObjectURL(file)
  userStore.setUser?.({ ...(userStore.user || {}), avatar_url: avatar_url.value })
}

const headerBadgeClass = computed(() =>
  availability.value
    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-400/20 dark:text-emerald-300"
    : "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
)
</script>

<template>
  <section class="py-8 px-4">
    <div class="mx-auto max-w-5xl">
      <!-- Заголовок -->
      <header class="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Профиль заказчика</h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Заполни профиль — исполнителям будет проще понять задачи и условия.
          </p>
        </div>
        <div class="hidden sm:flex items-center gap-2">
          <span :class="headerBadgeClass" class="px-2.5 py-1 rounded-full text-xs font-semibold">
            {{ availability ? 'Открыт к предложениям' : 'Временно не ищу' }}
          </span>
        </div>
      </header>

      <!-- Основные данные -->
      <div class="card">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-3">Основные данные</h3>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 items-center">
          <!-- Фото -->
          <div class="flex flex-col items-center gap-2">
            <img
              v-if="avatar_url"
              :src="avatar_url"
              alt="Фото профиля"
              class="w-24 h-24 rounded-full object-cover border border-gray-300 dark:border-gray-700"
            />
            <div v-else class="w-24 h-24 rounded-full flex items-center justify-center
                               bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400
                               border border-gray-300 dark:border-gray-700">
              <span class="text-sm">Нет фото</span>
            </div>

            <label class="cursor-pointer text-xs text-indigo-600 hover:underline dark:text-indigo-400">
              Загрузить фото
              <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            </label>
          </div>

          <!-- Read-only регистрационные поля -->
          <input :value="required.first_name" disabled class="inp muted" />
          <input :value="required.last_name"  disabled class="inp muted" />
          <input :value="required.email"      disabled class="inp muted" />
        </div>

        <div class="mt-4 flex items-center justify-between gap-4">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Имя, фамилия и e‑mail редактируются в разделе «Аккаунт». Роль: <b>{{ required.role }}</b>.
          </p>

          <!-- Переключатель типа профиля -->
          <div class="flex items-center gap-2 rounded-full bg-gray-100 dark:bg-gray-800 p-1">
            <button
              class="switch-btn"
              :class="profileType === 'individual' ? 'switch-btn--active' : ''"
              @click="profileType = 'individual'"
            >
              Я физ лицо
            </button>
            <button
              class="switch-btn"
              :class="profileType === 'company' ? 'switch-btn--active' : ''"
              @click="profileType = 'company'"
            >
              Я компания
            </button>
          </div>
        </div>
      </div>

      <!-- Формы -->
      <CustomerIndividualForm
        v-if="profileType === 'individual'"
        :availability="availability"
        @update:availability="val => availability = val"
        @submit="onSaveProfile"
      />
      <CustomerCompanyForm
        v-else
        :availability="availability"
        @update:availability="val => availability = val"
        @submit="onSaveProfile"
      />

      <!-- Кнопка сохранения дубль (на случай, если захочется внизу страницы) -->
      <div class="mt-6 flex items-center justify-end gap-3">
        <p v-if="saved" class="text-green-600 dark:text-green-400">Сохранено ✅</p>
        <button class="btn primary disabled:opacity-50" :disabled="saving" @click="$emit('submit')">
          {{ saving ? "Сохраняем..." : "Сохранить" }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.card { @apply rounded-2xl border bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 p-5 mb-6; }
.inp {
  @apply w-full px-3 py-2 rounded-lg border bg-white text-gray-900 placeholder-gray-400
         dark:bg-gray-900 dark:text-gray-100 dark:placeholder-gray-400
         border-gray-200 dark:border-gray-800 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
.inp.muted { @apply bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 border-gray-200 dark:border-gray-800; }

.btn { @apply px-5 py-3 rounded-full font-medium transition; }
.btn.primary { @apply bg-indigo-600 text-white hover:bg-indigo-700; }

.switch-btn {
  @apply px-3 py-1.5 text-sm rounded-full text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 transition;
}
.switch-btn--active {
  @apply bg-white text-indigo-700 dark:bg-gray-900 dark:text-indigo-300 shadow;
}
</style>
