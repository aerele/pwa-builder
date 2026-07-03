<template>
  <!-- Friendly mini app-screen mock used as a project card thumbnail.
       Light, abstract UI preview (not a dark phone). A gentle per-project
       accent gives the grid variety while staying tasteful. -->
  <div class="thumb">
    <div class="thumb__bar" :style="barStyle">
      <span class="thumb__avatar">{{ initial }}</span>
      <span class="thumb__title-lines">
        <i class="ln ln--lg" />
        <i class="ln ln--sm" />
      </span>
    </div>
    <div class="thumb__body">
      <div class="thumb__cards">
        <span class="kpi" /><span class="kpi" />
      </div>
      <div v-for="n in 3" :key="n" class="thumb__row">
        <span class="bullet" :style="{ background: accent }" />
        <span class="row-ln" :class="{ 'row-ln--short': n === 2 }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: 'App' },
})

// Curated, on-brand accent palette; pick deterministically from the title.
const palette = ['#4F46E5', '#0EA5A4', '#D97706', '#E11D48', '#7C3AED', '#2563EB']
const accent = computed(() => {
  let h = 0
  for (const ch of props.title) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  return palette[h % palette.length]
})
const barStyle = computed(() => ({
  background: `linear-gradient(135deg, ${accent.value}, ${accent.value}cc)`,
}))
const initial = computed(() => (props.title || 'A').trim().charAt(0).toUpperCase())
</script>

<style scoped>
.thumb {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
}
.thumb__bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
}
.thumb__avatar {
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 7px;
  flex-shrink: 0;
}
.thumb__title-lines { display: flex; flex-direction: column; gap: 4px; }
.thumb__title-lines .ln { display: block; height: 5px; border-radius: 3px; background: rgba(255, 255, 255, 0.7); }
.ln--lg { width: 64px; }
.ln--sm { width: 38px; background: rgba(255, 255, 255, 0.45) !important; }

.thumb__body { flex: 1; padding: 12px 14px; display: flex; flex-direction: column; gap: 9px; }
.thumb__cards { display: flex; gap: 8px; }
.kpi {
  flex: 1; height: 26px; border-radius: 7px;
  background: var(--surface-muted, #f7f8fa);
  border: 1px solid var(--border, #e5e7eb);
}
.thumb__row { display: flex; align-items: center; gap: 8px; }
.bullet { width: 14px; height: 14px; border-radius: 5px; opacity: 0.85; flex-shrink: 0; }
.row-ln { flex: 1; height: 8px; border-radius: 4px; background: var(--surface-muted, #f1f2f4); }
.row-ln--short { max-width: 60%; }
</style>
