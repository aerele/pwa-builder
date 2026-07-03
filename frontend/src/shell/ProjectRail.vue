<template>
  <!-- Left rail shown inside a project workspace. -->
  <nav class="rail">
    <router-link :to="{ name: 'Dashboard' }" class="rail__back">
      <FeatherIcon name="arrow-left" class="w-4 h-4" />
      <span>All projects</span>
    </router-link>

    <div class="rail__group">
      <router-link
        v-for="item in visibleItems"
        :key="item.name"
        :to="{ name: item.name, params: { projectId } }"
        class="rail__item"
        :class="{ 'rail__item--active': route.name === item.name }"
      >
        <FeatherIcon :name="item.icon" class="w-[18px] h-[18px]" />
        <span>{{ item.label }}</span>
        <span v-if="item.advanced" class="rail__adv">adv</span>
      </router-link>
    </div>

    <div class="rail__spacer" />

    <!-- Connection-health chip (static in Phase 0, wired in Phase 1) -->
    <div class="rail__health">
      <span class="rail__dot" />
      Connected
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { useMode } from '@/composables/useMode'

const props = defineProps({ projectId: { type: String, required: true } })
const route = useRoute()
const { isAdvanced } = useMode(props.projectId)

const items = [
  { name: 'ProjectOverview', label: 'Overview', icon: 'home' },
  { name: 'ProjectData', label: 'Data', icon: 'database' },
  { name: 'ProjectScreens', label: 'Screens', icon: 'layers' },
  { name: 'ProjectBuilder', label: 'Builder', icon: 'edit-3' },
  { name: 'ProjectFlow', label: 'Flow', icon: 'share-2', advanced: true },
  { name: 'ProjectPublish', label: 'Publish', icon: 'upload-cloud' },
]

// Advanced-only items hidden in simple mode (progressive disclosure).
const visibleItems = computed(() =>
  items.filter((i) => !i.advanced || isAdvanced.value)
)
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
.rail__back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  margin-bottom: 8px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-subtle);
  border-radius: var(--radius-control);
}
.rail__back:hover { color: var(--text); background: var(--surface-muted); }
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
.rail__item--active { background: var(--brand-subtle); color: var(--brand); }
.rail__adv {
  margin-left: auto;
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-subtle);
}
.rail__health {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 10px;
  font-size: 12px;
  color: var(--text-muted);
}
.rail__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ok);
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.15);
}
</style>
