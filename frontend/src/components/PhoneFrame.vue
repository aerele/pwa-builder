<template>
  <!-- Reusable device frame. Three contexts: dashboard thumbnails (scaled,
       non-interactive), screen cards, and the builder live preview. -->
  <div class="phone-frame" :style="frameStyle">
    <!-- Scale the whole bezel (padding + screen) so chrome and content stay aligned. -->
    <div class="phone-frame__scale" :style="scaleStyle">
      <div class="phone-frame__bezel">
        <div v-if="deviceFrame" class="phone-frame__notch" aria-hidden="true"></div>
        <div class="phone-frame__screen" :style="screenStyle">
          <slot>
            <div class="phone-frame__placeholder">
              <FeatherIcon name="smartphone" class="w-6 h-6" />
              <span>Preview</span>
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const BEZEL_PAD = 10 // matches .phone-frame__bezel padding

const props = defineProps({
  width: { type: Number, default: 375 }, // logical screen width (px)
  height: { type: Number, default: 720 },
  scale: { type: Number, default: 1 }, // 1 = full, <1 for thumbnails
  deviceFrame: { type: Boolean, default: true }, // bezel + notch
})

const chrome = computed(() => (props.deviceFrame ? BEZEL_PAD * 2 : 0))

const frameStyle = computed(() => ({
  // Layout box = full device (bezel chrome + screen) after scale
  width: `${(props.width + chrome.value) * props.scale}px`,
  height: `${(props.height + chrome.value) * props.scale}px`,
}))

const scaleStyle = computed(() => ({
  width: `${props.width + chrome.value}px`,
  height: `${props.height + chrome.value}px`,
  transform: props.scale === 1 ? 'none' : `scale(${props.scale})`,
  transformOrigin: 'top left',
}))

const screenStyle = computed(() => ({
  width: `${props.width}px`,
  height: `${props.height}px`,
}))
</script>

<style scoped>
.phone-frame {
  position: relative;
  flex: none;
}
.phone-frame__scale {
  position: absolute;
  top: 0;
  left: 0;
}
.phone-frame__bezel {
  box-sizing: border-box;
  padding: 10px;
  background: var(--brand-950, #05102a);
  border-radius: var(--radius-phone, 2rem);
  box-shadow: var(--shadow-md);
  /* Don't clip the scaled subtree's box; screen handles internal overflow. */
  overflow: visible;
}
.phone-frame__notch {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 38%;
  height: 16px;
  background: var(--brand-950, #05102a);
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  z-index: 2;
  pointer-events: none;
}
.phone-frame__screen {
  position: relative;
  box-sizing: border-box;
  background: #ffffff;
  border-radius: calc(var(--radius-phone, 2rem) - 8px);
  overflow: hidden;
  /* Critical: establish a real block formatting context for % heights */
  display: flex;
  flex-direction: column;
}
.phone-frame__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-subtle, #9ca3af);
  font-size: 13px;
}
</style>
