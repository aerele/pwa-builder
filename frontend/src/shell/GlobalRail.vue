<template>
  <!-- Left rail shown at the global (non-project) level. -->
  <nav class="rail">
    <div class="rail__group">
      <router-link
        v-for="item in items"
        :key="item.name"
        :to="item.to"
        class="rail__item"
        :class="{ 'rail__item--active': isActive(item) }"
      >
        <FeatherIcon :name="item.icon" class="w-[18px] h-[18px]" />
        <span>{{ item.label }}</span>
      </router-link>
    </div>

    <div class="rail__spacer" />

    <a class="rail__item rail__item--muted" href="https://github.com/aerele/pwa-builder" target="_blank" rel="noopener">
      <FeatherIcon name="help-circle" class="w-[18px] h-[18px]" />
      <span>Help</span>
    </a>
  </nav>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { useRoute } from 'vue-router'

const route = useRoute()
const items = [
  { name: 'Dashboard', label: 'Home', icon: 'grid', to: { name: 'Dashboard' } },
  { name: 'Templates', label: 'Templates', icon: 'layout', to: { name: 'Templates' } },
  { name: 'Settings', label: 'Settings', icon: 'settings', to: { name: 'Settings' } },
]

function isActive(item) {
  return route.name === item.name
}
</script>

<style scoped>
.rail {
  display: flex;
  flex-direction: column;
  width: 208px;
  height: 100%;
  padding: 12px 10px;
  background: var(--surface-rail);
  border-right: 1px solid var(--border);
}
.rail__group { display: flex; flex-direction: column; gap: 2px; }
.rail__spacer { flex: 1; }
.rail__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text-muted);
  border-radius: var(--radius-control);
  transition: background 0.12s ease, color 0.12s ease;
}
.rail__item:hover { background: var(--surface-muted); color: var(--text); }
.rail__item--active {
  background: var(--brand-subtle);
  color: var(--brand);
}
.rail__item--muted { color: var(--text-subtle); }
</style>
