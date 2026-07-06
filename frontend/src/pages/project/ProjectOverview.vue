<template>
  <section class="ov">
    <header class="ov__head">
      <div>
        <h1 class="ov__title">{{ title }}</h1>
        <p class="ov__sub">{{ subtitle }}</p>
      </div>
      <span class="ov__status" :class="published ? 'is-pub' : 'is-draft'">
        <span class="ov__dot" />{{ published ? 'Published' : 'Draft' }}
      </span>
    </header>

    <div class="ov__grid">
      <!-- Connection -->
      <div class="card">
        <div class="card__head"><FeatherIcon :name="isLocal ? 'home' : 'globe'" class="w-4 h-4" /> Connection</div>
        <div class="card__body">
          <div class="row"><span>Type</span><b>{{ isLocal ? 'This site' : 'Another site' }}</b></div>
          <div class="row"><span>Site</span><b class="trunc">{{ doc?.site_url || '—' }}</b></div>
          <div class="row">
            <span>Status</span>
            <b class="ok"><span class="hdot" /> {{ isLocal ? 'Local' : 'Connected' }}</b>
          </div>
        </div>
      </div>

      <!-- Publishing -->
      <div class="card">
        <div class="card__head"><FeatherIcon name="upload-cloud" class="w-4 h-4" /> Publishing</div>
        <div class="card__body">
          <template v-if="published">
            <div class="row">
              <span>Repository</span>
              <a class="link trunc" :href="doc.github_repository_url" target="_blank" rel="noopener">{{ doc.github_repository_url }}</a>
            </div>
            <div class="row"><span>Branch</span><b>{{ doc.github_default_branch || '—' }}</b></div>
            <div class="row"><span>Last push</span><b class="trunc">{{ doc.last_push_commit || '—' }}</b></div>
          </template>
          <div v-else class="card__empty">
            <p>Not published yet.</p>
            <router-link class="btn-primary" :to="{ name: 'ProjectPublish', params: { projectId } }">
              <FeatherIcon name="upload-cloud" class="w-4 h-4" /> Publish
            </router-link>
          </div>
        </div>
      </div>

      <!-- Screens -->
      <div class="card">
        <div class="card__head"><FeatherIcon name="layers" class="w-4 h-4" /> Screens</div>
        <div class="card__body card__body--center">
          <div class="big">{{ screens.data ? screens.data.length : '—' }}</div>
          <div class="muted">{{ (screens.data && screens.data.length === 1) ? 'screen' : 'screens' }} built</div>
          <router-link class="btn-ghost" :to="{ name: 'ProjectScreens', params: { projectId } }">Manage screens →</router-link>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="ov__actions">
      <router-link class="action" :to="{ name: 'ProjectBuilder', params: { projectId } }">
        <FeatherIcon name="edit-3" class="w-4 h-4" /> Open builder
      </router-link>
      <router-link class="action" :to="{ name: 'ProjectData', params: { projectId } }">
        <FeatherIcon name="database" class="w-4 h-4" /> Manage data
      </router-link>
      <span class="ov__edited" v-if="doc">Updated {{ relativeTime(doc.modified) }}</span>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon, createResource, createListResource } from 'frappe-ui'
import { relativeTime } from '@/data/projects'

const props = defineProps({ projectId: { type: String, required: true } })

const project = createResource({
  url: 'frappe.client.get',
  params: { doctype: 'PWA-Project', name: props.projectId },
  auto: true,
})
const screens = createListResource({
  doctype: 'PWA DocType',
  fields: ['name', 'title', 'doctype_name', 'disable'],
  filters: { project_name: props.projectId },
  pageLength: 99,
  auto: true,
})

const doc = computed(() => project.data)
const title = computed(() => doc.value?.project_title || props.projectId)
const subtitle = computed(() => doc.value?.description || doc.value?.sub_title || 'Project overview')
const isLocal = computed(() => (doc.value?.connection_type || 'Another Site') === 'This Site')
const published = computed(() => !!doc.value?.github_repository_url)
</script>

<style scoped>
.ov { padding: 24px; max-width: 1000px; margin: 0 auto; }
.ov__head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.ov__title { font-size: 22px; font-weight: 650; color: var(--text); }
.ov__sub { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }
.ov__status { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 550; padding: 5px 11px; border-radius: 999px; }
.ov__status.is-pub { color: var(--ok); background: rgba(22,163,74,0.1); }
.ov__status.is-draft { color: var(--text-muted); background: var(--surface-muted); }
.ov__dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }

.ov__grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); box-shadow: var(--shadow-sm); overflow: hidden; }
.card__head { display: flex; align-items: center; gap: 8px; padding: 13px 16px; font-size: 13px; font-weight: 600; color: var(--text); border-bottom: 1px solid var(--border); }
.card__body { padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }
.card__body--center { align-items: flex-start; }
.row { display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 13px; }
.row span { color: var(--text-muted); }
.row b { color: var(--text); font-weight: 550; max-width: 60%; text-align: right; }
.trunc { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ok { color: var(--ok) !important; display: inline-flex; align-items: center; gap: 6px; }
.hdot { width: 7px; height: 7px; border-radius: 50%; background: var(--ok); box-shadow: 0 0 0 3px rgba(22,163,74,0.15); }
.link { color: var(--brand); font-weight: 500; }
.card__empty { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }
.card__empty p { font-size: 13px; color: var(--text-muted); }
.big { font-size: 30px; font-weight: 700; color: var(--text); line-height: 1; }
.muted { font-size: 12.5px; color: var(--text-muted); }

.ov__actions { display: flex; align-items: center; gap: 12px; margin-top: 20px; }
.action { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 550; color: var(--text); padding: 9px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-control); transition: all 0.12s ease; }
.action:hover { border-color: var(--brand-300); color: var(--brand); box-shadow: var(--shadow-sm); }
.ov__edited { margin-left: auto; font-size: 12px; color: var(--text-subtle); }

.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 7px 13px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand); border-radius: var(--radius-control); }
.btn-primary:hover { background: var(--brand-hover); }
.btn-ghost { font-size: 12.5px; font-weight: 550; color: var(--brand); margin-top: 4px; }
</style>
