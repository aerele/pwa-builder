<template>
  <AuthLayout title="Create your account" subtitle="Start building PWAs in minutes.">
    <form @submit.prevent="signUp" class="space-y-4">
      <FormControl
        required
        type="text"
        label="Username"
        v-model="username"
        placeholder="johndoe"
      >
        <template #prefix><FeatherIcon class="w-4" name="user" /></template>
      </FormControl>

      <FormControl
        required
        type="email"
        label="Email"
        v-model="email"
        placeholder="johndoe@email.com"
      >
        <template #prefix><FeatherIcon class="w-4" name="mail" /></template>
      </FormControl>

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
        <button type="button" @click="showPassword = !showPassword" class="pw-toggle">
          {{ showPassword ? 'Hide' : 'Show' }}
        </button>
      </div>

      <div class="relative">
        <FormControl
          required
          label="Confirm Password"
          v-model="confirmPassword"
          :type="showConfirm ? 'text' : 'password'"
          placeholder="••••••"
        >
          <template #prefix><FeatherIcon class="w-4" name="lock" /></template>
        </FormControl>
        <button type="button" @click="showConfirm = !showConfirm" class="pw-toggle">
          {{ showConfirm ? 'Hide' : 'Show' }}
        </button>
      </div>

      <p v-if="formSubmitted && !emailValid" class="auth-error">Enter a valid email</p>
      <p v-if="formSubmitted && !passwordsMatch" class="auth-error">Passwords do not match</p>

      <p v-if="message" class="auth-alert" :class="`auth-alert--${messageType}`">{{ message }}</p>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? 'Creating…' : 'Sign Up' }}
      </button>
    </form>

    <template #footer>
      Already have an account?
      <router-link to="/login" class="auth-link">Back to login</router-link>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, FeatherIcon, createListResource } from 'frappe-ui'
import AuthLayout from '@/components/AuthLayout.vue'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const message = ref('')
const messageType = ref('error')
const formSubmitted = ref(false)
const loading = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)

const emailValid = computed(() => /\S+@\S+\.\S+/.test(email.value))
const passwordsMatch = computed(() => password.value === confirmPassword.value)

function signUp() {
  formSubmitted.value = true
  message.value = ''
  if (!emailValid.value || !passwordsMatch.value) return

  loading.value = true
  const users = createListResource({ doctype: 'User' })
  users.insert
    .submit({ email: email.value, first_name: username.value, new_password: password.value })
    .then(() => {
      messageType.value = 'ok'
      message.value = 'Account created. You can now log in.'
    })
    .catch((error) => {
      messageType.value = 'error'
      const status = error?.response?.status
      if (status === 417) message.value = 'Password is too weak'
      else if (status === 409) message.value = 'Email already exists'
      else message.value = 'Could not create the account'
    })
    .finally(() => {
      loading.value = false
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
  margin-top: -8px;
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
.auth-alert--ok {
  color: var(--ok);
  background: rgba(22, 163, 74, 0.08);
}
</style>
