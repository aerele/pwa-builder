<template>
  <!-- Static, realistic rendering of one field inside the phone preview. -->
  <div class="pf" :class="{ 'pf--selected': selected }">
    <!-- Number Card -->
    <div v-if="field.fieldtype === 'Number Card'" class="pf__card">
      <span class="pf__card-label">{{ field.label }}</span>
      <span class="pf__card-value">128</span>
    </div>

    <!-- Checkbox -->
    <label v-else-if="field.fieldtype === 'Check'" class="pf__check">
      <span class="pf__check-box"></span>
      <span class="pf__label pf__label--inline">{{ field.label }}<b v-if="field.reqd" class="pf__req">*</b></span>
    </label>

    <!-- Everything else gets a label + control mock -->
    <div v-else>
      <div class="pf__label">{{ field.label }}<b v-if="field.reqd" class="pf__req">*</b></div>

      <!-- Select -->
      <div v-if="field.fieldtype === 'Select'" class="pf__input pf__input--row">
        <span class="pf__value" :class="{ 'pf__value--empty': !firstOption }">{{ firstOption || 'Select…' }}</span>
        <FeatherIcon name="chevron-down" class="pf__icon" />
      </div>

      <!-- Link / Dynamic Link -->
      <div v-else-if="isLink" class="pf__input pf__input--row">
        <span class="pf__value pf__value--empty">{{ linkPlaceholder }}</span>
        <FeatherIcon name="search" class="pf__icon" />
      </div>

      <!-- Date / Datetime / Time -->
      <div v-else-if="isDate" class="pf__input pf__input--row">
        <span class="pf__value pf__value--empty">{{ datePlaceholder }}</span>
        <FeatherIcon :name="field.fieldtype === 'Time' ? 'clock' : 'calendar'" class="pf__icon" />
      </div>

      <!-- Numbers / Currency -->
      <div v-else-if="isNumber" class="pf__input pf__input--row">
        <span class="pf__value pf__value--empty">0{{ field.fieldtype === 'Currency' ? '.00' : '' }}</span>
      </div>

      <!-- Long text -->
      <div v-else-if="isTextarea" class="pf__input pf__input--area"></div>

      <!-- Attach -->
      <div v-else-if="isAttach" class="pf__attach">
        <FeatherIcon :name="field.fieldtype === 'Attach Image' ? 'image' : 'upload'" class="w-4 h-4" />
        <span>{{ field.fieldtype === 'Attach Image' ? 'Add image' : 'Attach file' }}</span>
      </div>

      <!-- Child table -->
      <div v-else-if="field.fieldtype === 'Table'" class="pf__table">
        <div class="pf__table-head">
          <span v-for="c in tableColumns" :key="c">{{ c }}</span>
        </div>
        <div v-for="n in 2" :key="n" class="pf__table-row">
          <span v-for="c in tableColumns" :key="c" class="pf__table-cell"></span>
        </div>
        <div class="pf__table-add"><FeatherIcon name="plus" class="w-3 h-3" /> Add row</div>
      </div>

      <!-- Default: plain text input -->
      <div v-else class="pf__input pf__input--row">
        <span class="pf__value pf__value--empty">{{ field.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  field: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

const isLink = computed(() => ['Link', 'Dynamic Link'].includes(props.field.fieldtype))
const isDate = computed(() => ['Date', 'Datetime', 'Time'].includes(props.field.fieldtype))
const isNumber = computed(() => ['Int', 'Float', 'Currency', 'Percent'].includes(props.field.fieldtype))
const isTextarea = computed(() =>
  ['Text', 'Small Text', 'Long Text', 'Text Editor', 'Markdown Editor', 'Code'].includes(props.field.fieldtype)
)
const isAttach = computed(() => ['Attach', 'Attach Image'].includes(props.field.fieldtype))

const firstOption = computed(() => {
  const opts = props.field.options
  if (typeof opts !== 'string') return ''
  return opts.split('\n').map((s) => s.trim()).filter(Boolean)[0] || ''
})

const linkPlaceholder = computed(() =>
  typeof props.field.options === 'string' && props.field.options ? `Select ${props.field.options}` : 'Select…'
)

const datePlaceholder = computed(() => {
  if (props.field.fieldtype === 'Time') return '00:00'
  if (props.field.fieldtype === 'Datetime') return 'dd-mm-yyyy 00:00'
  return 'dd-mm-yyyy'
})

// Table columns come from the picked child fields (array) stored in options.
const tableColumns = computed(() => {
  const opts = props.field.options
  if (Array.isArray(opts) && opts.length) return opts.slice(0, 3).map((c) => c.label || c.fieldname)
  return ['Column 1', 'Column 2']
})
</script>

<style scoped>
.pf { padding: 2px; border-radius: 8px; }
.pf--selected { outline: 2px solid var(--brand-500); outline-offset: 1px; }

.pf__label { font-size: 11.5px; font-weight: 550; color: var(--text-muted); margin-bottom: 4px; }
.pf__label--inline { margin-bottom: 0; }
.pf__req { color: var(--danger); margin-left: 2px; }

.pf__input { background: var(--surface-muted); border: 1px solid var(--border); border-radius: 8px; min-height: 34px; padding: 0 10px; }
.pf__input--row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.pf__input--area { min-height: 64px; }
.pf__value { font-size: 12.5px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pf__value--empty { color: var(--text-subtle); }
.pf__icon { width: 13px; height: 13px; color: var(--text-subtle); flex: none; }

.pf__check { display: flex; align-items: center; gap: 8px; min-height: 30px; }
.pf__check-box { width: 15px; height: 15px; border: 1.5px solid var(--border-strong); border-radius: 4px; background: var(--surface); flex: none; }

.pf__attach { display: flex; align-items: center; justify-content: center; gap: 7px; min-height: 46px; border: 1.5px dashed var(--border-strong); border-radius: 8px; color: var(--text-subtle); font-size: 12px; }

.pf__card { display: flex; flex-direction: column; gap: 4px; padding: 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; box-shadow: var(--shadow-sm); }
.pf__card-label { font-size: 11px; font-weight: 550; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.03em; }
.pf__card-value { font-size: 22px; font-weight: 650; color: var(--text); }

.pf__table { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; font-size: 11px; }
.pf__table-head { display: flex; background: var(--surface-muted); border-bottom: 1px solid var(--border); }
.pf__table-head span { flex: 1; padding: 6px 8px; font-weight: 600; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pf__table-row { display: flex; border-bottom: 1px solid var(--border); }
.pf__table-cell { flex: 1; height: 24px; }
.pf__table-add { display: flex; align-items: center; gap: 4px; padding: 6px 8px; color: var(--text-subtle); }
</style>
