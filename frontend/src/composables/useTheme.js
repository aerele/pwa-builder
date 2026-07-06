/* Theme: light / dark / system. Applies the .dark class on <html> so the
 * token overrides in design/tokens.css (and tailwind dark:) take effect. */
import { computed, ref, watch } from 'vue'

const STORAGE_KEY = 'pwa-builder:theme'
const VALID = ['light', 'dark', 'system']

const media = window.matchMedia('(prefers-color-scheme: dark)')
const systemDark = ref(media.matches)
media.addEventListener('change', (e) => (systemDark.value = e.matches))

function load() {
  const v = localStorage.getItem(STORAGE_KEY)
  return VALID.includes(v) ? v : 'system'
}

const theme = ref(load())
const isDark = computed(() => theme.value === 'dark' || (theme.value === 'system' && systemDark.value))

watch(
  isDark,
  (dark) => document.documentElement.classList.toggle('dark', dark),
  { immediate: true }
)
watch(theme, (v) => localStorage.setItem(STORAGE_KEY, v))

export function useTheme() {
  function setTheme(next) {
    if (VALID.includes(next)) theme.value = next
  }

  // Quick toggle: flips to the opposite of what is currently shown.
  function toggle() {
    theme.value = isDark.value ? 'light' : 'dark'
  }

  return { theme, isDark, setTheme, toggle }
}
