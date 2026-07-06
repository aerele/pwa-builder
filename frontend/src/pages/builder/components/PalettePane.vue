<template>
  <div class="pal">
    <div class="pal__search">
      <FeatherIcon name="search" class="pal__search-icon" />
      <input v-model="query" class="pal__search-in" :placeholder="isDashboard ? 'Search number cards' : 'Search fields'" />
    </div>

    <div v-if="loading" class="pal__hint">Loading fields…</div>
    <div v-else-if="!filtered.length" class="pal__hint">
      {{ palette.length ? 'No matches.' : 'All fields are placed.' }}
    </div>

    <!-- Drag onto the canvas, or click to append. Clone-pull leaves this
         list untouched; placed fields drop out via the palette computed. -->
    <Draggable
      :list="filtered"
      :group="{ name: 'canvasFields', pull: 'clone', put: false }"
      :clone="cloneField"
      :sort="false"
      item-key="fieldname"
      class="pal__list"
    >
      <template #item="{ element }">
        <div class="pal__item" @click="$emit('add', element)">
          <span class="pal__item-icon"><FeatherIcon :name="iconFor(element)" class="w-3.5 h-3.5" /></span>
          <span class="pal__item-main">
            <span class="pal__item-label">{{ element.label }}<b v-if="element.reqd" class="pal__req">*</b></span>
            <span class="pal__item-type">{{ element.fieldtype }}<template v-if="element.fieldtype === 'Link'"> · {{ element.options }}</template></span>
          </span>
          <FeatherIcon name="plus" class="pal__item-add" />
        </div>
      </template>
    </Draggable>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Draggable from 'vuedraggable'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  palette: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  isDashboard: { type: Boolean, default: false },
})
defineEmits(['add'])

const query = ref('')

const filtered = computed(() => {
  if (!query.value) return props.palette
  const q = query.value.toLowerCase()
  return props.palette.filter(
    (f) => (f.label || '').toLowerCase().includes(q) || (f.fieldname || '').toLowerCase().includes(q)
  )
})

function cloneField(f) {
  return JSON.parse(JSON.stringify(f))
}

const ICONS = {
  Data: 'type',
  Select: 'chevron-down',
  Link: 'link',
  'Dynamic Link': 'link',
  Int: 'hash',
  Float: 'hash',
  Currency: 'dollar-sign',
  Percent: 'percent',
  Date: 'calendar',
  Datetime: 'calendar',
  Time: 'clock',
  Check: 'check-square',
  Attach: 'paperclip',
  'Attach Image': 'image',
  Table: 'grid',
  'Number Card': 'bar-chart-2',
}

function iconFor(f) {
  if (['Text', 'Small Text', 'Long Text', 'Text Editor', 'Markdown Editor', 'Code'].includes(f.fieldtype)) {
    return 'align-left'
  }
  return ICONS[f.fieldtype] || 'type'
}
</script>

<style scoped>
.pal { display: flex; flex-direction: column; height: 100%; }
.pal__search { position: relative; margin: 12px 12px 8px; }
.pal__search-icon { position: absolute; left: 9px; top: 50%; transform: translateY(-50%); width: 13px; height: 13px; color: var(--text-subtle); }
.pal__search-in { width: 100%; padding: 7px 10px 7px 28px; font-size: 12.5px; color: var(--text); background: var(--surface-muted); border: 1px solid var(--border); border-radius: var(--radius-control); outline: none; }
.pal__search-in:focus { border-color: var(--brand-500); background: var(--surface); }

.pal__hint { padding: 20px 14px; font-size: 12.5px; color: var(--text-subtle); text-align: center; }
.pal__list { flex: 1; overflow-y: auto; padding: 0 8px 12px; }

.pal__item { display: flex; align-items: center; gap: 9px; padding: 8px 9px; margin-bottom: 2px; border-radius: 8px; cursor: grab; border: 1px solid transparent; }
.pal__item:hover { background: var(--surface-muted); border-color: var(--border); }
.pal__item:hover .pal__item-add { opacity: 1; }
.pal__item-icon { display: grid; place-items: center; width: 26px; height: 26px; flex: none; color: var(--brand); background: var(--brand-subtle); border-radius: 7px; }
.pal__item-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.pal__item-label { font-size: 12.5px; font-weight: 550; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pal__item-type { font-size: 11px; color: var(--text-subtle); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pal__item-add { width: 13px; height: 13px; color: var(--text-subtle); opacity: 0; flex: none; }
.pal__req { color: var(--danger); margin-left: 2px; }
</style>
