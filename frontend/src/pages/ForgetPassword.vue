<template>
  <AuthLayout
    title="Reset your password"
    subtitle="We'll email you instructions to reset it."
  >
    <form @submit.prevent="resetPassword" class="space-y-4">
      <FormControl
        required
        type="text"
        label="Email"
        v-model="email"
        placeholder="johndoe@email.com"
      >
        <template #prefix><FeatherIcon class="w-4" name="mail" /></template>
      </FormControl>
      <p v-if="formSubmitted && !emailValid" class="auth-error">Enter your email</p>

      <p v-if="message" class="auth-alert" :class="`auth-alert--${messageType}`">{{ message }}</p>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? 'Sending…' : 'Reset Password' }}
      </button>
    </form>

    <template #footer>
      <router-link to="/login" class="auth-link">Back to login</router-link>
    </template>
  </AuthLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, FeatherIcon, createResource } from 'frappe-ui'
import AuthLayout from '@/components/AuthLayout.vue'

const email = ref('')
const message = ref('')
const messageType = ref('ok')
const formSubmitted = ref(false)
const loading = ref(false)

const emailValid = computed(() => !!email.value)

// Same-origin call — the whitelisted (guest) reset endpoint on this site.
const reset = createResource({ url: 'frappe.core.doctype.user.user.reset_password' })

function resetPassword() {
  formSubmitted.value = true
  message.value = ''
  if (!emailValid.value) return

  loading.value = true
  reset
    .submit({ user: email.value })
    .then(() => {
      messageType.value = 'ok'
      message.value = 'Password reset instructions have been sent to your email.'
    })
    .catch((error) => {
      messageType.value = 'error'
      const status = error?.response?.status
      if (status === 404) message.value = 'No user found with that email.'
      else if (status === 501) message.value = 'Email is not configured on this site yet.'
      else message.value = 'Too many requests. Please try again later.'
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<style scoped>
.auth-link {
  color: var(--brand);
  font-weight: 500;
}
.auth-link:hover { text-decoration: underline; }
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
