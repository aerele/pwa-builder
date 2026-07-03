<template>
  <div class="dash">
    <!-- Getting-started checklist (clickable, real state, auto-hides when done) -->
    <section v-if="showChecklist && !allDone" class="dash__getstarted">
      <div class="gs__head">
        <h2 class="gs__title">Get started</h2>
        <button class="gs__dismiss" title="Dismiss" @click="dismissChecklist">
          <FeatherIcon name="x" class="w-4 h-4" />
        </button>
      </div>
      <ol class="gs__steps">
        <li v-for="(step, i) in steps" :key="step.key">
          <button class="gs__step" :class="{ 'gs__step--done': step.done }" @click="step.action()">
            <span class="gs__num">
              <FeatherIcon v-if="step.done" name="check" class="w-3 h-3" />
              <template v-else>{{ i + 1 }}</template>
            </span>
            {{ step.label }}
            <FeatherIcon v-if="!step.done" name="chevron-right" class="gs__chev w-3.5 h-3.5" />
          </button>
        </li>
      </ol>
      <div class="gs__foot">
        <div class="gs__bar"><span :style="{ width: progress + '%' }" /></div>
        <span class="gs__count">{{ doneCount }}/{{ steps.length }} done</span>
      </div>
    </section>

    <!-- Templates strip -->
    <section class="dash__section">
      <header class="sec__head">
        <h2 class="sec__title">Templates</h2>
        <router-link :to="{ name: 'Templates' }" class="sec__link">See all →</router-link>
      </header>
      <div class="tpl__row">
        <button v-for="t in templates" :key="t.label" class="tpl" @click="startFromTemplate(t)">
          <span class="tpl__icon"><FeatherIcon :name="t.icon" class="w-5 h-5" /></span>
          <span class="tpl__label">{{ t.label }}</span>
        </button>
      </div>
    </section>

    <!-- Projects -->
    <section class="dash__section">
      <header class="sec__head">
        <h2 class="sec__title">Your projects</h2>
        <button class="btn-primary" @click="showNew = true"><FeatherIcon name="plus" class="w-4 h-4" /> New project</button>
      </header>

      <!-- Loading skeletons -->
      <div v-if="loading && !cards.length" class="proj__grid">
        <div v-for="n in 3" :key="n" class="proj proj--skeleton">
          <div class="proj__thumb skeleton" />
          <div class="proj__meta">
            <div class="skeleton sk-line" />
            <div class="skeleton sk-line sk-line--short" />
          </div>
        </div>
      </div>

      <!-- Real projects -->
      <div v-else-if="cards.length" class="proj__grid">
        <router-link
          v-for="p in cards"
          :key="p.name"
          class="proj"
          :to="{ name: 'ProjectOverview', params: { projectId: p.name } }"
        >
          <div class="proj__thumb">
            <ProjectThumb :title="p.title" />
          </div>
          <div class="proj__meta">
            <div class="proj__name">{{ p.title }}</div>
            <div class="proj__sub">
              <span class="proj__status" :class="p.published ? 'is-pub' : 'is-draft'">
                <span class="proj__dot" />{{ p.published ? 'Published' : 'Draft' }}
              </span>
              <span class="proj__edited">edited {{ p.edited }}</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Empty state -->
      <div v-else class="empty">
        <div class="empty__thumb"><ProjectThumb title="New App" /></div>
        <h3>Create your first PWA</h3>
        <p>Connect a Frappe site and start building screens.</p>
        <button class="btn-primary" @click="showNew = true"><FeatherIcon name="plus" class="w-4 h-4" /> New project</button>
      </div>
    </section>

    <NewProjectDialog v-model="showNew" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon, createResource } from 'frappe-ui'
import ProjectThumb from '@/components/ProjectThumb.vue'
import NewProjectDialog from '@/components/NewProjectDialog.vue'
import { projects, relativeTime } from '@/data/projects'

const router = useRouter()
const showNew = ref(false)
// Persist dismissal so it doesn't nag after the user closes it.
const showChecklist = ref(localStorage.getItem('pwa-builder:gs-dismissed') !== '1')

const loading = computed(() => projects.loading)

// Map raw PWA-Project rows to card view-models.
const cards = computed(() =>
  (projects.data || []).map((p) => ({
    name: p.name,
    title: p.project_title || p.name,
    published: !!p.github_repository_url,
    edited: relativeTime(p.modified),
  }))
)

// --- Getting-started: real per-step state, tracked on the latest project ---
const latestProject = computed(() => (projects.data || [])[0] || null)

// Screens (PWA DocType rows) for the latest project, for steps 2 & 3.
const screens = createResource({ url: 'frappe.client.get_list' })
watch(
  latestProject,
  (p) => {
    if (p) {
      screens.submit({
        doctype: 'PWA DocType',
        filters: { project_name: p.name },
        fields: ['name', 'field_list'],
        limit_page_length: 0,
      })
    }
  },
  { immediate: true }
)

const hasProject = computed(() => cards.value.length > 0)
const hasDoctype = computed(() => (screens.data || []).length > 0)
const hasScreen = computed(() =>
  (screens.data || []).some((s) => s.field_list && s.field_list !== '{}' && s.field_list !== '')
)
const published = computed(() => cards.value.some((c) => c.published))

function goToLatest(routeName) {
  if (latestProject.value) {
    router.push({ name: routeName, params: { projectId: latestProject.value.name } })
  } else {
    showNew.value = true
  }
}

