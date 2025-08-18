<!-- components/BenefitsSection.vue -->
<template>
  <section class="py-16 px-4 bg-gray-50 dark:bg-gray-800/30">
    <div class="container mx-auto max-w-6xl">
      <!-- Заголовок -->
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Почему выбирают FreelanceHub?
        </h2>
        <p class="text-lg text-gray-600 dark:text-gray-300">
          Мы создали платформу, которая работает для всех
        </p>
      </div>

      <!-- Карточки -->
      <div class="grid md:grid-cols-3 gap-8">
        <!-- Без комиссий -->
        <div class="text-center rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-6 shadow-sm">
          <div class="w-12 h-12 bg-indigo-600/10 dark:bg-indigo-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <!-- CheckCircle -->
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-indigo-600 dark:text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Без комиссий</h3>
          <p class="mt-2 text-gray-600 dark:text-gray-300">
            Договаривайтесь напрямую и работайте без посредников. Вся оплата остается у вас.
          </p>
        </div>

        <!-- Проверенные специалисты -->
        <div class="text-center rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-6 shadow-sm">
          <div class="w-12 h-12 bg-emerald-600/10 dark:bg-emerald-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <!-- Users -->
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-emerald-600 dark:text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 14a4 4 0 10-8 0m12 4v-1a4 4 0 00-4-4H8a4 4 0 00-4 4v1m12-10a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Проверенные специалисты</h3>
          <p class="mt-2 text-gray-600 dark:text-gray-300">
            Система рейтингов и отзывов помогает найти надежных исполнителей для любых задач.
          </p>
        </div>

        <!-- Качественные проекты -->
        <div class="text-center rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-6 shadow-sm">
          <div class="w-12 h-12 bg-amber-500/10 dark:bg-amber-400/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <!-- Star -->
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-amber-500 dark:text-amber-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.48 3.5a.75.75 0 011.04 0l2.36 2.42 3.35.56a.75.75 0 01.4 1.28l-2.46 2.42.59 3.45a.75.75 0 01-1.09.79L12 13.88 8.33 15.4a.75.75 0 01-1.09-.79l.59-3.45L5.37 8.76a.75.75 0 01.4-1.28l3.35-.56L11.48 3.5z"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Качественные проекты</h3>
          <p class="mt-2 text-gray-600 dark:text-gray-300">
            Модерация заданий и профилей обеспечивает высокое качество предложений на платформе.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// без логики — чистый презентационный блок
</script>
