<!-- src/view/CustomerIndividualForm.vue -->
<script setup>
import { reactive, computed } from "vue"

const props = defineProps({
  availability: { type: Boolean, default: true },
})
const emit = defineEmits(["submit", "update:availability"])

/* Локальная форма */
const form = reactive({
  location: "",
  age: "",
  activity: "",            // student/employee/business/freelancer/other
  bio: "",

  contact: {
    phone: "",
    telegram: "",
    linkedin: "",
    preferred: "telegram",
    showEmailTo: "hired_only",
    allowDM: true,
    workingHours: { tz: "Europe/Moscow", from: "10:00", to: "18:00" },
  },

  categories: [],
  cooperation: ["fixed_price"],
  budgetRange: { currency: "RUB", min: "", max: "" },
  urgency: "normal",
  payMethods: ["card"],

  ordersCount: 0,
  rating: null,
})

const categoriesOptions = [
  { value: "web", label: "Веб‑разработка" },
  { value: "design", label: "Дизайн" },
  { value: "marketing", label: "Маркетинг" },
  { value: "content", label: "Копирайтинг/Контент" },
  { value: "admin", label: "Администрирование" },
]
const cooperationOptions = [
  { value: "fixed_price", label: "Фикс‑прайс" },
  { value: "hourly", label: "Почасовая" },
  { value: "long_term", label: "Долгосрочно" },
]
const payMethodsOptions = [
  { value: "card", label: "Банковская карта" },
  { value: "bank", label: "Банковский счёт" },
  { value: "ewallet", label: "Эл. кошелёк" },
]
const urgencyOptions = [
  { value: "asap", label: "Срочно" },
  { value: "normal", label: "Обычно" },
  { value: "flexible", label: "Гибко" },
]

const canSave = computed(() => {
  const ageOk = String(form.age) === "" || (Number(form.age) >= 18 && Number(form.age) <= 120)
  const { min, max } = form.budgetRange
  const budgetOk = (min === "" || max === "" || Number(min) <= Number(max))
  return ageOk && budgetOk
})

function toggleArrayValue(arrRef, v) {
  const i = arrRef.indexOf(v)
  if (i === -1) arrRef.push(v)
  else arrRef.splice(i, 1)
}

function onSubmit() {
  if (!canSave.value) return
  emit("submit", {
    location: form.location.trim(),
    age: form.age === "" ? null : Number(form.age),
    activity: form.activity,
    bio: form.bio.trim(),

    socials: {
      telegram: form.contact.telegram.trim(),
      linkedin: form.contact.linkedin.trim(),
    },
    phone: form.contact.phone.trim(),
    preferred_contact: form.contact.preferred,
    show_email_to: form.contact.showEmailTo,
    allow_dm: !!form.contact.allowDM,
    working_hours: form.contact.workingHours,

    preferred_categories: form.categories,
    cooperation_types: form.cooperation,
    budget_range: form.budgetRange,
    urgency: form.urgency,
    pay_methods: form.payMethods,

    availability: props.availability,
  })
}
</script>

