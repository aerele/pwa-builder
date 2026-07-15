<template>
  <div class="auth pwa-app-bg">
    <div class="auth__wrap">
      <div class="auth__brand">
        <img class="auth__logo-img" :src="appLogo" alt="PWA Builder" width="36" height="36" />
        <span class="auth__wordmark">PWA Builder</span>
      </div>
      <div class="auth__card">
        <h1 class="auth__title">{{ title }}</h1>
        <p v-if="subtitle" class="auth__subtitle">{{ subtitle }}</p>
        <slot />
      </div>
      <div v-if="$slots.footer" class="auth__footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup>
// Shared shell for the pre-auth pages (Login/SignUp/Forgot). Importing useTheme
// applies the stored light/dark preference on these pages too, which live
// outside AppShell.
import { useTheme } from '@/composables/useTheme'
import appLogo from '@/assets/pwa-builder-logo.png'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})

useTheme()
</script>

<style scoped>
.auth {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}
.auth__wrap {
  width: 100%;
  max-width: 400px;
}
.auth__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}
.auth__logo-img {
  width: 36px;
  height: 36px;
  display: block;
  object-fit: contain;
  border-radius: 9px;
}
.auth__logo {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  background: var(--brand);
  color: #fff;
  font-weight: 700;
  border-radius: var(--radius-control);
}
.auth__wordmark {
  font-weight: 600;
  font-size: 18px;
  color: var(--text);
}
.auth__card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-md);
  padding: 28px 24px;
}
.auth__title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}
.auth__subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
}
.auth__footer {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
