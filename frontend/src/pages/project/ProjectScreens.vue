<template>
  <section class="scr">
    <header class="scr__head">
      <div>
        <h1 class="scr__title">Screens</h1>
        <p class="scr__sub">The screens that make up this PWA. Open one to design it.</p>
      </div>
      <button class="btn-primary" @click="openNew">
        <FeatherIcon name="plus" class="w-4 h-4" /> New screen
      </button>
    </header>

    <p v-if="error" class="scr__err"><FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ error }}</p>

    <div v-if="rows.loading && !list.length" class="scr__grid">
      <div v-for="n in 3" :key="n" class="scr__sk skeleton" />
    </div>

    <div v-else-if="list.length" class="scr__grid">
      <div v-for="s in list" :key="s.name" class="card" @click="openBuilder(s)">
        <div class="card__thumb">
          <PhoneFrame :width="340" :height="640" :scale="0.36" :device-frame="true">
            <div class="card__mini">
              <div class="card__mini-bar">{{ s.title }}</div>
              <div class="card__mini-body">
                <template v-if="fieldsOf(s).length">
                  <PreviewField v-for="f in fieldsOf(s).slice(0, 7)" :key="f.fieldname" :field="f" />
                </template>
                <div v-else class="card__mini-empty">Empty screen</div>
              </div>
            </div>
          </PhoneFrame>
        </div>
        <div class="card__foot">
          <div class="card__main">
            <div class="card__title">{{ s.title }}</div>
            <div class="card__sub">{{ s.doctype_name }} · {{ fieldsOf(s).length }} fields</div>
          </div>
          <span v-if="s.is_validated" class="tag tag--ok">Validated</span>
          <button class="card__act card__act--danger" title="Delete screen" @click.stop="removeScreen(s)">
            <FeatherIcon name="trash-2" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div v-else class="scr__empty">
      <FeatherIcon name="layers" class="w-7 h-7" />
      <h3>No screens yet</h3>
      <p>Each screen is built from a doctype. Create the first one to start designing.</p>
      <button class="btn-primary" @click="openNew"><FeatherIcon name="plus" class="w-4 h-4" /> New screen</button>
    </div>

    <!-- New screen dialog -->
    <Dialog v-model="showNew">
      <template #body-title><h3 class="font-semibold">New screen</h3></template>
      <template #body-content>
        <div class="nw">
          <div v-if="!hasDashboard" class="nw__kind">
            <button class="nw__kind-btn" :class="{ 'nw__kind-btn--on': kind === 'form' }" @click="kind = 'form'">
              <FeatherIcon name="file-text" class="w-4 h-4" /> Form screen
            </button>
            <button class="nw__kind-btn" :class="{ 'nw__kind-btn--on': kind === 'dashboard' }" @click="kind = 'dashboard'">
              <FeatherIcon name="layout" class="w-4 h-4" /> Dashboard
            </button>
          </div>

          <template v-if="kind === 'form'">
            <label class="nw__group">
              <span class="nw__label">Doctype</span>
              <input v-model="newDoctype" list="scr-doctypes" class="nw__in" placeholder="e.g. Task" />
              <datalist id="scr-doctypes">
                <option v-for="d in (doctypes.data || [])" :key="d.name" :value="d.name" />
              </datalist>
            </label>
            <label class="nw__group">
              <span class="nw__label">Screen title</span>
              <input v-model="newTitle" class="nw__in" :placeholder="newDoctype || 'Optional'" @keyup.enter="createScreen" />
            </label>
          </template>
          <p v-else class="nw__hint">A dashboard screen shows Number Cards from this site.</p>

          <div class="nw__actions">
            <button class="btn-primary" :disabled="creating || (kind === 'form' && !newDoctype)" @click="createScreen">
              <FeatherIcon :name="creating ? 'loader' : 'plus'" class="w-4 h-4" :class="{ spin: creating }" />
              Create & open
            </button>
          </div>
        </div>
      </template>
    </Dialog>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, FeatherIcon, createListResource, createResource } from 'frappe-ui'
import PhoneFrame from '@/components/PhoneFrame.vue'
import PreviewField from '@/pages/builder/components/PreviewField.vue'

const props = defineProps({ projectId: { type: String, required: true } })
const router = useRouter()

const error = ref('')
const showNew = ref(false)
const kind = ref('form')
const newDoctype = ref('')
const newTitle = ref('')
const creating = ref(false)

const rows = createListResource({
  doctype: 'PWA DocType',
  fields: ['name', 'title', 'doctype_name', 'field_list', 'is_validated'],
  filters: { project_name: props.projectId },
  orderBy: 'creation asc',
  pageLength: 99,
  auto: true,
})
const list = computed(() => rows.data || [])
const hasDashboard = computed(() => list.value.some((s) => s.title === 'Dashboard'))

