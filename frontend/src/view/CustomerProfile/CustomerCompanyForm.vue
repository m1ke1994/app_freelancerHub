<!-- src/view/CustomerCompanyForm.vue -->
<script setup>
import { reactive, computed } from "vue"

const props = defineProps({
  availability: { type: Boolean, default: true },
})
const emit = defineEmits(["submit", "update:availability"])

/* Локальная форма компании */
const form = reactive({
  company: "",
  legalForm: "",          // ООО/ИП/Самозанятый/АО/Иное
  website: "",
  location: "",
  teamSize: "",           // 1–5 / 6–20 / 21–50 / 50+
  about: "",

  contact: {
    person: "",           // контактное лицо
    phone: "",
    email: "",
    telegram: "",
    preferred: "email",
    workingHours: { tz: "Europe/Moscow", from: "10:00", to: "18:00" },
  },

  cooperation: ["long_term"],
  budgetRange: { currency: "RUB", min: "", max: "" },
  categories: [],
  payMethods: ["bank"],

  vacancy: {
    enabled: false,
    title: "",
    employment: "full_time",
    remote: "any",
    officeLocation: "",
    salary: { currency: "RUB", min: "", max: "", gross: true },
    skills: [],
    newSkill: "",
    description: "",
  },
})

const legalForms = ["ООО", "ИП", "Самозанятый", "АО", "Другое"]
const teamSizes  = ["1–5", "6–20", "21–50", "50+"]
const categoriesOptions = [
  { value: "web", label: "Веб‑разработка" },
  { value: "design", label: "Дизайн" },
  { value: "marketing", label: "Маркетинг" },
  { value: "content", label: "Контент" },
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
const vacancyEmployment = [
  { value: "project", label: "Проектная" },
  { value: "part_time", label: "Частичная" },
  { value: "full_time", label: "Полная" },
]

const canSave = computed(() => {
  const { min, max } = form.budgetRange
  return (min === "" || max === "" || Number(min) <= Number(max))
})

const vacancyErrors = computed(() => {
  if (!form.vacancy.enabled) return []
  const e = []
  if (!form.vacancy.title.trim()) e.push("Укажите название вакансии.")
  const s = form.vacancy.salary
  if (s.min !== "" && s.max !== "" && Number(s.min) > Number(s.max)) e.push("Зарплата: «от» больше «до».")
  if (form.vacancy.remote !== "remote" && !form.vacancy.officeLocation.trim()) e.push("Добавьте локацию офиса.")
  return e
})

function toggleArrayValue(arr, v) {
  const i = arr.indexOf(v)
  if (i === -1) arr.push(v); else arr.splice(i, 1)
}

function addSkill() {
  const s = form.vacancy.newSkill.trim()
  if (!s) return
  if (!form.vacancy.skills.includes(s)) form.vacancy.skills.push(s)
  form.vacancy.newSkill = ""
}
function removeSkill(i) { form.vacancy.skills.splice(i, 1) }

function onSubmit() {
  if (!canSave.value) return
  const v = form.vacancy
  emit("submit", {
    // company profile
    company: form.company.trim(),
    legal_form: form.legalForm,
    website: form.website.trim(),
    location: form.location.trim(),
    team_size: form.teamSize,
    bio: form.about.trim(),

    contact_person: form.contact.person.trim(),
    phone: form.contact.phone.trim(),
    company_email: form.contact.email.trim(),
    telegram: form.contact.telegram.trim(),
    preferred_contact: form.contact.preferred,
    working_hours: form.contact.workingHours,

    preferred_categories: form.categories,
    cooperation_types: form.cooperation,
    budget_range: form.budgetRange,
    pay_methods: form.payMethods,

    availability: props.availability,

    // optional vacancy payload (только если включена)
    vacancy: !v.enabled ? null : {
      title: v.title.trim(),
      employment: v.employment,
      remote: v.remote,
      location: v.remote === "remote" ? "" : v.officeLocation.trim(),
      salary: v.salary,
      skills: v.skills,
      description: v.description.trim(),
    },
  })
}
</script>

<template>
  <!-- О компании -->
  <div class="card">
    <div class="card-title">
      <span>О компании</span>
      <label class="flex items-center gap-2">
        <input type="checkbox" class="chk" :checked="availability" @change="e => $emit('update:availability', e.target.checked)" />
        <span class="lbl !m-0">Открыты к предложениям</span>
      </label>
    </div>

    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
      <input v-model="form.company" class="inp" placeholder="Название компании" />
      <select v-model="form.legalForm" class="inp">
        <option value="" disabled>Организационно‑правовая форма</option>
        <option v-for="o in legalForms" :key="o" :value="o">{{ o }}</option>
      </select>
      <input v-model="form.website" class="inp sm:col-span-2" placeholder="Сайт (https://…)" />
      <input v-model="form.location" class="inp" placeholder="Город / страна" />
      <select v-model="form.teamSize" class="inp">
        <option value="" disabled>Размер команды</option>
        <option v-for="o in teamSizes" :key="o" :value="o">{{ o }}</option>
      </select>
      <textarea v-model="form.about" rows="4" class="inp sm:col-span-2" placeholder="Чем занимаетесь, чем можете быть интересны исполнителям"></textarea>
    </div>
  </div>

  <!-- Контакты -->
  <div class="card">
    <h3 class="card-title">Контакты</h3>
    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
      <input v-model="form.contact.person" class="inp" placeholder="Контактное лицо" />
      <input v-model="form.contact.phone" class="inp" placeholder="+7…" />
      <input v-model="form.contact.email" class="inp" placeholder="email@company.com" />
      <input v-model="form.contact.telegram" class="inp" placeholder="@telegram" />

      <div>
        <label class="lbl">Предпочтительный канал</label>
        <select v-model="form.contact.preferred" class="inp">
          <option value="email">E‑mail</option>
          <option value="phone">Телефон</option>
          <option value="telegram">Telegram</option>
        </select>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="lbl">Часовой пояс</label>
          <input v-model="form.contact.workingHours.tz" class="inp" placeholder="Europe/Moscow" />
        </div>
        <div>
          <label class="lbl">с</label>
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
    <h3 class="card-title">Предпочтения</h3>
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

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="lbl">Формат сотрудничества</label>
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

        <div>
          <label class="lbl">Способы оплаты</label>
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
.btn.ghost { @apply bg-transparent text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800; }

.chip { @apply inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs bg-indigo-600 text-white; }
.chip-x { @apply ml-1 rounded-full px-1 leading-none bg-black/10 dark:bg-white/10; }
</style>
