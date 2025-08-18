<!-- components/CategoriesSection.vue -->
<template>
  <section class="py-16 px-4">
    <div class="container mx-auto max-w-6xl">
      <!-- Заголовок -->
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Популярные категории
        </h2>
        <p class="text-lg text-gray-600 dark:text-gray-300">
          Найдите специалиста в любой области
        </p>
      </div>

      <!-- Сетка категорий -->
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="category in categories"
          :key="category"
          class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 
                 hover:shadow-md transition-shadow cursor-pointer"
        >
          <div class="p-4 text-center">
            <p class="font-medium text-sm text-gray-900 dark:text-gray-100">
              {{ category }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const categories = [
  "Веб-разработка",
  "Мобильные приложения",
  "Дизайн",
  "Копирайтинг",
  "SEO и маркетинг",
  "Переводы",
  "Видеомонтаж",
  "3D моделирование",
  "Консалтинг",
  "Фотография",
  "Анимация",
  "Тестирование"
]
</script>
