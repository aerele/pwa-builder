<template>
  <hr />

  <div class="px-4 py-2">
    <!-- {{ item }} -->
    <div class="flex flex-row justify-between items-center">
      <div class="cursor-pointer">
        <div class="cursor-pointer">{{ item.title }}</div>
        <div class="cursor-pointer">{{ item.status }}</div>
      </div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        height="20"
        width="20"
        stroke="currentColor"
        class=""
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="m19.5 8.25-7.5 7.5-7.5-7.5"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Function to toggle the expand state
let isExpanded = ref(true)

const { item } = defineProps(['item'])
</script>
