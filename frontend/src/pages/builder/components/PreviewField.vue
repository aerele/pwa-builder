<template>
  <!-- Static, realistic rendering of one field inside the phone preview. -->
  <div class="pf" :class="{ 'pf--selected': selected }" role="group">
    <!-- Number Card -->
    <div v-if="field.fieldtype === 'Number Card'" class="pf__card">
      <span class="pf__card-label">{{ field.label }}</span>
      <span class="pf__card-value">128</span>
    </div>

    <!-- Checkbox -->
    <label v-else-if="field.fieldtype === 'Check'" class="pf__check">
      <span class="pf__check-box" aria-hidden="true"></span>
      <span class="pf__label pf__label--inline"
        >{{ field.label }}<b v-if="field.reqd" class="pf__req">*</b></span
      >
    </label>

    <!-- Everything else: label + control mock -->
    <div v-else class="pf__stack">
      <div class="pf__label">
        {{ field.label }}<b v-if="field.reqd" class="pf__req">*</b>
      </div>

      <!-- Select / naming series -->
      <div v-if="field.fieldtype === 'Select' || isSeries" class="pf__input pf__input--row">
        <span class="pf__value" :class="{ 'pf__value--empty': !selectDisplay }">{{
          selectDisplay || 'Select…'
        }}</span>
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
        <span class="pf__value pf__value--empty">{{ numberPlaceholder }}</span>
      </div>

      <!-- Long text -->
      <div v-else-if="isTextarea" class="pf__input pf__input--area">
        <span class="pf__value pf__value--empty">{{ field.label }}</span>
      </div>

      <!-- Attach -->
      <div v-else-if="isAttach" class="pf__attach">
        <FeatherIcon :name="field.fieldtype === 'Attach Image' ? 'image' : 'upload'" class="pf__icon" />
        <span>{{ field.fieldtype === 'Attach Image' ? 'Add image' : 'Attach file' }}</span>
      </div>

      <!-- Rating -->
      <div v-else-if="field.fieldtype === 'Rating'" class="pf__rating">
        <span v-for="n in 5" :key="n" class="pf__star">★</span>
      </div>

      <!-- Color -->
      <div v-else-if="field.fieldtype === 'Color'" class="pf__input pf__input--row">
        <span class="pf__swatch"></span>
        <span class="pf__value pf__value--empty">Pick a color</span>
      </div>

      <!-- Child table -->
      <div v-else-if="field.fieldtype === 'Table'" class="pf__table">
        <div class="pf__table-head">
          <span v-for="c in tableColumns" :key="c">{{ c }}</span>
        </div>
        <div v-for="n in 2" :key="n" class="pf__table-row">
          <span v-for="c in tableColumns" :key="c" class="pf__table-cell"></span>
        </div>
        <div class="pf__table-add"><FeatherIcon name="plus" class="pf__icon" /> Add row</div>
      </div>

      <!-- HTML / HTML Editor -->
      <div v-else-if="isHtml" class="pf__html">
        <span class="pf__value pf__value--empty">HTML content</span>
      </div>

      <!-- Default: plain text input -->
      <div v-else class="pf__input pf__input--row">
        <span class="pf__value pf__value--empty">{{
          field.read_only ? '—' : field.label || 'Enter value'
        }}</span>
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
const isNumber = computed(() =>
  ['Int', 'Float', 'Currency', 'Percent', 'Duration'].includes(props.field.fieldtype)
)
const isTextarea = computed(() =>
  ['Text', 'Small Text', 'Long Text', 'Text Editor', 'Markdown Editor', 'Code', 'JSON'].includes(
    props.field.fieldtype
  )
)
const isAttach = computed(() => ['Attach', 'Attach Image', 'Signature'].includes(props.field.fieldtype))
const isHtml = computed(() => ['HTML', 'HTML Editor'].includes(props.field.fieldtype))
const isSeries = computed(
  () => props.field.fieldname === 'naming_series' || props.field.fieldtype === 'Autocomplete'
)

const firstOption = computed(() => {
  const opts = props.field.options
  if (typeof opts !== 'string') return ''
  // Naming series lines often look like "ACC-PINV-.YYYY.-" — still show first clean line
  return (
    opts
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)[0] || ''
  )
})

const selectDisplay = computed(() => {
  if (isSeries.value && firstOption.value) return firstOption.value
  if (props.field.fieldtype === 'Select') return firstOption.value
  return ''
})

const linkPlaceholder = computed(() =>
  typeof props.field.options === 'string' && props.field.options
    ? `Select ${props.field.options}`
    : 'Select…'
)

const datePlaceholder = computed(() => {
  if (props.field.fieldtype === 'Time') return '00:00'
  if (props.field.fieldtype === 'Datetime') return 'dd-mm-yyyy 00:00'
  return 'dd-mm-yyyy'
})

const numberPlaceholder = computed(() => {
  if (props.field.fieldtype === 'Currency') return '0.00'
  if (props.field.fieldtype === 'Percent') return '0%'
  return '0'
})

// Table columns come from the picked child fields (array) stored in options.
const tableColumns = computed(() => {
  const opts = props.field.options
  if (Array.isArray(opts) && opts.length) return opts.slice(0, 3).map((c) => c.label || c.fieldname)
  return ['Column 1', 'Column 2']
})
</script>

<style scoped>
.pf {
  padding: 1px;
  border-radius: 8px;
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
}
.pf--selected {
  outline: 2px solid #345086;
  outline-offset: 2px;
}

.pf__stack {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.pf__label {
  font-size: 11.5px;
  font-weight: 550;
  color: #6b7280;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pf__label--inline {
  margin-bottom: 0;
  white-space: normal;
}
.pf__req {
  color: #dc2626;
  margin-left: 2px;
  font-weight: 700;
}

.pf__input {
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-height: 36px;
  padding: 0 10px;
}
.pf__input--row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.pf__input--area {
  min-height: 68px;
  padding: 8px 10px;
  align-items: flex-start;
}
.pf__value {
  flex: 1;
  min-width: 0;
  font-size: 12.5px;
  line-height: 1.3;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pf__value--empty {
  color: #9ca3af;
}
.pf__icon {
  width: 14px !important;
  height: 14px !important;
  min-width: 14px;
  color: #9ca3af;
  flex: none;
}

.pf__check {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
}
.pf__check-box {
  width: 16px;
  height: 16px;
  border: 1.5px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  flex: none;
}

.pf__attach {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 48px;
  border: 1.5px dashed #d1d5db;
  border-radius: 8px;
  color: #9ca3af;
  font-size: 12px;
  background: #ffffff;
}

.pf__card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
}
.pf__card-label {
  font-size: 11px;
  font-weight: 550;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.pf__card-value {
  font-size: 22px;
  font-weight: 650;
  color: #111827;
}

.pf__table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  font-size: 11px;
  background: #ffffff;
}
.pf__table-head {
  display: flex;
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}
.pf__table-head span {
  flex: 1;
  min-width: 0;
  padding: 6px 8px;
  font-weight: 600;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pf__table-row {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}
.pf__table-cell {
  flex: 1;
  height: 26px;
}
.pf__table-add {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 8px;
  color: #9ca3af;
}

.pf__rating {
  display: flex;
  gap: 4px;
  color: #d1d5db;
  font-size: 16px;
  letter-spacing: 1px;
}
.pf__star:first-child {
  color: #f59e0b;
}

.pf__swatch {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(135deg, #345086, #8499bd);
  flex: none;
  border: 1px solid #e5e7eb;
}

.pf__html {
  min-height: 48px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px dashed #e5e7eb;
  background: #ffffff;
}
</style>
