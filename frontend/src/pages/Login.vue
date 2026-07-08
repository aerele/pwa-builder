<template>
  <AuthLayout title="Welcome back" subtitle="Sign in to build and publish your PWAs.">
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <FormControl
          required
          type="text"
          label="User ID"
          v-model="email"
          placeholder="johndoe@email.com"
        >
          <template #prefix><FeatherIcon class="w-4" name="mail" /></template>
        </FormControl>
        <p v-if="formSubmitted && !emailValid" class="auth-error">Enter a valid email</p>
      </div>

      <div>
        <div class="relative">
          <FormControl
            required
            label="Password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="••••••"
          >
            <template #prefix><FeatherIcon class="w-4" name="lock" /></template>
          </FormControl>
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="pw-toggle"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
        <p v-if="formSubmitted && !passwordValid" class="auth-error">Enter password</p>
      </div>

      <div class="flex justify-end">
        <router-link to="/forget-password" class="auth-link">Forgot password?</router-link>
      </div>

      <p v-if="loginError" class="auth-alert auth-alert--error">Login failed. Check your credentials.</p>

      <button type="submit" class="btn-primary" :disabled="session.login.loading">
        {{ session.login.loading ? 'Logging in…' : 'Login' }}
      </button>
    </form>

    <template #footer>
      New here?
      <router-link to="/signup" class="auth-link">Create an account</router-link>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, FeatherIcon } from 'frappe-ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { session } from '../data/session'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loginError = ref(false)
const formSubmitted = ref(false)

const emailValid = computed(() => email.value.includes('@') || email.value === 'Administrator')
const passwordValid = computed(() => !!password.value)

function submit() {
  formSubmitted.value = true
  if (!emailValid.value || !passwordValid.value) return

  loginError.value = false
  session.login
    .submit({ email: email.value, password: password.value })
    // onSuccess in data/session.js does a full reload, so no success handling here.
    .catch(() => {
      loginError.value = true
    })
}
</script>

<style scoped>
.pw-toggle {
  position: absolute;
  right: 8px;
  top: 30px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-muted);
}
.btn-primary {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-fg);
  background: var(--brand);
  border-radius: var(--radius-control);
}
.btn-primary:hover:not(:disabled) { background: var(--brand-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.auth-link {
  color: var(--brand);
  font-weight: 500;
}
.auth-link:hover { text-decoration: underline; }
.auth-error {
  margin-top: 4px;
  font-size: 12px;
  color: var(--danger);
}
.auth-alert {
  padding: 8px 12px;
  border-radius: var(--radius-control);
  font-size: 13px;
}
.auth-alert--error {
  color: var(--danger);
  background: rgba(220, 38, 38, 0.08);
}
</style>
