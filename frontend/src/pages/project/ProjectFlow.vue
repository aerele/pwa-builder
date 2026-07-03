<template>
  <section class="flow">
    <header class="flow__head">
      <div>
        <h1 class="flow__title">Flow</h1>
        <p class="flow__sub">The order screens appear in the app's navigation. Drag to rearrange — the first screen is home.</p>
      </div>
      <span v-if="saving" class="flow__saving"><FeatherIcon name="loader" class="w-3.5 h-3.5 spin" /> Saving order…</span>
    </header>

    <p v-if="error" class="flow__err"><FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ error }}</p>

    <div v-if="rows.loading && !list.length" class="flow__skels">
      <div v-for="n in 3" :key="n" class="flow__sk skeleton" />
    </div>

    <div v-else-if="list.length" class="flow__chain">
      <Draggable :list="list" item-key="name" handle=".fnode__grip" ghost-class="fnode--ghost" @end="persistOrder">
        <template #item="{ element, index }">
          <div>
            <div v-if="index" class="flow__link"><FeatherIcon name="arrow-down" class="w-4 h-4" /></div>
            <div class="fnode">
              <span class="fnode__grip"><FeatherIcon name="menu" class="w-4 h-4" /></span>
              <span class="fnode__icon">
                <FeatherIcon :name="element.title === 'Dashboard' ? 'layout' : 'file-text'" class="w-4 h-4" />
              </span>
              <div class="fnode__main">
                <div class="fnode__title">
                  {{ element.title }}
                  <span v-if="!index" class="fnode__home"><FeatherIcon name="home" class="w-3 h-3" /> Home</span>
                </div>
                <div class="fnode__sub">{{ element.doctype_name }} · {{ fieldCount(element) }} fields</div>
              </div>
              <router-link
                class="fnode__act"
                :to="{ name: 'ProjectBuilder', params: { projectId, screenId: element.name } }"
                title="Open in builder"
              >
                <FeatherIcon name="edit-3" class="w-4 h-4" />
              </router-link>
            </div>
          </div>
        </template>
      </Draggable>
    </div>

    <div v-else class="flow__empty">
      <FeatherIcon name="git-branch" class="w-7 h-7" />
      <h3>Nothing to arrange yet</h3>
      <p>Create screens first, then order the navigation here.</p>
      <router-link class="btn-primary" :to="{ name: 'ProjectScreens', params: { projectId } }">Go to Screens</router-link>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import Draggable from 'vuedraggable'
import { FeatherIcon, createListResource, createResource } from 'frappe-ui'

const props = defineProps({ projectId: { type: String, required: true } })

const error = ref('')
const saving = ref(false)
const list = ref([])

const rows = createListResource({
  doctype: 'PWA DocType',
  fields: ['name', 'title', 'doctype_name', 'field_list', 'nav_order'],
  filters: { project_name: props.projectId },
  orderBy: 'nav_order asc, creation asc',
  pageLength: 99,
  auto: true,
})

watch(
  () => rows.data,
  (data) => (list.value = [...(data || [])]),
  { immediate: true }
)

function fieldCount(s) {
  try {
    const parsed = s.field_list && s.field_list !== '{}' ? JSON.parse(s.field_list) : {}
    return (parsed.pwa_form_fields || []).length
  } catch (e) {
    return 0
  }
}

// Navigation order lives in nav_order; the builder and screens pages
// read the same order.
async function persistOrder() {
  saving.value = true
  error.value = ''
  try {
    const setValue = createResource({ url: 'frappe.client.set_value' })
    for (let i = 0; i < list.value.length; i++) {
      const row = list.value[i]
      if (row.nav_order !== i + 1) {
        await setValue.submit({ doctype: 'PWA DocType', name: row.name, fieldname: 'nav_order', value: i + 1 })
        row.nav_order = i + 1
      }
    }
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not save the order.'
    rows.reload()
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.flow { padding: 24px; max-width: 640px; margin: 0 auto; }
.flow__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.flow__title { font-size: 22px; font-weight: 650; color: var(--text); }
.flow__sub { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }
.flow__saving { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); white-space: nowrap; margin-top: 6px; }
.flow__err { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--danger); margin-bottom: 12px; }

.flow__link { display: flex; justify-content: center; padding: 4px 0; color: var(--text-subtle); }

.fnode { display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); box-shadow: var(--shadow-sm); }
.fnode--ghost { opacity: 0.4; border-style: dashed; }
.fnode__grip { color: var(--text-subtle); cursor: grab; flex: none; }
.fnode__grip:active { cursor: grabbing; }
.fnode__icon { display: grid; place-items: center; width: 32px; height: 32px; flex: none; color: var(--brand); background: var(--brand-subtle); border-radius: var(--radius-control); }
.fnode__main { flex: 1; min-width: 0; }
.fnode__title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--text); }
.fnode__home { display: inline-flex; align-items: center; gap: 4px; font-size: 10.5px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.03em; color: var(--brand); background: var(--brand-subtle); padding: 2px 7px; border-radius: 999px; }
.fnode__sub { font-size: 12px; color: var(--text-muted); }
.fnode__act { color: var(--text-subtle); padding: 6px; border-radius: var(--radius-control); flex: none; }
.fnode__act:hover { color: var(--text); background: var(--surface-muted); }

.flow__skels { display: flex; flex-direction: column; gap: 10px; }
.flow__sk { height: 62px; border-radius: var(--radius-card); }
.skeleton { position: relative; overflow: hidden; background: var(--surface-muted); }
.skeleton::after { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, transparent, var(--sheen), transparent); transform: translateX(-100%); animation: sk 1.3s infinite; }
@keyframes sk { 100% { transform: translateX(100%); } }

.flow__empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 56px; text-align: center; color: var(--text-subtle); background: var(--surface); border: 1px dashed var(--border-strong); border-radius: var(--radius-card); }
.flow__empty h3 { font-size: 15px; font-weight: 650; color: var(--text); }
.flow__empty p { font-size: 13px; color: var(--text-muted); }

.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 9px 14px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand); border-radius: var(--radius-control); }
.btn-primary:hover { background: var(--brand-hover); }
.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
