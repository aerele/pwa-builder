<template>
  <!-- Global chrome for all authenticated pages. Picks the rail based on
       whether we're inside a project (route has :projectId). Auth pages do
       not use this shell (they render bare). -->
  <div class="shell pwa-app-bg">
    <header class="shell__topbar">
      <div class="shell__brand">
        <img
          class="shell__logo-img"
          :src="appLogo"
          alt="PWA Builder"
          width="28"
          height="28"
        />
        <template v-if="projectId">
          <FeatherIcon name="chevron-right" class="w-4 h-4 text-[var(--text-subtle)]" />
          <span class="shell__project">{{ projectTitle || projectId }}</span>
          <span class="shell__status" :class="{ 'shell__status--live': projectPublished }">
            <span class="shell__status-dot" /> {{ projectPublished ? 'Published' : 'Draft' }}
          </span>
        </template>
        <span v-else class="shell__title">PWA Builder</span>
      </div>

      <div class="shell__actions">
        <ModeToggle :project-id="projectId" />
        <button class="shell__theme" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'" @click="toggleTheme">
          <FeatherIcon :name="isDark ? 'sun' : 'moon'" class="w-4 h-4" />
        </button>
        <button class="shell__avatar" :title="user">
          {{ initials }}
        </button>
      </div>
    </header>

    <div v-if="!online" class="shell__offline">
      <FeatherIcon name="wifi-off" class="w-3.5 h-3.5" />
      You're offline — changes can't be saved until the connection is back.
    </div>

    <div class="shell__body">
      <ProjectRail v-if="projectId" :project-id="projectId" />
      <GlobalRail v-else />
      <main class="shell__content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon, createResource } from 'frappe-ui'
import GlobalRail from './GlobalRail.vue'
import ProjectRail from './ProjectRail.vue'
import ModeToggle from './ModeToggle.vue'
import { session } from '@/data/session'
import { useTheme } from '@/composables/useTheme'
import appLogo from '@/assets/pwa-builder-logo.png'

const { isDark, toggle: toggleTheme } = useTheme()

const online = ref(navigator.onLine)
const setOnline = () => (online.value = true)
const setOffline = () => (online.value = false)
onMounted(() => {
  window.addEventListener('online', setOnline)
  window.addEventListener('offline', setOffline)
})
onBeforeUnmount(() => {
  window.removeEventListener('online', setOnline)
  window.removeEventListener('offline', setOffline)
})

const route = useRoute()
const projectId = computed(() => route.params.projectId || null)

// Human title + publish state for the breadcrumb (the route only has the id).
const projectTitle = ref('')
const projectPublished = ref(false)
watch(
  projectId,
  async (id) => {
    projectTitle.value = ''
    projectPublished.value = false
    if (!id) return
    try {
      const r = await createResource({ url: 'frappe.client.get_value' }).submit({
        doctype: 'PWA-Project',
        filters: id,
        fieldname: ['project_title', 'github_repository_url'],
      })
      if (projectId.value !== id) return // stale response after fast navigation
      projectTitle.value = r?.project_title || id
      projectPublished.value = !!r?.github_repository_url
    } catch (e) {
      projectTitle.value = id
    }
  },
  { immediate: true }
)

const user = computed(() => session.user || 'Guest')
const initials = computed(() => {
  const u = user.value || 'U'
  return u.replace(/@.*/, '').slice(0, 2).toUpperCase()
})
</script>

<style scoped>
.shell { display: flex; flex-direction: column; height: 100vh; }
.shell__topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.shell__brand { display: flex; align-items: center; gap: 10px; }
.shell__logo-img {
  width: 28px;
  height: 28px;
  display: block;
  flex: none;
  object-fit: contain;
  border-radius: 7px;
}
.shell__logo {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  background: var(--brand);
  color: #fff;
  font-weight: 700;
  border-radius: var(--radius-control);
}
.shell__title { font-weight: 600; color: var(--text); }
.shell__project { font-weight: 600; color: var(--text); }
.shell__status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: 4px;
  padding: 2px 8px;
  font-size: 11.5px;
  color: var(--text-muted);
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
}
.shell__status-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--text-subtle);
}
.shell__status--live { color: var(--ok); }
.shell__status--live .shell__status-dot { background: var(--ok); }
.shell__actions { display: flex; align-items: center; gap: 12px; }
.shell__theme { display: grid; place-items: center; width: 30px; height: 30px; color: var(--text-muted); border-radius: var(--radius-control); }
.shell__theme:hover { color: var(--text); background: var(--surface-muted); }
.shell__offline { display: flex; align-items: center; justify-content: center; gap: 7px; padding: 7px 12px; font-size: 12.5px; font-weight: 550; color: #fff; background: var(--warn); flex-shrink: 0; }
.shell__avatar {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--brand-fg);
  background: var(--brand-700);
  border-radius: 50%;
}
.shell__body { display: flex; flex: 1; min-height: 0; }
.shell__content { flex: 1; overflow: auto; }
</style>
