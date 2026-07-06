<template>
  <div ref="wrap" class="pv">
    <PhoneFrame :width="W" :height="H" :scale="scale">
      <!-- theme-light: the generated app is light regardless of builder theme -->
      <div class="pv__screen theme-light">
        <div class="pv__appbar">
          <FeatherIcon name="menu" class="w-4 h-4" />
          <span class="pv__appbar-title">{{ title }}</span>
          <FeatherIcon name="user" class="w-4 h-4" />
        </div>
        <div class="pv__body" :class="{ 'pv__body--grid': isDashboard }">
          <template v-if="fields.length">
            <PreviewField
              v-for="f in fields"
              :key="f.fieldname"
              :field="f"
              :selected="f.fieldname === selected"
              @click="$emit('select', f.fieldname)"
            />
          </template>
          <div v-else class="pv__empty">
            <FeatherIcon name="smartphone" class="w-6 h-6" />
            <p>Your screen is empty.<br />Add fields to see them live.</p>
          </div>
        </div>
        <div v-if="!isDashboard && fields.length" class="pv__submit">{{ isSubmittable ? 'Submit' : 'Save' }}</div>
      </div>
    </PhoneFrame>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import PhoneFrame from '@/components/PhoneFrame.vue'
import PreviewField from './PreviewField.vue'

defineProps({
  fields: { type: Array, required: true },
  title: { type: String, default: 'Screen' },
  selected: { type: String, default: null },
  isDashboard: { type: Boolean, default: false },
  isSubmittable: { type: [Number, Boolean], default: 0 },
})
defineEmits(['select'])

const W = 340
const H = 690

// Fit the phone to whatever space the pane gives us.
const wrap = ref(null)
const scale = ref(0.8)
let ro = null

function fit() {
  if (!wrap.value) return
  const pad = 24
  const s = Math.min((wrap.value.clientWidth - pad) / W, (wrap.value.clientHeight - pad) / H, 1)
  scale.value = Math.max(s, 0.3)
}

onMounted(() => {
  fit()
  ro = new ResizeObserver(fit)
  ro.observe(wrap.value)
})
onBeforeUnmount(() => ro && ro.disconnect())
</script>

<style scoped>
.pv { height: 100%; display: flex; align-items: center; justify-content: center; overflow: hidden; }

.pv__screen { display: flex; flex-direction: column; height: 100%; background: var(--surface); }
.pv__appbar { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 26px 14px 12px; background: var(--brand); color: #fff; }
.pv__appbar-title { flex: 1; text-align: center; font-size: 13.5px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.pv__body { flex: 1; overflow-y: auto; padding: 14px 14px 18px; display: flex; flex-direction: column; gap: 12px; }
.pv__body--grid { display: grid; grid-template-columns: 1fr 1fr; align-content: start; }

.pv__empty { display: flex; flex-direction: column; align-items: center; gap: 10px; margin: auto; color: var(--text-subtle); font-size: 12.5px; text-align: center; }

.pv__submit { margin: 0 14px 16px; padding: 11px; text-align: center; font-size: 13px; font-weight: 600; color: var(--brand-fg); background: var(--brand); border-radius: 10px; flex: none; }
</style>
