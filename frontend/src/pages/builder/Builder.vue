<template>
  <div class="bld">
    <!-- Loading / empty states -->
    <div v-if="state.screensLoading.value" class="bld__center"><Spinner class="w-8" /></div>

    <div v-else-if="!state.screens.value.length" class="bld__center bld__none">
      <FeatherIcon name="layers" class="w-8 h-8" />
      <h2>No screens yet</h2>
      <p>Create your first screen, then come back to design it.</p>
      <router-link class="bld__cta" :to="{ name: 'ProjectScreens', params: { projectId } }">
        Go to Screens
      </router-link>
    </div>

    <template v-else-if="state.screen.value">
      <!-- Builder toolbar -->
      <div class="bld__bar">
        <router-link class="bld__back" :to="{ name: 'ProjectScreens', params: { projectId } }" title="Back to screens">
          <FeatherIcon name="arrow-left" class="w-4 h-4" />
        </router-link>

        <select class="bld__switch" :value="state.screen.value.name" @change="switchScreen($event.target.value)">
          <option v-for="s in state.screens.value" :key="s.name" :value="s.name">{{ s.title }}</option>
        </select>
        <span v-if="state.dirty.value" class="bld__dirty" title="Unsaved changes"></span>

        <div class="bld__bar-mid">
          <button class="bld__tool" :disabled="!state.canUndo.value" title="Undo (Ctrl+Z)" @click="state.undo">
            <FeatherIcon name="corner-up-left" class="w-4 h-4" />
          </button>
          <button class="bld__tool" :disabled="!state.canRedo.value" title="Redo (Ctrl+Shift+Z)" @click="state.redo">
            <FeatherIcon name="corner-up-right" class="w-4 h-4" />
          </button>
        </div>

        <div class="bld__bar-right">
          <button class="bld__btn" :disabled="!state.screens.value.length || validating" @click="validateForms">
            <FeatherIcon :name="validating ? 'loader' : 'check-square'" class="w-3.5 h-3.5" :class="{ spin: validating }" />
            Validate
          </button>
          <router-link class="bld__btn" :to="{ name: 'ProjectPublish', params: { projectId } }">
            <FeatherIcon name="upload-cloud" class="w-3.5 h-3.5" /> Publish
          </router-link>
          <button class="bld__btn bld__btn--primary" :disabled="!state.dirty.value || state.saving.value" @click="saveScreen">
            <FeatherIcon :name="state.saving.value ? 'loader' : 'save'" class="w-3.5 h-3.5" :class="{ spin: state.saving.value }" />
            Save
          </button>
        </div>
      </div>

      <p v-if="state.loadError.value" class="bld__err">
        <FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ state.loadError.value }}
      </p>

      <!-- 3 panes: palette/inspector · canvas · live preview -->
      <div class="bld__panes">
        <aside class="bld__left">
          <div class="bld__tabs">
            <button class="bld__tab" :class="{ 'bld__tab--on': tab === 'insert' }" @click="tab = 'insert'">Insert</button>
            <button
              class="bld__tab"
              :class="{ 'bld__tab--on': tab === 'inspect' }"
              :disabled="!state.selectedField.value"
              @click="tab = 'inspect'"
            >
              Inspect
            </button>
          </div>
          <PalettePane
            v-if="tab === 'insert'"
            :palette="state.palette.value"
            :loading="state.metaLoading.value"
            :is-dashboard="state.isDashboard.value"
            @add="state.addField"
          />
          <InspectorPane
            v-else
            :field="state.selectedField.value"
            :child-meta="state.childMeta.value"
            :is-advanced="isAdvanced"
            @commit="state.commit"
            @remove="state.removeField"
          />
        </aside>

        <section class="bld__mid">
          <CanvasPane
            :fields="state.canvasFields.value"
            :selected="state.selected.value"
            :missing-required="state.missingRequired.value"
            @select="onSelect"
            @remove="state.removeField"
            @add="state.addField"
            @changed="onCanvasChanged"
          />
        </section>

        <aside class="bld__right">
          <PreviewPane
            :fields="state.canvasFields.value"
            :title="state.screen.value.title"
            :selected="state.selected.value"
            :is-dashboard="state.isDashboard.value"
            :is-submittable="state.isSubmittable.value"
            @select="onSelect"
          />
        </aside>
      </div>
    </template>

    <!-- Validation results -->
    <Dialog v-model="showValidation">
      <template #body-title><h3 class="font-semibold">Validation results</h3></template>
      <template #body-content>
        <div class="bld__val">
          <div v-for="r in validationRows" :key="r.form" class="bld__val-row">
            <span>{{ r.form }}</span>
            <Badge v-if="r.ok" theme="green" variant="subtle">Ready</Badge>
            <span v-else class="bld__val-missing">Missing: {{ r.missing.join(', ') }}</span>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { Badge, Dialog, FeatherIcon, Spinner, createResource, toast } from 'frappe-ui'
