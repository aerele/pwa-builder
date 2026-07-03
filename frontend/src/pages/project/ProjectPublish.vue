<template>
  <section class="pub">
    <header class="pub__head">
      <h1 class="pub__title">Publish</h1>
      <p class="pub__sub">Validate the screens, generate the app and push it to GitHub — one click.</p>
    </header>

    <!-- 1. GitHub connection -->
    <div class="card">
      <div class="card__title"><FeatherIcon name="github" class="w-4 h-4" /> GitHub</div>
      <GithubSetup @updated="(u) => (ghUser = u)" />
    </div>

    <!-- 2. Publish -->
    <div class="card">
      <div class="card__title"><FeatherIcon name="upload-cloud" class="w-4 h-4" /> Publish</div>

      <div class="pub__go">
        <div class="pub__go-info">
          <div class="pub__go-label">{{ screenCount }} screen{{ screenCount === 1 ? '' : 's' }} in this app</div>
          <div class="pub__go-hint">
            {{ repoUrl ? 'Publishing again pushes a new commit to the same repository.' : 'The first publish creates the repository.' }}
          </div>
        </div>
        <button class="btn-primary" :disabled="!canPublish" @click="publish">
          <FeatherIcon :name="running ? 'loader' : 'upload-cloud'" class="w-4 h-4" :class="{ spin: running }" />
          {{ running ? 'Publishing…' : 'Publish' }}
        </button>
      </div>
      <p v-if="!ghUser" class="pub__blocked">Connect GitHub above to enable publishing.</p>
      <p v-else-if="lastError && !running" class="pub__lasterr">
        <FeatherIcon name="alert-circle" class="w-4 h-4 flex-none" /> Last publish failed: {{ lastError }}
      </p>

      <!-- Timeline -->
      <ol v-if="steps.some((s) => s.state !== 'pending')" class="tl">
        <li v-for="s in steps" :key="s.id" class="tl__step" :class="`tl__step--${s.state}`">
          <span class="tl__dot">
            <FeatherIcon
              :name="s.state === 'done' ? 'check' : s.state === 'error' ? 'x' : s.state === 'active' ? 'loader' : 'circle'"
              class="w-3 h-3"
              :class="{ spin: s.state === 'active' }"
            />
          </span>
          <div class="tl__body">
            <div class="tl__label">{{ s.label }}</div>
            <div v-if="s.detail" class="tl__detail">{{ s.detail }}</div>
          </div>
        </li>
      </ol>

      <!-- Validation issues -->
      <div v-if="issues.length" class="pub__issues">
        <div v-for="i in issues" :key="i.form" class="pub__issue">
          <FeatherIcon name="alert-triangle" class="w-4 h-4 flex-none" />
          <span><b>{{ i.form }}</b> is missing: {{ i.missing.join(', ') }}</span>
        </div>
      </div>
    </div>

    <!-- 3. Repository -->
    <div v-if="repoUrl" class="card">
      <div class="card__title"><FeatherIcon name="package" class="w-4 h-4" /> Repository</div>
      <div class="pub__repo">
        <a :href="repoUrl" target="_blank" rel="noopener" class="pub__repo-link">{{ repoUrl }}</a>
        <div v-if="isAdvanced" class="pub__repo-meta">
          <span v-if="branch">branch: {{ branch }}</span>
          <span v-if="lastCommit">last push: {{ lastCommit }}</span>
          <span v-if="jobStatus">job: {{ jobStatus }}</span>
        </div>
        <p class="pub__go-hint">
          Install it on the target site with bench get-app, then open https://&lt;site&gt;/frontend.
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { FeatherIcon, createListResource, createResource } from 'frappe-ui'
import GithubSetup from '@/components/GithubSetup.vue'
import { useMode } from '@/composables/useMode'

const props = defineProps({ projectId: { type: String, required: true } })
const { isAdvanced } = useMode(props.projectId)

const ghUser = ref('')
const running = ref(false)
const issues = ref([])
const repoUrl = ref('')
const branch = ref('')
const lastCommit = ref('')
const jobStatus = ref('')
const lastError = ref('')

const STEP_DEFS = [
  { id: 'validate', label: 'Validate screens' },
  { id: 'queue', label: 'Queue the export' },
  { id: 'push', label: 'Generate the app and push to GitHub' },
  { id: 'live', label: 'Repository ready' },
]
const steps = ref(STEP_DEFS.map((s) => ({ ...s, state: 'pending', detail: '' })))

const screens = createListResource({
  doctype: 'PWA DocType',
  fields: ['name'],
  filters: { project_name: props.projectId, disable: 0 },
  pageLength: 99,
  auto: true,
})
const screenCount = computed(() => (screens.data || []).length)
const canPublish = computed(() => !!ghUser.value && screenCount.value > 0 && !running.value)

function setStep(id, state, detail = '') {
  const s = steps.value.find((x) => x.id === id)
  if (s) {
    s.state = state
    if (detail) s.detail = detail
  }
}

function resetSteps() {
  steps.value = STEP_DEFS.map((s) => ({ ...s, state: 'pending', detail: '' }))
  issues.value = []
  lastError.value = ''
}

async function fetchStatus() {
  return await createResource({ url: 'pwa_builder.api.export_status' }).submit({ project_name: props.projectId })
}

// Load existing publish state; resume the timeline if a job is running.
async function loadStatus() {
  try {
    const st = await fetchStatus()
    repoUrl.value = st.repository_url || ''
    branch.value = st.default_branch || ''
    lastCommit.value = st.last_commit || ''
    jobStatus.value = st.job_status || ''
    if (st.job_status === 'queued' || st.job_status === 'started') {
      running.value = true
      setStep('validate', 'done')
      setStep('queue', 'done')
      setStep('push', 'active')
      poll()
    } else if (st.job_status === 'failed' || (st.result && st.result.success === false)) {
      lastError.value = (st.result && st.result.error) || 'The export job failed — check the error log.'
    }
  } catch (e) {
    /* first load is best effort */
  }
}

