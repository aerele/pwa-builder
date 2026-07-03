<template>
  <div class="ins">
    <div v-if="!field" class="ins__empty">
      <FeatherIcon name="mouse-pointer" class="w-5 h-5" />
      <p>Select a field on the canvas to edit it.</p>
    </div>

    <div v-else class="ins__body">
      <div class="ins__head">
        <span class="ins__type">{{ field.fieldtype }}</span>
        <span v-if="isAdvanced" class="ins__fieldname">{{ field.fieldname }}</span>
      </div>

      <label class="ins__group">
        <span class="ins__label">Label</span>
        <input v-model="field.label" class="ins__in" @change="$emit('commit')" />
      </label>

      <label v-if="field.fieldtype !== 'Number Card'" class="ins__row">
        <input type="checkbox" :checked="!!field.reqd" @change="setReqd($event.target.checked)" />
        <span>Required</span>
      </label>

      <label v-if="field.fieldtype !== 'Number Card'" class="ins__group">
        <span class="ins__label">Help text</span>
        <input
          :value="field.description || ''"
          class="ins__in"
          placeholder="Shown under the field"
          @change="setDescription($event.target.value)"
        />
      </label>

      <!-- Table column picker -->
      <div v-if="field.fieldtype === 'Table'" class="ins__group">
        <span class="ins__label">Table columns</span>
        <p v-if="!childFields.length" class="ins__hint">No columns available for {{ field.options || 'this table' }}.</p>
        <label v-for="c in childFields" :key="c.fieldname" class="ins__row ins__row--tight">
          <input type="checkbox" :checked="isColumnPicked(c)" @change="toggleColumn(c, $event.target.checked)" />
          <span>{{ c.label }}</span>
        </label>
      </div>

      <!-- Advanced: raw field JSON -->
      <div v-if="isAdvanced" class="ins__group">
        <span class="ins__label">Field JSON</span>
        <textarea v-model="rawJson" class="ins__json" rows="9" spellcheck="false" @change="applyJson"></textarea>
        <p v-if="jsonError" class="ins__err">{{ jsonError }}</p>
      </div>

      <button class="ins__remove" @click="$emit('remove', field.fieldname)">
        <FeatherIcon name="trash-2" class="w-3.5 h-3.5" /> Remove from screen
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  field: { type: Object, default: null }, // the selected canvas field (mutated in place)
  childMeta: { type: Object, default: () => ({}) },
  isAdvanced: { type: Boolean, default: false },
})
const emit = defineEmits(['commit', 'remove'])

const childFields = computed(() => (props.field ? props.childMeta[props.field.fieldname] || [] : []))

function setReqd(checked) {
  props.field.reqd = checked ? 1 : 0
  emit('commit')
}

function setDescription(value) {
  props.field.description = value
  emit('commit')
}

// Picked columns live in field.options as an array (the format the old
// builder and the export template already use). A string means none picked.
function isColumnPicked(c) {
  return Array.isArray(props.field.options) && props.field.options.some((o) => o.fieldname === c.fieldname)
}

function toggleColumn(c, checked) {
  let picked = Array.isArray(props.field.options) ? props.field.options : []
  if (checked) {
    picked = [...picked, JSON.parse(JSON.stringify(c))]
  } else {
    picked = picked.filter((o) => o.fieldname !== c.fieldname)
  }
  // Keep the child-doctype name recoverable when nothing is picked.
  props.field.options = picked.length ? picked : childFields.value[0]?.parent || props.field.options
  emit('commit')
}

// --- advanced raw JSON ---
const rawJson = ref('')
const jsonError = ref('')

watch(
  () => props.field,
  (f) => {
    rawJson.value = f ? JSON.stringify(f, null, 2) : ''
    jsonError.value = ''
  },
  { immediate: true, deep: true }
)

function applyJson() {
  if (!props.field) return
  try {
    const next = JSON.parse(rawJson.value)
    if (!next.fieldname || !next.fieldtype) throw new Error('fieldname and fieldtype are required')
    Object.keys(props.field).forEach((k) => delete props.field[k])
    Object.assign(props.field, next)
    jsonError.value = ''
    emit('commit')
  } catch (e) {
    jsonError.value = e.message || 'Invalid JSON'
  }
}
</script>

<style scoped>
.ins { height: 100%; overflow-y: auto; }
.ins__empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 44px 20px; color: var(--text-subtle); font-size: 12.5px; text-align: center; }

.ins__body { display: flex; flex-direction: column; gap: 14px; padding: 14px; }
.ins__head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.ins__type { font-size: 10.5px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.04em; color: var(--brand); background: var(--brand-subtle); padding: 3px 8px; border-radius: 999px; }
.ins__fieldname { font-size: 11px; font-family: ui-monospace, monospace; color: var(--text-subtle); overflow: hidden; text-overflow: ellipsis; }

.ins__group { display: flex; flex-direction: column; gap: 5px; }
.ins__label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }
.ins__in { padding: 7px 10px; font-size: 13px; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-control); outline: none; }
.ins__in:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }

.ins__row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text); cursor: pointer; }
.ins__row--tight { font-size: 12.5px; }
.ins__row input { accent-color: var(--brand); }
.ins__hint { font-size: 12px; color: var(--text-subtle); }

.ins__json { padding: 8px 10px; font-size: 11.5px; font-family: ui-monospace, monospace; color: var(--text); background: var(--surface-muted); border: 1px solid var(--border); border-radius: var(--radius-control); outline: none; resize: vertical; }
.ins__json:focus { border-color: var(--brand-500); background: var(--surface); }
.ins__err { font-size: 12px; color: var(--danger); }

.ins__remove { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px; margin-top: 4px; font-size: 12.5px; font-weight: 550; color: var(--danger); border: 1px solid rgba(220, 38, 38, 0.3); border-radius: var(--radius-control); }
.ins__remove:hover { background: rgba(220, 38, 38, 0.06); }
</style>
