<template>
  <!-- Global chrome for all authenticated pages. Picks the rail based on
       whether we're inside a project (route has :projectId). Auth pages do
       not use this shell (they render bare). -->
  <div class="shell pwa-app-bg">
    <header class="shell__topbar">
      <div class="shell__brand">
        <div class="shell__logo">P</div>
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
        <button class="shell__avatar" :title="user">
          {{ initials }}
        </button>
      </div>
    </header>

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
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { FeatherIcon, createResource } from 'frappe-ui'
import GlobalRail from './GlobalRail.vue'
import ProjectRail from './ProjectRail.vue'
import ModeToggle from './ModeToggle.vue'
import { session } from '@/data/session'

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
.shell__logo {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  background: var(--brand-950);
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