const doctypes = createListResource({
  doctype: 'DocType',
  fields: ['name'],
  filters: { istable: 0, issingle: 0 },
  orderBy: 'name asc',
  pageLength: 0,
  auto: true,
})

function fieldsOf(s) {
  try {
    const parsed = s.field_list && s.field_list !== '{}' ? JSON.parse(s.field_list) : {}
    return parsed.pwa_form_fields || []
  } catch (e) {
    return []
  }
}

function openBuilder(s) {
  router.push({ name: 'ProjectBuilder', params: { projectId: props.projectId, screenId: s.name } })
}

function openNew() {
  kind.value = 'form'
  newDoctype.value = ''
  newTitle.value = ''
  showNew.value = true
}

async function createScreen() {
  if (creating.value) return
  error.value = ''
  creating.value = true
  try {
    const isDash = kind.value === 'dashboard'
    const doc = await createResource({ url: 'frappe.client.insert' }).submit({
      doc: {
        doctype: 'PWA DocType',
        project_name: props.projectId,
        doctype_name: isDash ? 'Number Card' : newDoctype.value,
        title: isDash ? 'Dashboard' : newTitle.value || newDoctype.value,
        field_list: '{}',
      },
    })
    showNew.value = false
    router.push({ name: 'ProjectBuilder', params: { projectId: props.projectId, screenId: doc.name } })
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not create the screen.'
    showNew.value = false
  } finally {
    creating.value = false
  }
}

async function removeScreen(s) {
  if (!confirm(`Delete the screen "${s.title}"? This cannot be undone.`)) return
  try {
    await createResource({ url: 'frappe.client.delete' }).submit({ doctype: 'PWA DocType', name: s.name })
    rows.reload()
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not delete the screen.'
  }
}
</script>

<style scoped>
.scr { padding: 24px; max-width: 1080px; margin: 0 auto; }
.scr__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.scr__title { font-size: 22px; font-weight: 650; color: var(--text); }
.scr__sub { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }
.scr__err { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--danger); margin-bottom: 12px; }

.scr__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.scr__sk { height: 300px; border-radius: var(--radius-card); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); box-shadow: var(--shadow-sm); overflow: hidden; cursor: pointer; transition: box-shadow 0.15s, border-color 0.15s; }
.card:hover { border-color: var(--border-strong); box-shadow: var(--shadow-md); }
.card__thumb { display: flex; justify-content: center; padding: 16px 16px 0; background: var(--surface-muted); }
.card__mini { display: flex; flex-direction: column; height: 100%; background: var(--surface); pointer-events: none; }
.card__mini-bar { padding: 26px 12px 10px; font-size: 13px; font-weight: 600; color: #fff; background: var(--brand-950); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card__mini-body { flex: 1; overflow: hidden; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.card__mini-empty { margin: auto; font-size: 13px; color: var(--text-subtle); }

.card__foot { display: flex; align-items: center; gap: 8px; padding: 12px 14px; }
.card__main { flex: 1; min-width: 0; }
.card__title { font-size: 14px; font-weight: 600; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card__sub { font-size: 12px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card__act { color: var(--text-subtle); padding: 6px; border-radius: var(--radius-control); flex: none; }
.card__act--danger:hover { color: var(--danger); background: rgba(220, 38, 38, 0.08); }
.tag { font-size: 10.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; padding: 3px 8px; border-radius: 999px; flex: none; }
.tag--ok { color: var(--ok); background: rgba(22, 163, 74, 0.1); }

.scr__empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 56px; text-align: center; color: var(--text-subtle); background: var(--surface); border: 1px dashed var(--border-strong); border-radius: var(--radius-card); }
.scr__empty h3 { font-size: 15px; font-weight: 650; color: var(--text); }
.scr__empty p { font-size: 13px; color: var(--text-muted); max-width: 360px; }

.nw { display: flex; flex-direction: column; gap: 14px; }
.nw__kind { display: flex; gap: 8px; }
.nw__kind-btn { display: flex; align-items: center; gap: 7px; flex: 1; justify-content: center; padding: 9px; font-size: 13px; font-weight: 550; color: var(--text-muted); border: 1px solid var(--border-strong); border-radius: var(--radius-control); }
.nw__kind-btn--on { color: var(--brand); border-color: var(--brand-500); background: var(--brand-subtle); }
.nw__group { display: flex; flex-direction: column; gap: 5px; }
.nw__label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }
.nw__in { padding: 9px 11px; font-size: 13px; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-control); outline: none; }
.nw__in:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }
.nw__hint { font-size: 13px; color: var(--text-muted); }
.nw__actions { display: flex; justify-content: flex-end; }

.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 9px 14px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand-950); border-radius: var(--radius-control); }
.btn-primary:hover { background: var(--brand-800); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
