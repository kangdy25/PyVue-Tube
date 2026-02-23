<template>
  <div class="input-card" :class="{ 'is-focused': isInputFocused }">
    <div class="icon-wrapper">
      <LinkIcon class="input-icon" />
    </div>
    <input 
      v-model="localUrl" 
      type="text" 
      placeholder="Paste YouTube URL here..." 
      class="url-input"
      @keyup.enter="onSubmit"
      @focus="isInputFocused = true"
      @blur="isInputFocused = false"
    />
    <button 
      @click="onSubmit" 
      :disabled="isLoading"
      class="btn-primary analyze-btn"
    >
      <div class="btn-shimmer"></div>
      <span v-if="!isLoading" class="btn-content">
        <Search class="btn-icon" />
        Analyze
      </span>
      <span v-else class="btn-content">
        <Loader2 class="btn-icon spinner" />
        Loading
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { LinkIcon, Search, Loader2 } from 'lucide-vue-next'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const localUrl = ref(props.modelValue)
const isInputFocused = ref(false)

watch(localUrl, (newVal) => {
  emit('update:modelValue', newVal)
})
watch(() => props.modelValue, (newVal) => {
  localUrl.value = newVal
})

const onSubmit = () => {
  emit('submit', localUrl.value)
}
</script>

<style lang="scss" scoped>
$primary-color: #4f46e5; // Indigo 600
$primary-hover: #6366f1; // Indigo 500
$secondary-color: #7c3aed; // Violet 600
$secondary-hover: #8b5cf6; // Violet 500
$bg-slate-950: #020617;
$bg-slate-900: #0f172a;
$text-slate-100: #f1f5f9;
$text-slate-400: #94a3b8;
$text-slate-500: #64748b;

$glass-bg: rgba(255, 255, 255, 0.03);
$glass-border: rgba(255, 255, 255, 0.1);
$glass-blur: blur(12px);

$transition-snappy: 300ms cubic-bezier(0.4, 0, 0.2, 1);

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.input-card {
  background-color: $glass-bg;
  backdrop-filter: blur(24px);
  border: 1px solid $glass-border;
  border-radius: 1.5rem;
  padding: 0.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all $transition-snappy;

  &.is-focused {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 0 30px -5px rgba(99, 102, 241, 0.2);

    .icon-wrapper {
      color: #818cf8; // Indigo 400
    }
  }
}

.icon-wrapper {
  padding-left: 1rem;
  color: $text-slate-500;
  transition: color $transition-snappy;

  .input-icon {
    width: 1.25rem;
    height: 1.25rem;
  }
}

.url-input {
  flex: 1;
  background-color: transparent;
  border: none;
  outline: none;
  padding: 1rem 0.5rem;
  color: $text-slate-100;
  font-size: 1.125rem;

  &::placeholder {
    color: #475569; // Slate 600
  }
}

.btn-primary {
  position: relative;
  overflow: hidden;
  background-color: $primary-color;
  color: white;
  padding: 1rem;
  border-radius: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transition: all $transition-snappy;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;

  &:hover:not(:disabled) {
    background-color: $primary-hover;
    
    .btn-shimmer {
      animation: shimmer 1.5s infinite;
    }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-shimmer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background-image: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
    transform: translateX(-100%);
  }

  .btn-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
  }

  .btn-icon {
    width: 1.25rem;
    height: 1.25rem;
  }
}

.spinner {
  animation: spin 1s linear infinite;
}
</style>
