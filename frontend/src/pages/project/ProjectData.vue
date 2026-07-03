<template>
  <section class="data">
    <header class="data__head">
      <div>
        <h1 class="data__title">Data</h1>
        <p class="data__sub">Doctypes available to build screens from in this project.</p>
      </div>
    </header>

    <!-- Add row -->
    <div class="add">
      <input
        v-model="newDoctype"
        list="local-doctypes"
        class="add__in add__in--dt"
        placeholder="Doctype (e.g. Task)"
        @keyup.enter="addDoctype"
      />
      <datalist id="local-doctypes">
        <option v-for="d in (doctypes.data || [])" :key="d.name" :value="d.name" />
      </datalist>
      <input
        v-model="newTitle"
        class="add__in"
        placeholder="Screen title (optional)"
        @keyup.enter="addDoctype"
      />
      <button class="btn-primary" :disabled="!newDoctype || adding" @click="addDoctype">
        <FeatherIcon :name="adding ? 'loader' : 'plus'" class="w-4 h-4" :class="{ spin: adding }" /> Add
      </button>
    </div>
    <p v-if="error" class="err"><FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ error }}</p>

    <!-- List -->
    <div v-if="rows.loading && !list.length" class="skeleton-list">
      <div v-for="n in 3" :key="n" class="sk-row skeleton" />
    </div>

    <ul v-else-if="list.length" class="rows">
      <li v-for="r in list" :key="r.name" class="rowitem">
        <span class="rowitem__icon"><FeatherIcon name="database" class="w-4 h-4" /></span>
        <div class="rowitem__main">
          <div class="rowitem__title">{{ r.title || r.doctype_name }}</div>
          <div class="rowitem__sub">{{ r.doctype_name }}</div>
        </div>
        <span v-if="r.disable" class="tag">Disabled</span>
        <span v-if="r.is_validated" class="tag tag--ok">Validated</span>
        <router-link class="rowitem__act" :to="{ name: 'ProjectBuilder', params: { projectId, screenId: r.name } }" title="Open in builder">
          <FeatherIcon name="edit-3" class="w-4 h-4" />
        </router-link>
        <button class="rowitem__act rowitem__act--danger" title="Remove" @click="removeDoctype(r.name)">
          <FeatherIcon name="trash-2" class="w-4 h-4" />
        </button>
      </li>
    </ul>

    <div v-else class="empty">
      <FeatherIcon name="database" class="w-7 h-7" />
      <h3>No doctypes yet</h3>
      <p>Add a doctype above to start building screens from it.</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { FeatherIcon, createResource, createListResource } from 'frappe-ui'

const props = defineProps({ projectId: { type: String, required: true } })

const newDoctype = ref('')
const newTitle = ref('')
const adding = ref(false)
const error = ref('')

const rows = createListResource({
  doctype: 'PWA DocType',
  fields: ['name', 'title', 'doctype_name', 'disable', 'is_validated'],
  filters: { project_name: props.projectId },
  pageLength: 99,
  auto: true,
})
const list = computed(() => rows.data || [])

// Local doctype suggestions (best effort; useful for "This site" projects).
const doctypes = createListResource({
  doctype: 'DocType',
  fields: ['name'],
  filters: { istable: 0, issingle: 0 },
  orderBy: 'name asc',
  pageLength: 0,
  auto: true,
})

const insert = createResource({ url: 'frappe.client.insert' })
const del = createResource({ url: 'frappe.client.delete' })

async function addDoctype() {
  if (!newDoctype.value || adding.value) return
  error.value = ''
  adding.value = true
  try {
    await insert.submit({
      doc: {
        doctype: 'PWA DocType',
        project_name: props.projectId,
        doctype_name: newDoctype.value,
        title: newTitle.value || newDoctype.value,
        field_list: '{}',
      },
    })
    newDoctype.value = ''
    newTitle.value = ''
    rows.reload()
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not add doctype.'
  } finally {
    adding.value = false
  }
}

async function removeDoctype(name) {
  try {
    await del.submit({ doctype: 'PWA DocType', name })
    rows.reload()
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not remove.'
  }
}
</script>

<style scoped>
.data { padding: 24px; max-width: 820px; margin: 0 auto; }
.data__head { margin-bottom: 18px; }
.data__title { font-size: 22px; font-weight: 650; color: var(--text); }
.data__sub { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }

.add { display: flex; gap: 10px; margin-bottom: 8px; }
.add__in { flex: 1; padding: 9px 11px; font-size: 13px; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-control); outline: none; transition: border-color 0.12s, box-shadow 0.12s; }
.add__in--dt { flex: 1.2; }
.add__in:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }
.err { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--danger); margin-bottom: 10px; }

.rows { display: flex; flex-direction: column; gap: 8px; margin-top: 14px; }
.rowitem { display: flex; align-items: center; gap: 12px; padding: 11px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); box-shadow: var(--shadow-sm); }
.rowitem__icon { color: var(--brand); display: grid; place-items: center; width: 30px; height: 30px; background: var(--brand-subtle); border-radius: var(--radius-control); }
.rowitem__main { flex: 1; min-width: 0; }
.rowitem__title { font-size: 14px; font-weight: 600; color: var(--text); }
.rowitem__sub { font-size: 12px; color: var(--text-muted); }
.tag { font-size: 10.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); background: var(--surface-muted); padding: 3px 8px; border-radius: 999px; }
.tag--ok { color: var(--ok); background: rgba(22,163,74,0.1); }
.rowitem__act { color: var(--text-subtle); padding: 6px; border-radius: var(--radius-control); }
.rowitem__act:hover { color: var(--text); background: var(--surface-muted); }
.rowitem__act--danger:hover { color: var(--danger); background: rgba(220,38,38,0.08); }

.skeleton-list { display: flex; flex-direction: column; gap: 8px; margin-top: 14px; }
.sk-row { height: 54px; border-radius: var(--radius-card); }
.skeleton { position: relative; overflow: hidden; background: var(--surface-muted); }
.skeleton::after { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent); transform: translateX(-100%); animation: sk 1.3s infinite; }
@keyframes sk { 100% { transform: translateX(100%); } }

.empty { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 48px; text-align: center; color: var(--text-subtle); margin-top: 14px; background: var(--surface); border: 1px dashed var(--border-strong); border-radius: var(--radius-card); }
.empty h3 { font-size: 15px; font-weight: 650; color: var(--text); }
.empty p { font-size: 13px; color: var(--text-muted); }

.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 9px 14px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand-950); border-radius: var(--radius-control); }
.btn-primary:hover { background: var(--brand-800); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
