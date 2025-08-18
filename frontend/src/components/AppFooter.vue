<!-- components/AppFooter.vue -->
<template>
  <footer class="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
    <div class="container mx-auto max-w-7xl px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-10">
        <!-- Логотип -->
        <div>
          <div class="flex items-center gap-2 mb-4">
            <div class="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7h16M4 12h16M4 17h16"/>
              </svg>
            </div>
            <span class="text-2xl font-bold text-indigo-600">FreelanceHub</span>
          </div>
          <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-4">
            Платформа для прямого взаимодействия заказчиков и исполнителей.
          </p>
          <!-- Соцсети -->
          <div class="flex gap-4">
            <a href="#" class="text-gray-500 hover:text-indigo-600 transition" aria-label="Telegram">
              <i class="fa-brands fa-telegram fa-lg"></i>
            </a>
            <a href="#" class="text-gray-500 hover:text-indigo-600 transition" aria-label="VK">
              <i class="fa-brands fa-vk fa-lg"></i>
            </a>
            <a href="#" class="text-gray-500 hover:text-indigo-600 transition" aria-label="GitHub">
              <i class="fa-brands fa-github fa-lg"></i>
            </a>
          </div>
        </div>

        <!-- Для заказчиков -->
        <div>
          <h3 class="font-semibold mb-4 text-gray-900 dark:text-gray-100">Для заказчиков</h3>
          <ul class="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
            <li><router-link to="/create-task" class="hover:text-indigo-600">Разместить задание</router-link></li>
            <li><router-link to="/services" class="hover:text-indigo-600">Найти исполнителя</router-link></li>
            <li><router-link to="/how-it-works" class="hover:text-indigo-600">Как это работает</router-link></li>
          </ul>
        </div>

        <!-- Для исполнителей -->
        <div>
          <h3 class="font-semibold mb-4 text-gray-900 dark:text-gray-100">Для исполнителей</h3>
          <ul class="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
            <li><router-link to="/tasks" class="hover:text-indigo-600">Найти работу</router-link></li>
            <li><router-link to="/register" class="hover:text-indigo-600">Создать профиль</router-link></li>
            <li><router-link to="/tips-for-freelancers" class="hover:text-indigo-600">Советы фрилансерам</router-link></li>
          </ul>
        </div>

        <!-- Поддержка -->
        <div>
          <h3 class="font-semibold mb-4 text-gray-900 dark:text-gray-100">Поддержка</h3>
          <ul class="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
            <li><router-link to="/help" class="hover:text-indigo-600">Помощь</router-link></li>
            <li><router-link to="/contact" class="hover:text-indigo-600">Контакты</router-link></li>
            <li><router-link to="/terms" class="hover:text-indigo-600">Условия использования</router-link></li>
          </ul>
        </div>
      </div>

      <!-- Нижняя часть -->
      <div class="border-t border-gray-200 dark:border-gray-700 mt-10 pt-6 text-center text-gray-600 dark:text-gray-400 text-sm">
        <p>&copy; 2024 FreelanceHub. Все права защищены.</p>
      </div>
    </div>
  </footer>
</template>
