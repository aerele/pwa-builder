<template>
  <!-- Simple/Advanced segmented control. Sits in the top bar. -->
  <div class="mode-toggle" role="tablist" aria-label="Builder mode">
    <button
      v-for="opt in options"
      :key="opt.value"
      role="tab"
      :aria-selected="mode === opt.value"
      class="mode-toggle__btn"
      :class="{ 'mode-toggle__btn--active': mode === opt.value }"
      @click="setMode(opt.value)"
    >
      <FeatherIcon :name="opt.icon" class="w-3.5 h-3.5" />
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { useMode } from '@/composables/useMode'

// Optional per-project scoping; null = global toggle.
const props = defineProps({ projectId: { type: String, default: null } })
const { mode, setMode } = useMode(props.projectId)

const options = [
  { value: 'simple', label: 'Simple', icon: 'zap' },
  { value: 'advanced', label: 'Advanced', icon: 'sliders' },
]
</script>

<style scoped>
.mode-toggle {
  display: inline-flex;
  padding: 2px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-control);
}
.mode-toggle__btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-muted);
  border-radius: calc(var(--radius-control) - 2px);
  transition: all 0.12s ease;
}
.mode-toggle__btn--active {
  background: var(--surface);
  color: var(--brand);
  box-shadow: var(--shadow-sm);
}
</style>
