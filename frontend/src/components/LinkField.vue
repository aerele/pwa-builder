<!--
  Frappe Link search, styled for PWA Builder design tokens.
  Uses frappe-ui Autocomplete + frappe.desk.search.search_link.
-->
<template>
  <Autocomplete
    ref="autocompleteRef"
    v-model="value"
    :placeholder="placeholder"
    :options="options.data || []"
    :class="['lf', disabled ? 'lf--disabled' : '', sizeClass]"
    :body-classes="dropdownBodyClass"
    :disabled="disabled"
    @update:query="handleQueryUpdate"
  >
    <!-- Custom trigger — matches .add__in / .nw__in / .ins__in -->
    <template #target="{ togglePopover }">
      <button
        type="button"
        class="lf__trigger"
        :disabled="disabled"
        @click="onTriggerClick(togglePopover)"
      >
        <FeatherIcon name="search" class="lf__search-ico" aria-hidden="true" />
        <span class="lf__value" :class="{ 'lf__value--empty': !displayLabel }">
          {{ displayLabel || placeholder }}
        </span>
        <span
          v-if="displayLabel && !disabled"
          class="lf__clear"
          title="Clear"
          role="button"
          tabindex="-1"
          @click.stop.prevent="clear"
        >
          <FeatherIcon name="x" class="lf__clear-ico" />
        </span>
        <FeatherIcon name="chevron-down" class="lf__chev" aria-hidden="true" />
      </button>
    </template>
  </Autocomplete>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Autocomplete, FeatherIcon, createResource, debounce } from 'frappe-ui'

const props = defineProps({
  /** Target DocType to search (e.g. "DocType", "Customer") */
  doctype: { type: String, required: true },
  modelValue: { type: String, default: '' },
  filters: { type: Object, default: () => ({}) },
  placeholder: { type: String, default: 'Type to search…' },
  disabled: { type: Boolean, default: false },
  /** Visual size: default | compact (inspector / tight forms) */
  size: { type: String, default: 'default' },
})

const emit = defineEmits(['update:modelValue'])

const autocompleteRef = ref(null)
const searchText = ref('')

const sizeClass = computed(() => (props.size === 'compact' ? 'lf--compact' : ''))
const dropdownBodyClass = 'lf-dropdown'

const value = computed({
  get: () => props.modelValue,
  set: (val) => {
    if (typeof val === 'string') {
      emit('update:modelValue', val)
    } else {
      emit('update:modelValue', val?.value || '')
    }
  },
})

const displayLabel = computed(() => {
  const v = props.modelValue
  if (!v) return ''
  if (typeof v === 'string') return v
  return v?.label || v?.value || ''
})

const options = createResource({
  url: 'frappe.desk.search.search_link',
  method: 'POST',
  params: {
    doctype: props.doctype,
    txt: searchText.value,
    filters: props.filters,
  },
  transform: (data) => {
    return (data || []).map((doc) => {
      let title = null
      if (doc.label && doc.label !== doc.value) {
        title = doc.label
      } else if (doc.description) {
        title = String(doc.description).split(',')[0]
      }
      return {
        label: title && title !== doc.value ? `${doc.value}` : doc.value,
        value: doc.value,
        description: title && title !== doc.value ? title : doc.description || '',
      }
    })
  },
})

function reloadOptions(txt) {
  options.update({
    params: {
      txt: txt || '',
      doctype: props.doctype,
      filters: props.filters,
    },
  })
  options.reload()
}

const handleQueryUpdate = debounce((newQuery) => {
  const val = newQuery || ''
  if (searchText.value === val) return
  searchText.value = val
  reloadOptions(val)
}, 300)

function onTriggerClick(togglePopover) {
  if (props.disabled) return
  togglePopover()
  // Load suggestions when opening (empty query = top matches)
  reloadOptions(searchText.value || '')
}

function clear() {
  emit('update:modelValue', '')
  searchText.value = ''
  reloadOptions('')
}

watch(
  () => props.doctype,
  () => {
    if (!props.doctype) return
    reloadOptions('')
  },
  { immediate: true },
)

