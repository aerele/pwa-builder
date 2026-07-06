/* useMode — the simple/advanced split.
 *
 * One shared reactive flag, persisted to localStorage, with an optional
 * per-project override. Everything "advanced" is gated with v-if="isAdvanced"
 * so there is a single component tree, not separate code paths (per the
 * redesign plan). Phase 0 ships the toggle; later phases consume isAdvanced.
 */
import { computed, ref, watch } from 'vue'

const STORAGE_KEY = 'pwa-builder:mode'
const VALID = ['simple', 'advanced']

function load() {
  const v = localStorage.getItem(STORAGE_KEY)
  return VALID.includes(v) ? v : 'simple'
}

// Module-level singleton so every component shares the same state.
const globalMode = ref(load())
// Per-project overrides: { [projectId]: 'simple' | 'advanced' }
const projectOverrides = ref({})

watch(globalMode, (v) => localStorage.setItem(STORAGE_KEY, v))

export function useMode(projectId = null) {
  const mode = computed(() => {
    if (projectId && projectOverrides.value[projectId]) {
      return projectOverrides.value[projectId]
    }
    return globalMode.value
  })

  const isAdvanced = computed(() => mode.value === 'advanced')
  const isSimple = computed(() => mode.value === 'simple')

  function setMode(next) {
    if (!VALID.includes(next)) return
    if (projectId) {
      projectOverrides.value = { ...projectOverrides.value, [projectId]: next }
    } else {
      globalMode.value = next
    }
  }

  function toggle() {
    setMode(mode.value === 'advanced' ? 'simple' : 'advanced')
  }

  function clearProjectOverride() {
    if (!projectId) return
    const next = { ...projectOverrides.value }
    delete next[projectId]
    projectOverrides.value = next
  }

  return { mode, isAdvanced, isSimple, setMode, toggle, clearProjectOverride }
}
