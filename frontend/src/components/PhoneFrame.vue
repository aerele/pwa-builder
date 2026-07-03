<template>
  <!-- Reusable device frame. Three contexts: dashboard thumbnails (scaled,
       non-interactive), screen cards, and the builder live preview. -->
  <div class="phone-frame" :style="frameStyle">
    <div class="phone-frame__bezel">
      <div v-if="deviceFrame" class="phone-frame__notch"></div>
      <div class="phone-frame__screen" :style="screenStyle">
        <slot>
          <!-- Empty-state placeholder shown when no screen content is bound -->
          <div class="phone-frame__placeholder">
            <FeatherIcon name="smartphone" class="w-6 h-6" />
            <span>Preview</span>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  width: { type: Number, default: 375 }, // logical screen width (px)
  height: { type: Number, default: 720 },
  scale: { type: Number, default: 1 }, // 1 = full, <1 for thumbnails
  deviceFrame: { type: Boolean, default: true }, // bezel + notch
})

const frameStyle = computed(() => ({
  // Reserve laid-out space equal to the scaled size so flow layout is correct.
  width: `${props.width * props.scale}px`,
  height: `${props.height * props.scale}px`,
}))

const screenStyle = computed(() => ({
  width: `${props.width}px`,
  height: `${props.height}px`,
  transform: props.scale === 1 ? 'none' : `scale(${props.scale})`,
  transformOrigin: 'top left',
}))
</script>

<style scoped>
.phone-frame {
  position: relative;
}
.phone-frame__bezel {
  position: absolute;
  inset: 0;
  padding: 10px;
  background: var(--brand-950);
  border-radius: var(--radius-phone);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.phone-frame__notch {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 38%;
  height: 16px;
  background: var(--brand-950);
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  z-index: 2;
}
.phone-frame__screen {
  position: relative;
  background: var(--surface);
  border-radius: calc(var(--radius-phone) - 8px);
  overflow: hidden;
}
.phone-frame__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-subtle);
  font-size: 13px;
}
</style>
