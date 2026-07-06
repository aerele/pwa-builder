<template>
  <div class="cv" @click.self="$emit('select', null)">
    <!-- Inline mandatory-field hint -->
    <div v-if="missingRequired.length" class="cv__warn">
      <FeatherIcon name="alert-triangle" class="w-4 h-4 flex-none" />
      <span>
        {{ missingRequired.length }} required {{ missingRequired.length === 1 ? 'field is' : 'fields are' }} not on
        this screen:
        <button v-for="f in missingRequired" :key="f.fieldname" class="cv__warn-add" @click="$emit('add', f)">
          {{ f.label }}
        </button>
      </span>
    </div>

    <Draggable
      :list="fields"
      group="canvasFields"
      item-key="fieldname"
      handle=".cv__grip"
      ghost-class="cv__ghost"
      class="cv__list"
      @change="$emit('changed')"
    >
      <template #item="{ element }">
        <div
          class="cv__row"
          :class="{ 'cv__row--selected': element.fieldname === selected }"
          @click="$emit('select', element.fieldname)"
        >
          <span class="cv__grip" @click.stop>
            <FeatherIcon name="menu" class="w-3.5 h-3.5" />
          </span>
          <span class="cv__main">
            <span class="cv__label">{{ element.label }}<b v-if="element.reqd" class="cv__req">*</b></span>
            <span class="cv__type">{{ element.fieldtype }}</span>
          </span>
          <button class="cv__del" title="Remove field" @click.stop="$emit('remove', element.fieldname)">
            <FeatherIcon name="x" class="w-3.5 h-3.5" />
          </button>
        </div>
      </template>
      <template #footer>
        <div v-if="!fields.length" class="cv__empty">
          <FeatherIcon name="move" class="w-6 h-6" />
          <p>Drag fields here from the left,<br />or click one to add it.</p>
        </div>
      </template>
    </Draggable>
  </div>
</template>

<script setup>
import Draggable from 'vuedraggable'
import { FeatherIcon } from 'frappe-ui'

defineProps({
  fields: { type: Array, required: true },
  selected: { type: String, default: null },
  missingRequired: { type: Array, default: () => [] },
})
defineEmits(['select', 'remove', 'add', 'changed'])
</script>

<style scoped>
.cv { height: 100%; overflow-y: auto; padding: 16px; }

.cv__warn { display: flex; gap: 8px; align-items: baseline; padding: 10px 12px; margin-bottom: 12px; font-size: 12.5px; color: var(--warn); background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.25); border-radius: var(--radius-card); }
.cv__warn-add { margin-left: 6px; font-weight: 600; text-decoration: underline; text-underline-offset: 2px; color: inherit; }
.cv__warn-add:hover { color: var(--text); }

.cv__list { min-height: 120px; }
.cv__row { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 6px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); box-shadow: var(--shadow-sm); cursor: pointer; }
.cv__row:hover { border-color: var(--border-strong); }
.cv__row--selected { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }
.cv__ghost { opacity: 0.4; border-style: dashed; }

.cv__grip { color: var(--text-subtle); cursor: grab; padding: 2px; flex: none; }
.cv__grip:active { cursor: grabbing; }
.cv__main { flex: 1; min-width: 0; display: flex; align-items: baseline; gap: 8px; }
.cv__label { font-size: 13px; font-weight: 550; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cv__req { color: var(--danger); margin-left: 2px; }
.cv__type { font-size: 11px; color: var(--text-subtle); flex: none; }
.cv__del { color: var(--text-subtle); padding: 4px; border-radius: 6px; flex: none; }
.cv__del:hover { color: var(--danger); background: rgba(220, 38, 38, 0.08); }

.cv__empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 56px 20px; color: var(--text-subtle); font-size: 13px; text-align: center; border: 1.5px dashed var(--border-strong); border-radius: var(--radius-card); }
</style>
