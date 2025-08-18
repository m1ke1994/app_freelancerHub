<script setup>
import { useRoute } from "vue-router"
import AppHeader from "@/components/AppNavbar.vue"
import AppFooter from "@/components/AppFooter.vue"

const route = useRoute()

// список маршрутов, где шапку и футер показывать не надо
const hiddenLayoutRoutes = ["/login", "/register"]
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <AppHeader v-if="!hiddenLayoutRoutes.includes(route.path)" />

    <!-- main растягивается -->
    <main class="flex-1 mx-auto w-full max-w-7xl p-4">
      <router-view />
    </main>

    <!-- footer всегда снизу -->
    <AppFooter v-if="!hiddenLayoutRoutes.includes(route.path)" />
  </div>
</template>
