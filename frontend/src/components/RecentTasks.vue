<!-- components/LatestJobs.vue -->
<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-900/30">
    <div class="container mx-auto max-w-6xl">
      <!-- Заголовок -->
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Свежие задания</h2>
        <router-link
          to="/tasks"
          class="px-4 py-2 border rounded-md text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition flex items-center gap-2"
        >
          Все задания
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </router-link>
      </div>

      <!-- Сетка заданий -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(job, index) in jobs"
          :key="index"
          class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 
                 p-5 hover:shadow-lg transition-shadow cursor-pointer"
        >
          <!-- Заголовок -->
          <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
            {{ job.title }}
          </h3>

          <!-- Бюджет + Дедлайн -->
          <div class="flex items-center justify-between mb-4">
            <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{{ job.budget }}</span>
            <span class="px-2 py-1 text-xs font-medium border rounded-md text-gray-700 dark:text-gray-300">
              {{ job.deadline }}
            </span>
          </div>

          <!-- Навыки -->
          <div class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="skill in job.skills"
              :key="skill"
              class="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-md text-xs text-gray-800 dark:text-gray-200"
            >
              {{ skill }}
            </span>
          </div>

          <!-- Кол-во откликов -->
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ job.responses }} откликов
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const jobs = [
  {
    title: "Разработка интернет-магазина на React",
    budget: "150 000 ₽",
    deadline: "2 недели",
    skills: ["React", "Node.js", "PostgreSQL"],
    responses: 12,
  },
  {
    title: "Дизайн мобильного приложения",
    budget: "80 000 ₽",
    deadline: "10 дней",
    skills: ["UI/UX", "Figma", "Mobile Design"],
    responses: 8,
  },
  {
    title: "SEO оптимизация сайта",
    budget: "45 000 ₽",
    deadline: "1 месяц",
    skills: ["SEO", "Google Analytics", "Контент"],
    responses: 15,
  },
]
</script>
