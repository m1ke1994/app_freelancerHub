<!-- src/view/NotFound.vue -->
<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 text-center">
    <h1 class="text-6xl font-bold text-indigo-600 mb-4">404</h1>
    <p class="text-xl text-gray-700 dark:text-gray-300 mb-6">Страница не найдена</p>
    <router-link
      to="/"
      class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition"
    >
      На главную
    </router-link>
  </div>
</template>