watch(
  () => props.filters,
  () => reloadOptions(''),
  { deep: true },
)
</script>

<style scoped>
.lf {
  display: block;
  width: 100%;
  min-width: 0;
}
.lf--disabled {
  opacity: 0.55;
  pointer-events: none;
}

/* Trigger — same chrome as .add__in / .nw__in / .ins__in */
.lf__trigger {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 38px;
  padding: 9px 11px;
  margin: 0;
  text-align: left;
  font-size: 13px;
  line-height: 1.3;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-control);
  outline: none;
  cursor: pointer;
  transition: border-color 0.12s, box-shadow 0.12s, background 0.12s;
}
.lf__trigger:hover:not(:disabled) {
  border-color: var(--brand-400, var(--border-strong));
  background: var(--surface);
}
.lf__trigger:focus,
.lf__trigger:focus-visible {
  border-color: var(--brand-500);
  box-shadow: 0 0 0 3px var(--brand-ring);
}
.lf__trigger:disabled {
  cursor: not-allowed;
}

.lf--compact .lf__trigger {
  min-height: 34px;
  padding: 7px 10px;
}

.lf__search-ico {
  width: 14px;
  height: 14px;
  flex: none;
  color: var(--text-subtle);
}
.lf__value {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 450;
  color: var(--text);
}
.lf__value--empty {
  color: var(--text-subtle);
  font-weight: 400;
}
.lf__chev {
  width: 14px;
  height: 14px;
  flex: none;
  color: var(--text-subtle);
}
.lf__clear {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  flex: none;
  border-radius: 4px;
  color: var(--text-subtle);
}
.lf__clear:hover {
  color: var(--text);
  background: var(--surface-muted);
}
.lf__clear-ico {
  width: 12px;
  height: 12px;
}

/* Kill default frappe-ui gray button if target slot fails */
.lf :deep(> .w-full > button.flex) {
  display: none;
}
</style>

<!-- Dropdown panel is teleported / outside scoped tree — use global class from body-classes -->
<style>
.lf-dropdown {
  border: 1px solid var(--border-strong, #d1d5db) !important;
  border-radius: var(--radius-card, 12px) !important;
  background: var(--surface, #fff) !important;
  box-shadow: var(--shadow-md, 0 4px 16px rgba(16, 24, 40, 0.1)) !important;
  overflow: hidden;
  color: var(--text, #111827);
}
.lf-dropdown .form-input,
.lf-dropdown input[type='text'] {
  height: 34px !important;
  min-height: 34px !important;
  padding: 0 32px 0 10px !important;
  font-size: 13px !important;
  color: var(--text, #111827) !important;
  background: var(--surface, #fff) !important;
  border: 1px solid var(--border-strong, #d1d5db) !important;
  border-radius: var(--radius-control, 6px) !important;
  outline: none !important;
  box-shadow: none !important;
}
.lf-dropdown .form-input:focus,
.lf-dropdown input[type='text']:focus {
  border-color: var(--brand-500, #345086) !important;
  box-shadow: 0 0 0 3px var(--brand-ring, rgba(5, 16, 42, 0.2)) !important;
}
.lf-dropdown li {
  border-radius: var(--radius-control, 6px) !important;
  font-size: 13px !important;
  color: var(--text, #111827) !important;
}
.lf-dropdown li:hover,
.lf-dropdown li[data-headlessui-state*='active'],
.lf-dropdown .bg-gray-100 {
  background: var(--brand-subtle, #eef1f6) !important;
}
.lf-dropdown .text-gray-600,
.lf-dropdown .text-sm {
  color: var(--text-muted, #6b7280) !important;
  font-size: 11.5px !important;
}
.lf-dropdown .sticky {
  background: var(--surface, #fff) !important;
  border-bottom: 1px solid var(--border, #e5e7eb);
  margin-bottom: 4px;
}
/* Dark mode support via tokens */
.dark .lf-dropdown {
  background: var(--surface) !important;
  border-color: var(--border-strong) !important;
}
</style>