<template>
  <!-- О себе -->
  <div class="card">
    <div class="card-title">
      <span>О себе (физ лицо)</span>
      <label class="flex items-center gap-2">
        <input type="checkbox" class="chk" :checked="availability" @change="e => emit('update:availability', e.target.checked)" />
        <span class="lbl !m-0">Открыт к предложениям</span>
      </label>
    </div>

    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
      <input v-model="form.location" placeholder="Город / регион" class="inp" />
      <input v-model="form.age" type="number" min="18" max="120" placeholder="Возраст" class="inp" />

      <select v-model="form.activity" class="inp">
        <option value="" disabled>Род занятий</option>
        <option value="student">Студент</option>
        <option value="employee">Сотрудник</option>
        <option value="business">Предприниматель</option>
        <option value="freelancer">Фрилансер</option>
        <option value="other">Другое</option>
      </select>

      <textarea v-model="form.bio" rows="4" class="inp sm:col-span-2"
        placeholder="Коротко о себе и какие задачи хотите поручать"></textarea>
    </div>
  </div>

  <!-- Контакты и приватность -->
  <div class="card">
    <h3 class="card-title">Контакты и приватность</h3>

    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
      <input v-model="form.contact.phone" placeholder="+7…" class="inp" />
      <input v-model="form.contact.telegram" placeholder="@telegram" class="inp" />
      <input v-model="form.contact.linkedin" placeholder="https://linkedin.com/in/…" class="inp sm:col-span-2" />

      <div class="sm:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="lbl">Предпочтительный канал связи</label>
          <select v-model="form.contact.preferred" class="inp">
            <option value="phone">Телефон</option>
            <option value="telegram">Telegram</option>
            <option value="email">E‑mail</option>
            <option value="linkedin">LinkedIn</option>
          </select>
        </div>

        <div>
          <label class="lbl">Кому виден мой e‑mail</label>
          <select v-model="form.contact.showEmailTo" class="inp">
            <option value="all">Всем</option>
            <option value="registered">Только зарегистрированным</option>
            <option value="hired_only">Только нанятым</option>
          </select>
        </div>

        <div class="flex items-center gap-3">
          <input id="allowDM" type="checkbox" v-model="form.contact.allowDM" class="chk" />
          <label for="allowDM" class="lbl !m-0">Разрешать личные заявки</label>
        </div>
      </div>

      <div class="sm:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="lbl">Часовой пояс</label>
          <input v-model="form.contact.workingHours.tz" class="inp" placeholder="Europe/Moscow" />
        </div>
        <div>
          <label class="lbl">Доступен с</label>
          <input v-model="form.contact.workingHours.from" class="inp" placeholder="10:00" />
        </div>
        <div>
          <label class="lbl">до</label>
          <input v-model="form.contact.workingHours.to" class="inp" placeholder="18:00" />
        </div>
      </div>
    </div>
  </div>

  <!-- Предпочтения -->
  <div class="card">
    <h3 class="card-title">Предпочтения по задачам</h3>

    <div class="mt-4 space-y-5">
      <div>
        <div class="lbl mb-2">Категории задач</div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in categoriesOptions"
            :key="opt.value"
            type="button"
            @click="toggleArrayValue(form.categories, opt.value)"
            :class="form.categories.includes(opt.value)
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700'"
            class="px-3 py-1.5 rounded-full text-sm transition"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div>
        <div class="lbl mb-2">Формат сотрудничества</div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in cooperationOptions"
            :key="opt.value"
            type="button"
            @click="toggleArrayValue(form.cooperation, opt.value)"
            :class="form.cooperation.includes(opt.value)
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700'"
            class="px-3 py-1.5 rounded-full text-sm transition"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="lbl">Валюта</label>
          <select v-model="form.budgetRange.currency" class="inp">
            <option value="RUB">RUB</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
          </select>
        </div>
        <div>
          <label class="lbl">Бюджет от</label>
          <input v-model="form.budgetRange.min" type="number" min="0" class="inp" placeholder="0" />
        </div>
        <div>
          <label class="lbl">до</label>
          <input v-model="form.budgetRange.max" type="number" min="0" class="inp" placeholder="100000" />
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="lbl">Срочность</label>
          <select v-model="form.urgency" class="inp">
            <option v-for="o in urgencyOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>
        <div>
          <div class="lbl mb-2">Способы оплаты</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="opt in payMethodsOptions"
              :key="opt.value"
              type="button"
              @click="toggleArrayValue(form.payMethods, opt.value)"
              :class="form.payMethods.includes(opt.value)
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700'"
              class="px-3 py-1.5 rounded-full text-sm transition"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6 flex items-center justify-end">
      <button class="btn primary" :disabled="!canSave" @click="onSubmit">Сохранить раздел</button>
    </div>
  </div>
</template>

<style scoped>
.card { @apply rounded-2xl border bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 p-5 mb-6; }
.card-title { @apply flex items-center justify-between w-full text-left font-semibold text-gray-900 dark:text-white; }
.inp {
  @apply w-full px-3 py-2 rounded-lg border bg-white text-gray-900 placeholder-gray-400
         dark:bg-gray-900 dark:text-gray-100 dark:placeholder-gray-400
         border-gray-200 dark:border-gray-800 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
.lbl { @apply block text-sm font-medium text-gray-800 dark:text-gray-200 mb-1; }
.chk { @apply rounded border-gray-300 text-indigo-600 focus:ring-indigo-500; }
.btn { @apply px-5 py-3 rounded-full font-medium transition; }
.btn.primary { @apply bg-indigo-600 text-white hover:bg-indigo-700; }
</style>
