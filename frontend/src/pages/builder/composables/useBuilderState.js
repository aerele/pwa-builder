/* Per-screen builder state: screens, canvas fields, palette, selection,
 * undo/redo history, dirty tracking and save. One instance per Builder mount. */
import { computed, ref } from 'vue'
import { createResource } from 'frappe-ui'

const EXCLUDED_TYPES = ['Section Break', 'Column Break', 'Tab Break', 'Geolocation', 'Button']
const EXCLUDED_NAMES = ['rgt', 'lft', 'old_parent']

export function usableField(f) {
  return !EXCLUDED_TYPES.includes(f.fieldtype) && !EXCLUDED_NAMES.includes(f.fieldname)
}

export function useBuilderState(projectId) {
  const screens = ref([])
  const screensLoading = ref(true)
  const screen = ref(null) // current PWA DocType row
  const metaLoading = ref(false)
  const metaFields = ref([]) // usable doctype meta fields (palette source)
  const childMeta = ref({}) // { table fieldname: [child doctype fields] }
  const isSubmittable = ref(0)
  const canvasFields = ref([])
  const selected = ref(null) // fieldname of the selected canvas field
  const saving = ref(false)
  const loadError = ref('')

  const isDashboard = computed(() => screen.value?.title === 'Dashboard')

  // --- undo/redo: string snapshots of the canvas ---
  const past = ref([])
  const future = ref([])
  let lastSnapshot = '[]'
  const serialize = () => JSON.stringify(canvasFields.value)
  const canUndo = computed(() => past.value.length > 0)
  const canRedo = computed(() => future.value.length > 0)

  function commit() {
    if (serialize() === lastSnapshot) return
    past.value.push(lastSnapshot)
    if (past.value.length > 100) past.value.shift()
    future.value = []
    lastSnapshot = serialize()
  }

  function restore(snapshot) {
    canvasFields.value = JSON.parse(snapshot)
    lastSnapshot = snapshot
    if (selected.value && !canvasFields.value.some((f) => f.fieldname === selected.value)) {
      selected.value = null
    }
  }

  function undo() {
    if (!canUndo.value) return
    future.value.push(serialize())
    restore(past.value.pop())
  }

  function redo() {
    if (!canRedo.value) return
    past.value.push(serialize())
    restore(future.value.pop())
  }

  // --- dirty tracking ---
  const savedSnapshot = ref('[]')
  const dirty = computed(() => serialize() !== savedSnapshot.value)

  // --- palette ---
  const paletteSource = ref([])
  const placedNames = computed(() => new Set(canvasFields.value.map((f) => f.fieldname)))
  const palette = computed(() => paletteSource.value.filter((f) => !placedNames.value.has(f.fieldname)))

  // Required doctype fields not yet placed — surfaced inline in the builder.
  const missingRequired = computed(() => {
    if (isDashboard.value) return []
    return metaFields.value.filter((f) => f.reqd && !placedNames.value.has(f.fieldname))
  })

  const selectedField = computed(() => canvasFields.value.find((f) => f.fieldname === selected.value) || null)

  // --- loading ---
  async function loadScreens() {
    screensLoading.value = true
    try {
      const rows = await createResource({ url: 'frappe.client.get_list' }).submit({
        doctype: 'PWA DocType',
        filters: { project_name: projectId },
        fields: ['name', 'title', 'doctype_name', 'field_list', 'is_validated'],
        limit_page_length: 0,
        order_by: 'nav_order asc, creation asc',
      })
      screens.value = rows || []
    } catch (e) {
      loadError.value = errText(e, 'Could not load screens.')
    } finally {
      screensLoading.value = false
    }
    return screens.value
  }

  async function loadDoctypeMeta(doctype) {
    const meta = await createResource({ url: 'pwa_builder.api.get_meta' }).submit({
      doctype,
      project: projectId,
    })
    return meta
  }

  async function openScreen(name) {
    const row = screens.value.find((s) => s.name === name)
    if (!row) return
    screen.value = row
    selected.value = null
    loadError.value = ''

    // Parse whatever is stored; legacy rows may hold '{}'.
    let parsed = {}
    try {
      parsed = row.field_list && row.field_list !== '{}' ? JSON.parse(row.field_list) : {}
    } catch (e) {
      parsed = {}
    }
    canvasFields.value = parsed.pwa_form_fields || []
    lastSnapshot = serialize()
    savedSnapshot.value = lastSnapshot
    past.value = []
    future.value = []

    metaLoading.value = true
    metaFields.value = []
    childMeta.value = {}
    try {
      if (isDashboard.value) {
        // Dashboard screens place local Number Cards instead of doctype fields.
        const cards = await createResource({ url: 'frappe.client.get_list' }).submit({
          doctype: 'Number Card',
          fields: ['name', 'label'],
          limit_page_length: 0,
        })
        isSubmittable.value = 0
        paletteSource.value = (cards || []).map((c) => ({
          fieldtype: 'Number Card',
          fieldname: c.name,
          label: c.label || c.name,
        }))
      } else {
        const meta = await loadDoctypeMeta(row.doctype_name)
        isSubmittable.value = meta?.is_submittable || 0
        metaFields.value = (meta?.fields || []).filter(usableField)
        paletteSource.value = metaFields.value
        await Promise.all(
          metaFields.value
            .filter((f) => f.fieldtype === 'Table' && f.options)
            .map(async (f) => {
              try {
                const child = await loadDoctypeMeta(f.options)
                childMeta.value = { ...childMeta.value, [f.fieldname]: (child?.fields || []).filter(usableField) }
              } catch (e) {
                /* child meta is optional; the column picker just stays empty */
              }
            })
        )
      }
    } catch (e) {
      loadError.value = errText(e, 'Could not load doctype metadata.')
    } finally {
      metaLoading.value = false
    }
  }

  // --- mutations (each commits a history snapshot) ---
  function addField(field, index = null) {
    if (placedNames.value.has(field.fieldname)) return
    const copy = JSON.parse(JSON.stringify(field))
    if (index === null || index > canvasFields.value.length) index = canvasFields.value.length
    canvasFields.value.splice(index, 0, copy)
    commit()
    selected.value = copy.fieldname
  }

  function removeField(fieldname) {
    const i = canvasFields.value.findIndex((f) => f.fieldname === fieldname)
    if (i === -1) return
    canvasFields.value.splice(i, 1)
    if (selected.value === fieldname) selected.value = null
    commit()
  }

  function select(fieldname) {
    selected.value = fieldname
  }

  // --- save (same payload shape the export pipeline already consumes) ---
  async function save() {
    if (!screen.value || saving.value) return false
    saving.value = true
    canvasFields.value.forEach((f, i) => (f.idx = i + 1))
    const payload = {
      form_name: isDashboard.value ? 'Dashboard' : screen.value.title,
      name: screen.value.name,
      doctype_name: isDashboard.value ? 'Dashboard' : screen.value.doctype_name,
      is_submittable: isSubmittable.value,
      pwa_form_fields: canvasFields.value,
    }
    try {
      await createResource({ url: 'pwa_builder.api.set_value' }).submit({
        doctype: 'PWA DocType',
        docname: screen.value.name,
        fieldname: 'field_list',
        value: payload,
      })
      lastSnapshot = serialize()
      savedSnapshot.value = lastSnapshot
      screen.value.field_list = JSON.stringify(payload)
      return true
    } catch (e) {
      loadError.value = errText(e, 'Could not save the screen.')
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    screens,
    screensLoading,
    screen,
    isDashboard,
    metaLoading,
    metaFields,
    childMeta,
    isSubmittable,
    canvasFields,
    palette,
    missingRequired,
    selected,
    selectedField,
    dirty,
    saving,
    loadError,
    canUndo,
    canRedo,
    loadScreens,
    openScreen,
    addField,
    removeField,
    select,
    commit,
    undo,
    redo,
    save,
  }
}

function errText(e, fallback) {
  return (e && e.messages && e.messages[0]) || (e && e.message) || fallback
}
