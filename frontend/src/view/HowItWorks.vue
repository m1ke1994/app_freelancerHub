<!-- src/components/HowItWorks.vue -->
<script setup>
import { ref } from "vue"

const mode = ref("customer") // 'customer' | 'freelancer'

const stepsCustomer = [
  { title: "Опишите задачу", text: "Коротко и по делу: цели, объём, сроки. Добавьте файлы при необходимости.", icon: "edit" },
  { title: "Получайте отклики", text: "Фрилансеры сами откликнутся. Сравните ставки, сроки и опыт.", icon: "inbox" },
  { title: "Выберите исполнителя", text: "Оцените портфолио и рейтинг. Обсудите детали в чате.", icon: "user-check" },
  { title: "Получите результат", text: "Примите работу и оставьте отзыв.", icon: "check-circle" },
]

const stepsFreelancer = [
  { title: "Заполните профиль", text: "Био, навыки, портфолио и ставка — чтобы вас выбрали.", icon: "id" },
  { title: "Находите задания", text: "Фильтры и поиск помогут быстро найти проекты.", icon: "search" },
  { title: "Откликайтесь", text: "Пишите осмысленные предложения со сроками и ценой.", icon: "message" },
  { title: "Работайте и растите", text: "Сдавайте проекты, получайте отзывы и растите в рейтинге.", icon: "growth" },
]
</script>

<template>
  <section class="py-12 px-4 bg-white dark:bg-gray-900">
    <div class="mx-auto max-w-7xl">
      <!-- Заголовок -->
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white">Как это работает</h2>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Понятный процесс для заказчиков и исполнителей — без комиссий и лишней бюрократии
        </p>
      </div>

      <!-- Переключатель -->
      <div class="mx-auto w-full sm:w-auto flex items-center justify-center">
        <div class="inline-flex rounded-full border border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-gray-800 p-1">
          <button
            class="px-4 py-1.5 text-sm rounded-full transition"
            :class="mode === 'customer'
              ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow'
              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'"
            @click="mode = 'customer'"
          >
            Для заказчика
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-full transition"
            :class="mode === 'freelancer'
              ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow'
              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'"
            @click="mode = 'freelancer'"
          >
            Для исполнителя
          </button>
        </div>
      </div>

      <!-- Сетка шагов -->
      <div class="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="(s, i) in (mode === 'customer' ? stepsCustomer : stepsFreelancer)"
          :key="s.title"
          class="h-full rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-sm hover:shadow-md transition"
        >
          <!-- Две колонки: иконка | контент -->
          <div class="grid grid-cols-[3.5rem,1fr] gap-4 items-start">
            <!-- Иконка: фиксированный аккуратный «квадрат» -->
            <div class="shrink-0 grid place-items-center w-14 h-14 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300">
              <!-- все SVG одинакового размера -->
              <svg v-if="s.icon==='edit'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M16 3l5 5M4 20l5.5-1.5L21 7l-5-5L4 20Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='inbox'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M3 13h4l2 3h6l2-3h4M5 7h14l2 6-2 6H5L3 13l2-6Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='user-check'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11-2-2 2-1-1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='check-circle'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M9 12l2 2 4-4M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='id'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M3 5h18v14H3V5Zm6 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm8 6h-8a4 4 0 0 1 8 0Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='search'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M21 21l-4.35-4.35M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='message'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M21 12c0 4.418-4.03 8-9 8-1.1 0-2.15-.18-3.1-.51L3 21l1.6-4.2C4.2 15.58 3 13.9 3 12c0-4.42 4.03-8 9-8s9 3.58 9 8Z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else-if="s.icon==='growth'" viewBox="0 0 24 24" fill="none" class="w-7 h-7 stroke-current">
                <path d="M3 21h18M7 17V9m5 8V7m5 10V5M7 9l5-2 5-2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>

            <!-- Контент -->
            <div>
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center justify-center text-xs font-semibold text-white bg-indigo-600 rounded-full w-6 h-6 leading-none">
                  {{ i + 1 }}
                </span>
                <h3 class="font-semibold text-gray-900 dark:text-white leading-tight">
                  {{ s.title }}
                </h3>
              </div>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {{ s.text }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
        <router-link
          v-if="mode === 'customer'"
          to="/create-task"
          class="inline-flex items-center justify-center px-5 py-3 rounded-full bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition w-full sm:w-auto"
        >
          Разместить задание
          <span class="ml-2" aria-hidden="true">→</span>
        </router-link>

        <router-link
          v-else
          to="/register"
          class="inline-flex items-center justify-center px-5 py-3 rounded-full bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition w-full sm:w-auto"
        >
          Создать профиль
          <span class="ml-2" aria-hidden="true">→</span>
        </router-link>

        <router-link
          :to="mode === 'customer' ? '/jobs' : '/freelancers'"
          class="inline-flex items-center justify-center px-5 py-3 rounded-full border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 transition w-full sm:w-auto"
        >
          Посмотреть каталог
        </router-link>
      </div>
    </div>
  </section>
</template>
