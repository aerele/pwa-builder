<template>
  <!-- Create a PWA project + connect a remote site. Single-step for now;
       the multi-step "Test connection" wizard arrives with the backend
       session (needs a non-persisting test_connection endpoint). -->
  <div v-if="modelValue" class="np">
    <div class="np__scrim" @click="close" />
    <div class="np__card" role="dialog" aria-modal="true">
      <header class="np__head">
        <h2 class="np__title">New project</h2>
        <button class="np__x" @click="close"><FeatherIcon name="x" class="w-4 h-4" /></button>
      </header>

      <div class="np__body">
        <!-- Where does this PWA's data live? -->
        <div class="np__seg" role="tablist" aria-label="Connection">
          <button
            v-for="opt in connOptions"
            :key="opt.value"
            role="tab"
            :aria-selected="form.connection_type === opt.value"
            class="np__seg-btn"
            :class="{ 'np__seg-btn--active': form.connection_type === opt.value }"
            @click="form.connection_type = opt.value"
          >
            <FeatherIcon :name="opt.icon" class="w-3.5 h-3.5" />
            {{ opt.label }}
          </button>
        </div>
        <p class="np__seg-hint">
          <FeatherIcon name="info" class="w-3.5 h-3.5" />
          {{ isLocal ? 'Builds on this site — no URL or login needed.' : 'Connect to a different Frappe site.' }}
        </p>

        <div class="np__field">
          <label>Project title <i>*</i></label>
          <input v-model="form.project_title" type="text" placeholder="e.g. Field Service" />
        </div>
        <div class="np__field">
          <label>Route name</label>
          <input v-model="form.sub_title" type="text" placeholder="e.g. field-service" />
        </div>

        <template v-if="!isLocal">
          <div class="np__field">
            <label>Site URL <i>*</i></label>
            <input v-model="form.site_url" type="text" placeholder="https://your-site.com" />
          </div>
          <div class="np__grid">
            <div class="np__field">
              <label>User ID <i>*</i></label>
              <input v-model="form.user_id" type="email" placeholder="you@example.com" />
            </div>
            <div class="np__field">
              <label>Password <i>*</i></label>
              <input v-model="form.password" type="password" placeholder="••••••••" />
            </div>
          </div>
        </template>
        <div class="np__field">
          <label>Description</label>
          <textarea v-model="form.description" rows="2" placeholder="Optional"></textarea>
        </div>

        <p v-if="error" class="np__error"><FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ error }}</p>
      </div>

      <footer class="np__foot">
        <button class="btn-ghost" @click="close">Cancel</button>
        <button class="btn-primary" :disabled="!canSubmit || creating" @click="submit">
          <FeatherIcon v-if="creating" name="loader" class="w-4 h-4 np__spin" />
          {{ creating ? 'Connecting…' : 'Create project' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { FeatherIcon, createResource } from 'frappe-ui'
import { projects } from '@/data/projects'

const props = defineProps({ modelValue: { type: Boolean, default: false } })
const emit = defineEmits(['update:modelValue', 'created'])

const blank = () => ({
  project_title: '',
  connection_type: 'This Site',
  sub_title: '',
  site_url: '',
  user_id: '',
  password: '',
  description: '',
})
const form = reactive(blank())
const error = ref('')
const creating = ref(false)

const connOptions = [
  { value: 'This Site', label: 'This site', icon: 'home' },
  { value: 'Another Site', label: 'Another site', icon: 'globe' },
]
const isLocal = computed(() => form.connection_type === 'This Site')

const canSubmit = computed(() => {
  if (!form.project_title) return false
  if (isLocal.value) return true
  return !!(form.site_url && form.user_id && form.password)
})

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      Object.assign(form, blank())
      error.value = ''
    }
  }
)

const createSite = createResource({
  url: 'pwa_builder.api.add_site',
  onSuccess(result) {
    creating.value = false
    // add_site returns "Created" | "Updated" | "Invalid credentials"
    if (result === 'Invalid credentials') {
      error.value = 'Could not connect — check the site URL and credentials.'
      return
    }
    projects.reload()
    emit('created')
    close()
  },
  onError(err) {
    creating.value = false
    error.value = (err && err.messages && err.messages[0]) || 'Something went wrong. Please try again.'
  },
})

function submit() {
  if (!canSubmit.value || creating.value) return
  error.value = ''
  creating.value = true
  createSite.submit({ data: { ...form } })
}

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.np { position: fixed; inset: 0; z-index: 50; display: grid; place-items: center; }
.np__scrim { position: absolute; inset: 0; background: rgba(5, 16, 42, 0.45); backdrop-filter: blur(1px); }
.np__card {
  position: relative;
  width: 480px;
  max-width: calc(100vw - 32px);
  background: var(--surface);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.np__head { display: flex; align-items: center; justify-content: space-between; padding: 16px 18px; border-bottom: 1px solid var(--border); }
.np__title { font-size: 16px; font-weight: 650; color: var(--text); }
.np__x { color: var(--text-subtle); }
.np__x:hover { color: var(--text); }
.np__body { padding: 18px; display: flex; flex-direction: column; gap: 12px; max-height: 60vh; overflow: auto; }

/* Connection switch */
.np__seg { display: flex; gap: 4px; padding: 3px; background: var(--surface-muted); border: 1px solid var(--border); border-radius: var(--radius-control); }
.np__seg-btn {
  flex: 1; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 7px 10px; font-size: 13px; font-weight: 550; color: var(--text-muted);
  border-radius: calc(var(--radius-control) - 1px); transition: all 0.12s ease;
}
.np__seg-btn--active { background: var(--surface); color: var(--brand); box-shadow: var(--shadow-sm); }
.np__seg-hint { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); margin-top: -4px; }
.np__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.np__field { display: flex; flex-direction: column; gap: 5px; }
.np__field label { font-size: 12.5px; font-weight: 550; color: var(--text); }
.np__field label i { color: var(--danger); font-style: normal; }
.np__field input,
.np__field textarea {
  width: 100%;
  padding: 8px 10px;
  font-size: 13px;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-control);
  outline: none;
  transition: border-color 0.12s ease, box-shadow 0.12s ease;
}
.np__field input:focus,
.np__field textarea:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }
.np__error { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--danger); }
.np__foot { display: flex; align-items: center; justify-content: flex-end; gap: 10px; padding: 14px 18px; border-top: 1px solid var(--border); background: var(--surface-muted); }
.np__spin { animation: np-spin 0.8s linear infinite; }
@keyframes np-spin { to { transform: rotate(360deg); } }

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; font-size: 13px; font-weight: 550;
  color: var(--brand-fg); background: var(--brand-950);
  border-radius: var(--radius-control); transition: background 0.12s ease;
}
.btn-primary:hover { background: var(--brand-800); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { font-size: 13px; font-weight: 550; color: var(--text-muted); padding: 8px 12px; border-radius: var(--radius-control); }
.btn-ghost:hover { background: var(--surface); color: var(--text); }
</style>
