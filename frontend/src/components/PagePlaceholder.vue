<template>
  <!-- Shared skeleton for Phase 0 stub pages. Real content lands in later
       phases; this keeps the shell navigable and the IA verifiable now. -->
  <section class="ph">
    <div class="ph__head">
      <div>
        <h1 class="ph__title">{{ title }}</h1>
        <p v-if="subtitle" class="ph__subtitle">{{ subtitle }}</p>
      </div>
      <span class="ph__phase">{{ phase }}</span>
    </div>
    <div class="ph__canvas">
      <FeatherIcon :name="icon" class="w-7 h-7" />
      <p>{{ title }} — coming in {{ phase }}</p>
      <slot />
    </div>
  </section>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: 'square' },
  phase: { type: String, default: 'a later phase' },
})
</script>

<style scoped>
.ph { padding: 24px; max-width: 1100px; margin: 0 auto; }
.ph__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}
.ph__title { font-size: 22px; font-weight: 650; color: var(--text); }
.ph__subtitle { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }
.ph__phase {
  font-size: 11px;
  font-weight: 600;
  color: var(--brand);
  background: var(--brand-subtle);
  padding: 4px 10px;
  border-radius: 999px;
}
.ph__canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 320px;
  color: var(--text-subtle);
  font-size: 14px;
  background: var(--surface);
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius-card);
}
</style>