const steps = computed(() => [
  { key: 'connect', label: 'Connect a site', done: hasProject.value, action: () => (showNew.value = true) },
  { key: 'doctype', label: 'Pick a doctype', done: hasDoctype.value, action: () => goToLatest('ProjectData') },
  { key: 'screen', label: 'Add a screen', done: hasScreen.value, action: () => goToLatest('ProjectBuilder') },
  { key: 'preview', label: 'Preview', done: hasScreen.value, action: () => goToLatest('ProjectBuilder') },
  { key: 'publish', label: 'Publish', done: published.value, action: () => goToLatest('ProjectPublish') },
])
const doneCount = computed(() => steps.value.filter((s) => s.done).length)
const allDone = computed(() => doneCount.value === steps.value.length)
const progress = computed(() => Math.round((doneCount.value / steps.value.length) * 100))

function dismissChecklist() {
  showChecklist.value = false
  localStorage.setItem('pwa-builder:gs-dismissed', '1')
}

const templates = [
  { label: 'List', icon: 'list' },
  { label: 'Form', icon: 'edit' },
  { label: 'Dashboard', icon: 'bar-chart-2' },
  { label: 'Blank', icon: 'plus' },
]

// Templates pre-seed the create flow. Screen-template wiring lands in Phase 3;
// for now any tile opens the New-project dialog.
function startFromTemplate(_t) {
  showNew.value = true
}
</script>

<style scoped>
.dash { padding: 24px; max-width: 1100px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; }

/* Getting started */
.dash__getstarted {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
}
.gs__head { display: flex; align-items: center; justify-content: space-between; }
.gs__title { font-size: 15px; font-weight: 650; color: var(--text); }
.gs__dismiss { color: var(--text-subtle); }
.gs__dismiss:hover { color: var(--text); }
.gs__steps { display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0; list-style: none; padding: 0; }
.gs__step {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 12px 7px 8px; font-size: 13px; font-weight: 500; color: var(--text-muted);
  background: var(--surface); border: 1px solid var(--border); border-radius: 999px;
  cursor: pointer; transition: all 0.12s ease;
}
.gs__step:hover { border-color: var(--brand-300); color: var(--brand); box-shadow: var(--shadow-sm); }
.gs__step--done { color: var(--text); background: var(--surface-muted); }
.gs__step--done:hover { border-color: var(--border); box-shadow: none; }
.gs__chev { color: var(--text-subtle); margin-left: 2px; }
.gs__num {
  width: 20px; height: 20px; display: grid; place-items: center;
  font-size: 11px; font-weight: 600; border-radius: 50%;
  background: var(--surface-muted); color: var(--text-muted);
  border: 1px solid var(--border);
}
.gs__step--done .gs__num { background: var(--brand); color: var(--brand-fg); border-color: var(--brand); }
.gs__foot { display: flex; align-items: center; gap: 12px; }
.gs__bar { flex: 1; height: 6px; background: var(--surface-muted); border-radius: 999px; overflow: hidden; }
.gs__bar span { display: block; height: 100%; background: var(--brand); border-radius: 999px; transition: width 0.3s ease; }
.gs__count { font-size: 12px; color: var(--text-muted); }

/* Sections */
.sec__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.sec__title { font-size: 16px; font-weight: 650; color: var(--text); }
.sec__link { font-size: 13px; color: var(--brand); font-weight: 500; }

/* Templates */
.tpl__row { display: flex; gap: 14px; flex-wrap: wrap; }
.tpl {
  width: 132px; height: 96px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card);
  color: var(--text-muted); transition: all 0.12s ease;
}
.tpl:hover { border-color: var(--brand-300); color: var(--brand); box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.tpl__icon { color: var(--brand); }
.tpl__label { font-size: 13px; font-weight: 500; color: var(--text); }

/* Projects */
.proj__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 18px; }
.proj {
  display: block;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-card); overflow: hidden; transition: all 0.12s ease;
}
.proj:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.proj--skeleton:hover { transform: none; box-shadow: none; }
.proj__thumb {
  height: 168px; display: grid; place-items: center;
  background: var(--surface-muted); border-bottom: 1px solid var(--border); overflow: hidden;
}
.proj__meta { padding: 12px 14px; }
.proj__name { font-size: 14px; font-weight: 600; color: var(--text); }
.proj__sub { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.proj__status { display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 500; }
.proj__status.is-pub { color: var(--ok); }
.proj__status.is-draft { color: var(--text-muted); }
.proj__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.proj__edited { font-size: 11.5px; color: var(--text-subtle); }

/* Skeleton */
.skeleton { position: relative; overflow: hidden; background: var(--surface-muted); }
.skeleton::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, var(--sheen), transparent);
  transform: translateX(-100%); animation: sk 1.3s infinite;
}
@keyframes sk { 100% { transform: translateX(100%); } }
.sk-line { height: 12px; border-radius: 5px; margin-top: 6px; }
.sk-line--short { width: 55%; }

/* Empty state */
.empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 40px; text-align: center; }
.empty__thumb { width: 200px; height: 150px; border: 1px solid var(--border); border-radius: var(--radius-card); overflow: hidden; box-shadow: var(--shadow-sm); }
.empty h3 { font-size: 16px; font-weight: 650; color: var(--text); margin-top: 8px; }
.empty p { font-size: 13px; color: var(--text-muted); }

/* Shared primary button */
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 13px; font-size: 13px; font-weight: 550;
  color: var(--brand-fg); background: var(--brand);
  border-radius: var(--radius-control); transition: background 0.12s ease;
}
.btn-primary:hover { background: var(--brand-hover); }
</style>
