<template>
  <section class="settings">
    <div class="settings__head">
      <h1 class="settings__title">Settings</h1>
      <p class="settings__subtitle">Account, builder mode, and integrations.</p>
    </div>

    <!-- Builder mode (functional in Phase 0) -->
    <div class="card">
      <div class="card__row">
        <div>
          <div class="card__label">Builder mode</div>
          <div class="card__hint">Simple hides advanced controls. Switch any time.</div>
        </div>
        <ModeToggle />
      </div>
    </div>

    <!-- GitHub integration (advanced) -->
    <div v-if="isAdvanced" class="card">
      <div class="card__label">GitHub integration</div>
      <div class="card__hint" style="margin-bottom: 12px">Used to publish exported apps.</div>
      <GithubSetup />
    </div>

    <div class="card">
      <div class="card__row">
        <div>
          <div class="card__label">Account</div>
          <div class="card__hint">{{ user }}</div>
        </div>
        <button class="btn-ghost" @click="session.logout.submit()">Log out</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import ModeToggle from '@/shell/ModeToggle.vue'
import GithubSetup from '@/components/GithubSetup.vue'
import { useMode } from '@/composables/useMode'
import { session } from '@/data/session'

const { isAdvanced } = useMode()
const user = computed(() => session.user || 'Guest')
</script>

<style scoped>
.settings { padding: 24px; max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
.settings__head { margin-bottom: 4px; }
.settings__title { font-size: 22px; font-weight: 650; color: var(--text); }
.settings__subtitle { margin-top: 4px; font-size: 13.5px; color: var(--text-muted); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); padding: 16px 18px; box-shadow: var(--shadow-sm); }
.card__row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.card__label { font-size: 14px; font-weight: 600; color: var(--text); }
.card__hint { font-size: 12.5px; color: var(--text-muted); margin-top: 3px; }
.badge { font-size: 11px; font-weight: 600; color: var(--brand); background: var(--brand-subtle); padding: 4px 10px; border-radius: 999px; }
.btn-ghost { font-size: 13px; font-weight: 550; color: var(--danger); padding: 7px 12px; border-radius: var(--radius-control); }
.btn-ghost:hover { background: var(--surface-muted); }
</style>
