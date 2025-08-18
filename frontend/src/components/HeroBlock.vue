<template>
  <section class="py-16 px-4">
    <div class="container mx-auto text-center max-w-4xl">
      <!-- Заголовок -->
      <h1 class="text-4xl md:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6">
        Найди идеального
        <span class="text-indigo-600 dark:text-indigo-400"> исполнителя </span>
        без комиссий
      </h1>

      <!-- Подзаголовок -->
      <p class="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
        Прямое взаимодействие между заказчиками и фрилансерами. 
        Никаких скрытых комиссий, только честная работа.
      </p>

      <!-- CTA кнопки -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <router-link
          to="/services"
          class="px-8 py-3 text-lg font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition"
        >
          Найти исполнителя
          <svg xmlns="http://www.w3.org/2000/svg" class="inline ml-2 w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </router-link>

        <router-link
          to="/create-task"
          class="px-8 py-3 text-lg font-medium rounded-md border border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
        >
          Разместить задание
        </router-link>
      </div>

      <!-- Поисковая строка -->
      <div class="max-w-2xl mx-auto relative">
        <svg xmlns="http://www.w3.org/2000/svg"
             class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5"
             fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Поиск по заданиям: веб-разработка, дизайн, копирайтинг..."
          class="pl-12 pr-24 py-4 w-full rounded-md border border-gray-300 dark:border-gray-700 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
        />
        <router-link
          :to="{ path: '/tasks', query: { q: search }}"
          class="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
        >
          Найти
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const search = ref('')
</script>