import { useMode } from '@/composables/useMode'
import { useBuilderState } from './composables/useBuilderState'
import PalettePane from './components/PalettePane.vue'
import CanvasPane from './components/CanvasPane.vue'
import InspectorPane from './components/InspectorPane.vue'
import PreviewPane from './components/PreviewPane.vue'

const props = defineProps({
  projectId: { type: String, required: true },
  screenId: { type: String, default: '' },
})

const router = useRouter()
const { isAdvanced } = useMode(props.projectId)
const state = useBuilderState(props.projectId)

const tab = ref('insert')
const validating = ref(false)
const showValidation = ref(false)
const validationRows = ref([])

onMounted(async () => {
  await state.loadScreens()
  if (!state.screens.value.length) return
  const target = state.screens.value.find((s) => s.name === props.screenId) || state.screens.value[0]
  await state.openScreen(target.name)
  if (target.name !== props.screenId) {
    router.replace({ name: 'ProjectBuilder', params: { projectId: props.projectId, screenId: target.name } })
  }
})

// Route-driven screen changes (switcher, back/forward).
watch(
  () => props.screenId,
  async (name) => {
    if (name && state.screens.value.some((s) => s.name === name) && state.screen.value?.name !== name) {
      await state.openScreen(name)
      tab.value = 'insert'
    }
  }
)

function switchScreen(name) {
  if (name === state.screen.value?.name) return
  if (state.dirty.value && !confirm('You have unsaved changes. Switch screens anyway?')) return
  router.push({ name: 'ProjectBuilder', params: { projectId: props.projectId, screenId: name } })
}

function onSelect(fieldname) {
  state.select(fieldname)
  tab.value = fieldname ? 'inspect' : 'insert'
}

// Drag mutates the canvas array directly; snapshot it, and select drops.
function onCanvasChanged() {
  state.commit()
}

async function saveScreen() {
  const ok = await state.save()
  if (ok) {
    toast({
      title: 'Saved',
      text: `${state.screen.value.title} saved.`,
      icon: 'check-circle',
      position: 'bottom-right',
      iconClasses: 'text-green-500',
    })
  }
}

async function validateForms() {
  if (state.dirty.value && !(await state.save())) return
  validating.value = true
  try {
    const res = await createResource({ url: 'pwa_builder.api.validate_form_fields' }).submit({
      project_name: props.projectId,
    })
    if (res?.success) {
      validationRows.value = state.screens.value.map((s) => ({ form: s.title, ok: true, missing: [] }))
    } else {
      const missing = res?.forms_with_missing_fields || {}
      // Values are labels, nested one level deeper for child-table fields.
      validationRows.value = Object.entries(missing).map(([form, fields]) => ({
        form,
        ok: false,
        missing: Object.values(fields || {}).flatMap((v) =>
          v && typeof v === 'object' ? Object.values(v) : [v]
        ),
      }))
      if (!validationRows.value.length) {
        toast({
          title: 'Validation failed',
          text: res?.message || 'Some screens are not ready.',
          icon: 'x',
          position: 'bottom-right',
          iconClasses: 'text-red-500',
        })
        return
      }
    }
    showValidation.value = true
  } catch (e) {
    toast({
      title: 'Error',
      text: (e && e.messages && e.messages[0]) || 'Validation failed.',
      icon: 'x',
      position: 'bottom-right',
      iconClasses: 'text-red-500',
    })
  } finally {
    validating.value = false
  }
}

// --- keyboard shortcuts ---
function isTyping(e) {
  return ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName) || e.target.isContentEditable
}

