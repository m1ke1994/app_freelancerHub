<script setup lang="ts">
import HeroBlock from '../components/HeroBlock.vue';
import PopularCategories from '../components/PopularCategories.vue';
import RecentTasks from '../components/RecentTasks.vue';
import WhyChoose from '../components/WhyChoose.vue';


</script>

<template>
  <section class="space-y-3">
    <HeroBlock></HeroBlock>
    <WhyChoose></WhyChoose>
    <PopularCategories></PopularCategories>
    <RecentTasks></RecentTasks>
   
  </section>
</template>
