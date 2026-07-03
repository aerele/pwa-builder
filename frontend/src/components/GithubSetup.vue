<template>
  <div class="gh">
    <div v-if="loading" class="gh__hint">Checking GitHub connection…</div>

    <template v-else-if="connected && !editing">
      <div class="gh__row">
        <span class="gh__ok"><FeatherIcon name="check-circle" class="w-4 h-4" /></span>
        <div class="gh__main">
          <div class="gh__label">Connected as {{ username }}</div>
          <div class="gh__hint">Published apps are pushed to this account{{ orgName ? ` (org: ${orgName})` : '' }}.</div>
        </div>
        <button class="gh__ghost" @click="startEdit">Change</button>
      </div>
    </template>

    <template v-else>
      <div class="gh__form">
        <label class="gh__group">
          <span class="gh__flabel">GitHub username</span>
          <input v-model="form.username" class="gh__in" placeholder="octocat" />
        </label>
        <label class="gh__group">
          <span class="gh__flabel">Access token</span>
          <input v-model="form.token" type="password" class="gh__in" placeholder="ghp_…" />
          <span class="gh__hint">A personal access token with repo scope. Stored on this site only.</span>
        </label>
        <label class="gh__check">
          <input v-model="form.isPrivate" type="checkbox" />
          <span>Create private repositories</span>
        </label>
        <template v-if="isAdvanced">
          <label class="gh__check">
            <input v-model="form.useOrg" type="checkbox" />
            <span>Push to an organization</span>
          </label>
          <label v-if="form.useOrg" class="gh__group">
            <span class="gh__flabel">Organization name</span>
            <input v-model="form.orgName" class="gh__in" placeholder="my-org" />
          </label>
        </template>
        <p v-if="error" class="gh__err"><FeatherIcon name="alert-circle" class="w-4 h-4" /> {{ error }}</p>
        <div class="gh__actions">
          <button v-if="connected" class="gh__ghost" @click="editing = false">Cancel</button>
          <button class="gh__save" :disabled="!canSave || saving" @click="save">
            <FeatherIcon :name="saving ? 'loader' : 'check'" class="w-3.5 h-3.5" :class="{ spin: saving }" />
            Save connection
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { FeatherIcon, createResource } from 'frappe-ui'
import { useMode } from '@/composables/useMode'

const emit = defineEmits(['updated'])
const { isAdvanced } = useMode()

const loading = ref(true)
const saving = ref(false)
const editing = ref(false)
const error = ref('')
const username = ref('')
const orgName = ref('')
const isPrivate = ref(false)
const useOrg = ref(false)

const form = reactive({ username: '', token: '', isPrivate: false, useOrg: false, orgName: '' })

const connected = computed(() => !!username.value)
// A new token is required only when connecting for the first time.
const canSave = computed(() => form.username && (form.token || connected.value))

async function load() {
  loading.value = true
  try {
    const doc = await createResource({ url: 'frappe.client.get' }).submit({ doctype: 'PWA GitHub Integration' })
    username.value = doc?.github_username || ''
    isPrivate.value = !!doc?.is_private
    useOrg.value = !!doc?.push_repository_to_an_organization
    orgName.value = doc?.organization_name || ''
    emit('updated', username.value)
  } catch (e) {
    username.value = ''
  } finally {
    loading.value = false
  }
}

function startEdit() {
  form.username = username.value
  form.token = ''
  form.isPrivate = isPrivate.value
  form.useOrg = useOrg.value
  form.orgName = orgName.value
  editing.value = true
}

async function save() {
  if (!canSave.value || saving.value) return
  error.value = ''
  saving.value = true
  try {
    // Merge onto the loaded doc: keeps modified (stale-doc check) and other
    // fields; the stored token comes back masked, which frappe retains as-is.
    const existing = await createResource({ url: 'frappe.client.get' }).submit({ doctype: 'PWA GitHub Integration' })
    const doc = {
      ...existing,
      github_username: form.username,
      is_private: form.isPrivate ? 1 : 0,
      push_repository_to_an_organization: form.useOrg ? 1 : 0,
      organization_name: form.useOrg ? form.orgName : '',
    }
    if (form.token) doc.access_token = form.token
    await createResource({ url: 'frappe.client.save' }).submit({ doc })
    editing.value = false
    await load()
  } catch (e) {
    error.value = (e && e.messages && e.messages[0]) || 'Could not save the connection.'
  } finally {
    saving.value = false
  }
}

load()
</script>

<style scoped>
.gh__row { display: flex; align-items: center; gap: 12px; }
.gh__ok { color: var(--ok); display: grid; place-items: center; }
.gh__main { flex: 1; min-width: 0; }
.gh__label { font-size: 14px; font-weight: 600; color: var(--text); }
.gh__hint { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.gh__form { display: flex; flex-direction: column; gap: 12px; }
.gh__group { display: flex; flex-direction: column; gap: 5px; }
.gh__flabel { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }
.gh__in { padding: 9px 11px; font-size: 13px; color: var(--text); background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-control); outline: none; }
.gh__in:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px var(--brand-ring); }
.gh__check { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text); cursor: pointer; }
.gh__check input { accent-color: var(--brand); }
.gh__err { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--danger); }

.gh__actions { display: flex; justify-content: flex-end; gap: 8px; }
.gh__save { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; font-size: 13px; font-weight: 550; color: var(--brand-fg); background: var(--brand-950); border-radius: var(--radius-control); }
.gh__save:hover:not(:disabled) { background: var(--brand-800); }
.gh__save:disabled { opacity: 0.5; cursor: not-allowed; }
.gh__ghost { font-size: 13px; font-weight: 550; color: var(--text-muted); padding: 8px 12px; border-radius: var(--radius-control); }
.gh__ghost:hover { color: var(--text); background: var(--surface-muted); }
.spin { animation: sp 0.8s linear infinite; }
@keyframes sp { to { transform: rotate(360deg); } }
</style>