function onKeydown(e) {
  const mod = e.ctrlKey || e.metaKey
  if (mod && e.key.toLowerCase() === 's') {
    e.preventDefault()
    if (state.dirty.value) saveScreen()
    return
  }
  if (isTyping(e)) return
  if (mod && e.key.toLowerCase() === 'z') {
    e.preventDefault()
    e.shiftKey ? state.redo() : state.undo()
  } else if (mod && e.key.toLowerCase() === 'y') {
    e.preventDefault()
    state.redo()
  } else if ((e.key === 'Delete' || e.key === 'Backspace') && state.selected.value) {
    e.preventDefault()
    state.removeField(state.selected.value)
  }
}

function onBeforeUnload(e) {
  if (state.dirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('beforeunload', onBeforeUnload)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('beforeunload', onBeforeUnload)
})

onBeforeRouteLeave((to) => {
  // Screen switches inside the builder are guarded in switchScreen already.
  if (to.name === 'ProjectBuilder') return true
  if (state.dirty.value && !confirm('You have unsaved changes. Leave the builder anyway?')) return false
  return true
})
</script>

<style scoped>
.bld { height: 100%; display: flex; flex-direction: column; }
.bld__center { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }
.bld__none { color: var(--text-subtle); }
.bld__none h2 { font-size: 16px; font-weight: 650; color: var(--text); }
.bld__none p { font-size: 13px; color: var(--text-muted); }
.bld__cta { margin-top: 6px; padding: 8px 16px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand); border-radius: var(--radius-control); }
.bld__cta:hover { background: var(--brand-hover); }

.bld__bar { display: flex; align-items: center; gap: 10px; height: 50px; padding: 0 14px; background: var(--surface); border-bottom: 1px solid var(--border); flex: none; }
.bld__back { display: grid; place-items: center; width: 30px; height: 30px; color: var(--text-muted); border-radius: var(--radius-control); }
.bld__back:hover { color: var(--text); background: var(--surface-muted); }
.bld__switch { max-width: 220px; padding: 6px 8px; font-size: 13px; font-weight: 600; color: var(--text); background: transparent; border: 1px solid transparent; border-radius: var(--radius-control); outline: none; cursor: pointer; }
.bld__switch:hover { border-color: var(--border-strong); background: var(--surface); }
.bld__dirty { width: 8px; height: 8px; border-radius: 50%; background: var(--warn); flex: none; }

.bld__bar-mid { display: flex; gap: 2px; margin-left: 8px; }
.bld__tool { display: grid; place-items: center; width: 30px; height: 30px; color: var(--text-muted); border-radius: var(--radius-control); }
.bld__tool:hover:not(:disabled) { color: var(--text); background: var(--surface-muted); }
.bld__tool:disabled { opacity: 0.35; cursor: not-allowed; }

.bld__bar-right { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.bld__btn { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; font-size: 12.5px; font-weight: 550; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-control); }
.bld__btn:hover:not(:disabled) { background: var(--surface-muted); }
.bld__btn:disabled { opacity: 0.5; cursor: not-allowed; }
.bld__btn--primary { color: var(--brand-fg); background: var(--brand); border-color: var(--brand); }
.bld__btn--primary:hover:not(:disabled) { background: var(--brand-hover); }

.bld__err { display: flex; align-items: center; gap: 6px; padding: 8px 14px; font-size: 12.5px; color: var(--danger); background: rgba(220, 38, 38, 0.06); border-bottom: 1px solid rgba(220, 38, 38, 0.15); }

.bld__panes { flex: 1; min-height: 0; display: grid; grid-template-columns: 280px minmax(0, 1fr) minmax(300px, 380px); }
.bld__left { display: flex; flex-direction: column; min-height: 0; background: var(--surface); border-right: 1px solid var(--border); }
.bld__tabs { display: flex; gap: 4px; padding: 10px 12px 0; border-bottom: 1px solid var(--border); }
.bld__tab { padding: 7px 12px; font-size: 12.5px; font-weight: 550; color: var(--text-muted); border-bottom: 2px solid transparent; margin-bottom: -1px; }
.bld__tab--on { color: var(--text); border-bottom-color: var(--brand); }
.bld__tab:disabled { opacity: 0.4; cursor: not-allowed; }
.bld__mid { min-height: 0; }
.bld__right { min-height: 0; border-left: 1px solid var(--border); padding: 12px; }

.bld__val { display: flex; flex-direction: column; gap: 10px; }
.bld__val-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 13.5px; color: var(--text); }
.bld__val-missing { font-size: 12px; color: var(--danger); text-align: right; }

.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
