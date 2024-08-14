<template>
  <hr />

  <div class="px-4 py-2">
    <!-- {{ item }} -->
    <div class="flex flex-row justify-between items-center cursor-pointer">
      <div class="cursor-pointer">
        <div class="">{{ item.title }}</div>
        <!-- <div class="cursor-pointer">{{ item.status }}</div> -->
         <div>{{ item.doctype_name }}</div>
      </div>
      <!-- <svg
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
      </svg> -->
      <Menu as="div" class="relative inline-block text-left">
    <div>
      <MenuButton class="hover:bg-gray-50">
        <FeatherIcon name="chevron-down" class="w-5 h-5" />
      </MenuButton>
    </div>
    <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
      <MenuItems class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
        <div class="py-1">
          <MenuItem v-slot="{ active }">
            <a href="#" :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'block px-4 py-2 text-sm']">Account settings</a>
          </MenuItem>
          <MenuItem v-slot="{ active }">
            <a href="#" :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'block px-4 py-2 text-sm']">Support</a>
          </MenuItem>
          <MenuItem v-slot="{ active }">
            <a href="#" :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'block px-4 py-2 text-sm']">License</a>
          </MenuItem>
          <form method="POST" action="#">
            <MenuItem v-slot="{ active }">
              <button type="submit" :class="[active ? 'bg-gray-100 text-gray-900' : 'text-gray-700', 'block w-full px-4 py-2 text-left text-sm']">Delete</button>
            </MenuItem>
          </form>
        </div>
      </MenuItems>
    </transition>
  </Menu>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { FeatherIcon, Dropdown } from 'frappe-ui'

// Function to toggle the expand state
let isExpanded = ref(true)



const { item } = defineProps(['item'])
</script>