<template>
  <div class="progress-card">
    <div class="progress-header">
      <div class="status-container">
        <Loader2 v-if="isActive" class="status-icon spinner indigo-text" />
        <AlertCircle v-else-if="failed > 0 || cancelled" class="status-icon error-text" />
        <CheckCircle2 v-else class="status-icon success-text" />
        <span class="status-text">{{ downloadStatus }}</span>
      </div>
      <span class="progress-percentage">
        {{ progress.toFixed(1) }}<span class="percentage-symbol">%</span>
      </span>
    </div>

    <div v-if="total" class="batch-summary">
      항목 {{ current || completed }}/{{ total }} · 완료 {{ completed }} · 실패 {{ failed }}
      <span v-if="cancelled && remaining"> · 남음 {{ remaining }}</span>
    </div>
    
    <!-- Premium Animated Progress Bar -->
    <div class="progress-bar-container">
      <div 
        class="progress-bar-fill"
        :class="{
          'is-complete': progress >= 100 && failed === 0 && !cancelled,
          'has-error': failed > 0 || cancelled
        }"
      >
        <div class="progress-stripes"></div>
      </div>
    </div>

    <div class="job-actions">
      <button v-if="isActive" type="button" class="btn-job cancel" @click="$emit('cancel')">
        <Square class="btn-icon" />
        다운로드 취소
      </button>
      <button v-else-if="canRetry" type="button" class="btn-job retry" @click="$emit('retry')">
        <RotateCcw class="btn-icon" />
        {{ cancelled ? '남은 항목 재시도' : '실패 항목 재시도' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loader2, CheckCircle2, AlertCircle, RotateCcw, Square } from 'lucide-vue-next'

defineEmits(['cancel', 'retry'])

const props = defineProps({
  progress: {
    type: Number,
    required: true
  },
  downloadStatus: {
    type: String,
    required: true
  },
  current: {
    type: Number,
    default: null
  },
  total: {
    type: Number,
    default: null
  },
  completed: {
    type: Number,
    default: 0
  },
  failed: {
    type: Number,
    default: 0
  },
  remaining: {
    type: Number,
    default: 0
  },
  isActive: {
    type: Boolean,
    default: false
  },
  canRetry: {
    type: Boolean,
    default: false
  },
  cancelled: {
    type: Boolean,
    default: false
  }
})

// Dynamic style bindings
const progressWidth = computed(() => `${Math.max(props.progress, 3)}%`);
</script>

<style lang="scss" scoped>
$primary-color: #4f46e5; // Indigo 600
$primary-hover: #6366f1; // Indigo 500
$secondary-color: #7c3aed; // Violet 600
$secondary-hover: #8b5cf6; // Violet 500
$bg-slate-950: #020617;
$bg-slate-900: #0f172a;

$glass-border: rgba(255, 255, 255, 0.1);

@keyframes stripes {
  0% {
    background-position: 1rem 0;
  }
  100% {
    background-position: 0 0;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.progress-card {
  background-color: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  padding: 1.5rem;
  border-radius: 1.5rem;
  border: 1px solid $glass-border;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;

  .status-icon {
    width: 1.25rem;
    height: 1.25rem;
    
    &.indigo-text { color: #818cf8; }
    &.success-text { color: #34d399; } // Emerald 400
    &.error-text { color: #f87171; }
  }

  .status-text {
    color: #cbd5e1; // Slate 300
    font-weight: 500;
    letter-spacing: 0.025em;
  }
}

.progress-percentage {
  font-size: 1.875rem;
  font-weight: 900;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  background-image: linear-gradient(to right, #818cf8, #a78bfa);

  .percentage-symbol {
    font-size: 1.125rem;
  }
}

.batch-summary {
  color: #94a3b8;
  font-size: 0.8125rem;
  font-weight: 600;
}

.spinner {
  animation: spin 1s linear infinite;
}

.progress-bar-container {
  width: 100%;
  background-color: $bg-slate-950;
  border-radius: 9999px;
  height: 1rem;
  padding: 0.25rem;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.progress-bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: all 300ms ease-out;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  background-image: linear-gradient(to right, $primary-hover, $secondary-hover);
  // Using v-bind injected variable
  width: v-bind(progressWidth);

  &.is-complete {
    background-image: linear-gradient(to right, #10b981, #2dd4bf); // Emerald 500 to Teal 400
  }

  &.has-error {
    background-image: linear-gradient(to right, #ef4444, #f97316);
  }

  .progress-stripes {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.15) 50%,
      rgba(255, 255, 255, 0.15) 75%,
      transparent 75%,
      transparent
    );
    background-size: 1rem 1rem;
    animation: stripes 1s linear infinite;
    opacity: 0.5;
  }
}

.job-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-job {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.875rem;
  border-radius: 0.625rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 200ms ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  &.cancel:hover {
    border-color: rgba(248, 113, 113, 0.45);
    color: #fca5a5;
  }

  &.retry:hover {
    border-color: rgba(129, 140, 248, 0.45);
    color: #c7d2fe;
  }

  .btn-icon {
    width: 0.875rem;
    height: 0.875rem;
  }
}
</style>
