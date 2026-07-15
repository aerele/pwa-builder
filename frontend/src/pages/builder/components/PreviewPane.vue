<template>
  <div ref="wrap" class="pv">
    <PhoneFrame :width="W" :height="H" :scale="scale">
      <!-- theme-light: the generated app is light regardless of builder theme -->
      <div class="pv__screen theme-light">
        <header class="pv__appbar">
          <FeatherIcon name="menu" class="pv__appbar-ico" />
          <span class="pv__appbar-title">{{ title }}</span>
          <FeatherIcon name="user" class="pv__appbar-ico" />
        </header>

        <div
          class="pv__body"
          :class="{
            'pv__body--grid': isDashboard && visibleFields.length,
            'pv__body--empty': !visibleFields.length,
          }"
        >
          <template v-if="visibleFields.length">
            <PreviewField
              v-for="f in visibleFields"
              :key="f.fieldname"
              :field="f"
              :selected="f.fieldname === selected"
              @click="$emit('select', f.fieldname)"
            />
          </template>
          <div v-else class="pv__empty">
            <FeatherIcon name="smartphone" class="pv__empty-ico" />
            <p class="pv__empty-text">
              Your screen is empty.<br />
              Add fields to see them live.
            </p>
          </div>
        </div>

        <div v-if="!isDashboard && visibleFields.length" class="pv__submit">
          {{ isSubmittable ? 'Submit' : 'Save' }}
        </div>
      </div>
    </PhoneFrame>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import PhoneFrame from '@/components/PhoneFrame.vue'
import PreviewField from './PreviewField.vue'

const props = defineProps({
  fields: { type: Array, required: true },
  title: { type: String, default: 'Screen' },
  selected: { type: String, default: null },
  isDashboard: { type: Boolean, default: false },
  isSubmittable: { type: [Number, Boolean], default: 0 },
})
defineEmits(['select'])

const W = 340
const H = 690

// Hide layout-only fieldtypes if they ever land on the canvas
const HIDDEN = new Set(['Section Break', 'Column Break', 'Tab Break', 'Fold', 'Heading'])
const visibleFields = computed(() =>
  (props.fields || []).filter((f) => f && f.fieldtype && !HIDDEN.has(f.fieldtype))
)

// Fit the phone to whatever space the pane gives us.
const wrap = ref(null)
const scale = ref(0.8)
let ro = null

function fit() {
  if (!wrap.value) return
  const pad = 28
  // PhoneFrame outer size includes 20px bezel chrome
  const outerW = W + 20
  const outerH = H + 20
  const s = Math.min(
    (wrap.value.clientWidth - pad) / outerW,
    (wrap.value.clientHeight - pad) / outerH,
    1
  )
  scale.value = Math.max(Number.isFinite(s) ? s : 0.5, 0.28)
}

onMounted(() => {
  fit()
  if (typeof ResizeObserver !== 'undefined' && wrap.value) {
    ro = new ResizeObserver(() => fit())
    ro.observe(wrap.value)
  }
  // Re-fit after fonts/layout settle
  requestAnimationFrame(fit)
})
onBeforeUnmount(() => ro && ro.disconnect())
</script>

<style scoped>
.pv {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-sizing: border-box;
  padding: 8px;
}

/* Fill the phone screen height so body can scroll */
.pv__screen {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: #ffffff;
  color: #111827;
  font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.pv__appbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex: none;
  padding: 28px 14px 12px;
  background: #05102a;
  color: #ffffff;
}
.pv__appbar-title {
  flex: 1;
  min-width: 0;
  text-align: center;
  font-size: 13.5px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pv__appbar-ico {
  width: 16px;
  height: 16px;
  flex: none;
  opacity: 0.95;
}

/* min-height: 0 is required for overflow-y to work inside a flex column */
.pv__body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 12px 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 11px;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  background: #f8fafc;
}
.pv__body--grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-content: start;
  gap: 10px;
}

/* Empty: fill the phone body and center icon + copy both axes */
.pv__body--empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 24px 20px;
}

.pv__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  max-width: 220px;
  margin: 0 auto;
  color: #9ca3af;
  text-align: center;
}
.pv__empty-ico {
  display: block;
  width: 28px;
  height: 28px;
  flex: none;
  margin: 0 auto;
  opacity: 0.85;
}
.pv__empty-text {
  margin: 0;
  width: 100%;
  font-size: 12.5px;
  line-height: 1.5;
  text-align: center;
  color: #9ca3af;
}

.pv__submit {
  flex: none;
  margin: 0 14px 14px;
  padding: 12px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  background: #05102a;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.08);
}
</style>