async function publish() {
  if (!canPublish.value) return
  running.value = true
  resetSteps()
  setStep('validate', 'active')
  try {
    const res = await createResource({ url: 'pwa_builder.api.validate_form_fields' }).submit({
      project_name: props.projectId,
    })
    if (!res?.success) {
      const missing = res?.forms_with_missing_fields || {}
      issues.value = Object.entries(missing).map(([form, fields]) => ({
        form,
        missing: Object.values(fields || {}).flatMap((v) => (v && typeof v === 'object' ? Object.values(v) : [v])),
      }))
      setStep('validate', 'error', res?.message || 'Some screens are not ready.')
      running.value = false
      return
    }
    setStep('validate', 'done')
    setStep('queue', 'active')
    await createResource({ url: 'pwa_builder.api.export_project' }).submit({ project_name: props.projectId })
    setStep('queue', 'done')
    setStep('push', 'active')
    poll()
  } catch (e) {
    setStep('queue', 'error', (e && e.messages && e.messages[0]) || 'Could not queue the export.')
    running.value = false
  }
}

let timer = null
let polls = 0

function poll() {
  clearInterval(timer)
  polls = 0
  const before = repoUrl.value
  timer = setInterval(async () => {
    polls++
    let st
    try {
      st = await fetchStatus()
    } catch (e) {
      return
    }
    jobStatus.value = st.job_status || ''
    if (st.job_status === 'failed' || (st.result && st.result.success === false)) {
      const msg = (st.result && st.result.error) || 'The export job failed — check the error log.'
      setStep('push', 'error', msg)
      lastError.value = msg
      stopPoll()
      return
    }
    if ((st.result && st.result.success) || (st.repository_url && st.repository_url !== before)) {
      repoUrl.value = st.repository_url || repoUrl.value
      branch.value = st.default_branch || ''
      lastCommit.value = st.last_commit || ''
      setStep('push', 'done')
      setStep('live', 'done', repoUrl.value)
      stopPoll()
      return
    }
    if (polls > 60) {
      setStep('push', 'error', 'Timed out waiting for the job — is a background worker running?')
      stopPoll()
    }
  }, 3000)
}

function stopPoll() {
  clearInterval(timer)
  timer = null
  running.value = false
}

onBeforeUnmount(() => clearInterval(timer))
loadStatus()
</script>

<style scoped>
.pub { padding: 24px; max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
.pub__head { margin-bottom: 4px; }
.pub__title { font-size: 22px; font-weight: 650; color: var(--text); }
.pub__sub { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); padding: 16px 18px; box-shadow: var(--shadow-sm); }
.card__title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 14px; }

.pub__go { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.pub__go-label { font-size: 14px; font-weight: 600; color: var(--text); }
.pub__go-hint { font-size: 12.5px; color: var(--text-muted); margin-top: 3px; }
.pub__blocked { margin-top: 10px; font-size: 12.5px; color: var(--warn); }
.pub__lasterr { display: flex; gap: 7px; align-items: baseline; margin-top: 12px; padding: 10px 12px; font-size: 12.5px; color: var(--danger); background: rgba(220, 38, 38, 0.06); border: 1px solid rgba(220, 38, 38, 0.2); border-radius: var(--radius-control); }

.tl { margin-top: 16px; display: flex; flex-direction: column; }
.tl__step { display: flex; gap: 12px; position: relative; padding-bottom: 18px; }
.tl__step:last-child { padding-bottom: 0; }
.tl__step:not(:last-child)::before { content: ''; position: absolute; left: 11px; top: 24px; bottom: 2px; width: 2px; background: var(--border); }
.tl__dot { display: grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; flex: none; background: var(--surface-muted); color: var(--text-subtle); border: 1px solid var(--border); z-index: 1; }
.tl__step--done .tl__dot { background: var(--ok); border-color: var(--ok); color: #fff; }
.tl__step--active .tl__dot { background: var(--brand-950); border-color: var(--brand-950); color: #fff; }
.tl__step--error .tl__dot { background: var(--danger); border-color: var(--danger); color: #fff; }
.tl__label { font-size: 13.5px; font-weight: 550; color: var(--text); padding-top: 3px; }
.tl__step--pending .tl__label { color: var(--text-subtle); font-weight: 450; }
.tl__detail { font-size: 12px; color: var(--text-muted); margin-top: 3px; word-break: break-all; }
.tl__step--error .tl__detail { color: var(--danger); }

.pub__issues { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
.pub__issue { display: flex; gap: 8px; align-items: baseline; padding: 10px 12px; font-size: 12.5px; color: var(--warn); background: rgba(217, 119, 6, 0.08); border: 1px solid rgba(217, 119, 6, 0.25); border-radius: var(--radius-control); }

.pub__repo-link { font-size: 13.5px; font-weight: 550; color: var(--brand-500); text-decoration: underline; text-underline-offset: 2px; word-break: break-all; }
.pub__repo-meta { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 8px; font-size: 12px; font-family: ui-monospace, monospace; color: var(--text-muted); }

.btn-primary { display: inline-flex; align-items: center; gap: 7px; padding: 10px 18px; font-size: 13.5px; font-weight: 600; color: var(--brand-fg); background: var(--brand-950); border-radius: var(--radius-control); flex: none; }
.btn-primary:hover:not(:disabled) { background: var(--brand-800); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
