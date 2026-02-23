<template>
  <div class="app-container">
    
    <!-- Background Ambient Glow -->
    <div class="ambient-glow glow-indigo"></div>
    <div class="ambient-glow glow-violet"></div>

    <div class="main-wrapper">
      
      <!-- Header -->
      <header class="app-header">
        <div class="logo-icon-wrapper">
          <Youtube class="logo-icon" />
        </div>
        <h1 class="app-title">PyVue-Tube</h1>
        <p class="app-subtitle">Premium YouTube Downloader</p>
      </header>

      <!-- Main Input Card -->
      <div class="input-card" :class="{ 'is-focused': isInputFocused }">
        <div class="icon-wrapper">
          <LinkIcon class="input-icon" />
        </div>
        <input 
          v-model="url" 
          type="text" 
          placeholder="Paste YouTube URL here..." 
          class="url-input"
          @keyup.enter="fetchInfo"
          @focus="isInputFocused = true"
          @blur="isInputFocused = false"
        />
        <button 
          @click="fetchInfo" 
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

      <!-- Video Info & Actions (Animated Entrance) -->
      <transition name="fade-slide">
        <div v-if="videoInfo" class="video-info-card">
          
          <!-- Thumbnail Section -->
          <div class="thumbnail-wrapper">
            <img :src="videoInfo.thumbnail" class="thumbnail-img" alt="Thumbnail" />
            <div class="thumbnail-overlay"></div>
            <div class="duration-badge">
              <span v-if="videoInfo.duration">{{ formatDuration(videoInfo.duration) }}</span>
              <span v-else>LIVE</span>
            </div>
          </div>
          
          <!-- Info & Actions Section -->
          <div class="info-content">
            <h2 class="video-title">
              {{ videoInfo.title }}
            </h2>
            
            <div class="action-buttons">
              <button @click="startDownload('video')" class="btn-action btn-video">
                <div class="btn-action-content">
                  <div class="action-icon-wrapper">
                    <Video class="action-icon" />
                  </div>
                  <span class="action-text">Best Quality Video</span>
                </div>
                <span class="format-badge">MP4</span>
              </button>
              
              <button @click="startDownload('audio')" class="btn-action btn-audio">
                <div class="btn-action-content">
                  <div class="action-icon-wrapper">
                    <Music class="action-icon" />
                  </div>
                  <span class="action-text">Extract Audio 192k</span>
                </div>
                <span class="format-badge">MP3</span>
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Progress Section -->
      <transition name="slide-up">
        <div v-if="isDownloading" class="progress-card">
          <div class="progress-header">
            <div class="status-container">
              <Loader2 v-if="progress < 100 && !downloadStatus.includes('완료') && !downloadStatus.includes('Completed')" class="status-icon spinner indigo-text" />
              <CheckCircle2 v-else class="status-icon success-text" />
              <span class="status-text">{{ downloadStatus }}</span>
            </div>
            <span class="progress-percentage">
              {{ progress.toFixed(1) }}<span class="percentage-symbol">%</span>
            </span>
          </div>
          
          <!-- Premium Animated Progress Bar -->
          <div class="progress-bar-container">
            <div 
              class="progress-bar-fill"
              :class="{ 'is-complete': progress >= 100 }"
            >
              <div class="progress-stripes"></div>
            </div>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { Youtube, Search, Video, Music, LinkIcon, Loader2, CheckCircle2 } from 'lucide-vue-next'

const url = ref('')
const videoInfo = ref(null)
const isLoading = ref(false)
const isDownloading = ref(false)
const progress = ref(0)
const downloadStatus = ref('')
const isInputFocused = ref(false)

// Dynamic style bindings
const progressWidth = computed(() => `${Math.max(progress.value, 3)}%`);

onMounted(() => {
  window.updateProgress = (p) => {
    progress.value = p
    downloadStatus.value = 'Downloading files...'
  }
  window.updateStatus = (status) => {
    downloadStatus.value = status
  }
  window.downloadComplete = (success, msg) => {
    progress.value = 100;
    downloadStatus.value = success ? 'Processing Completed!' : 'Error occurred';
    setTimeout(() => { 
      isDownloading.value = false; 
      progress.value = 0; 
      url.value = ''; 
      videoInfo.value = null; 
    }, 3000)
    if (!success) {
      setTimeout(() => alert(msg), 100);
    }
  }
})

const fetchInfo = async () => {
  if (!url.value) return
  isLoading.value = true
  try {
    let retries = 0;
    while (!window.pywebview && retries < 10) {
      await new Promise(r => setTimeout(r, 100));
      retries++;
    }

    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.get_info(url.value)
      if (res.success) {
        videoInfo.value = res
      } else {
        alert('Error: ' + res.error)
      }
    } else {
      setTimeout(() => {
        videoInfo.value = {
          success: true,
          title: "UI Design Preview Mode (No Backend Connected)",
          thumbnail: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop",
          duration: 365
        }
        isLoading.value = false
      }, 1000)
    }
  } catch (e) {
    alert('Please run the app via the pywebview backend environment.')
  } finally {
    isLoading.value = false
  }
}

const startDownload = async (type) => {
  isDownloading.value = true
  progress.value = 0
  downloadStatus.value = 'Connecting to server...'
  try {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.download(url.value, type)
      if (!res.success) {
        alert('Error: ' + res.error)
        isDownloading.value = false
      }
    } else {
      // Mock progress for UI testing
      let p = 0
      const interval = setInterval(() => {
        p += 2.5
        window.updateProgress(p)
        if (p >= 50) window.updateStatus("Extracting audio stream...")
        if (p >= 80) window.updateStatus("Converting to format...")
        if (p >= 100) {
          clearInterval(interval)
          window.downloadComplete(true, "Download Finished (Test Mode)")
        }
      }, 50)
    }
  } catch (e) {
    isDownloading.value = false
  }
}

const formatDuration = (seconds) => {
  if (!seconds) return '';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [
    h > 0 ? h : null,
    m > 9 ? m : (h > 0 ? '0' + m : m || '0'),
    s > 9 ? s : '0' + s
  ].filter(a => a !== null).join(':');
}
</script>

<style lang="scss" scoped>
// Variables
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

// Keyframes
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

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

// Base Layout
.app-container {
  min-height: 100vh;
  background-color: $bg-slate-950;
  color: $text-slate-100;
  font-family: Inter, system-ui, sans-serif;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  
  ::selection {
    background-color: rgba(99, 102, 241, 0.3);
    color: #c7d2fe;
  }
}

.ambient-glow {
  position: absolute;
  width: 50%;
  height: 50%;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(120px);
  
  &.glow-indigo {
    top: -20%;
    left: -10%;
    background-color: rgba(79, 70, 229, 0.2); // Indigo 600 / 20%
  }
  
  &.glow-violet {
    bottom: -20%;
    right: -10%;
    background-color: rgba(124, 58, 237, 0.2); // Violet 600 / 20%
  }
}

.main-wrapper {
  width: 100%;
  max-width: 48rem; // 3xl
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

// Header
.app-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.logo-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 1.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  backdrop-filter: $glass-blur;
  border: 1px solid $glass-border;
  box-shadow: 0 0 40px -10px rgba(99, 102, 241, 0.3);
  margin-bottom: 0.5rem;
  align-self: center;

  .logo-icon {
    width: 2.5rem;
    height: 2.5rem;
    color: #818cf8; // Indigo 400
  }
}

.app-title {
  font-size: 2.25rem;
  line-height: 2.5rem;
  font-weight: 900;
  letter-spacing: -0.025em;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  background-image: linear-gradient(to bottom right, #a5b4fc, #ffffff, #a78bfa);
  margin: 0;

  @media (min-width: 768px) {
    font-size: 3rem;
    line-height: 1;
  }
}

.app-subtitle {
  color: $text-slate-400;
  font-weight: 500;
  letter-spacing: 0.025em;
  margin: 0;
}

// Input Card
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

// Video Info Card
.video-info-card {
  background-color: rgba(15, 23, 42, 0.6); // Slate 900 / 60%
  backdrop-filter: $glass-blur;
  border-radius: 1.5rem;
  overflow: hidden;
  border: 1px solid $glass-border;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;

  @media (min-width: 768px) {
    flex-direction: row;
    align-items: stretch;
  }
}

.thumbnail-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;

  @media (min-width: 768px) {
    width: 41.666667%; // 5/12
    aspect-ratio: auto;
  }

  &:hover .thumbnail-img {
    transform: scale(105%);
  }

  .thumbnail-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 700ms ease;
  }

  .thumbnail-overlay {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(to top, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.5), transparent);

    @media (min-width: 768px) {
      background-image: linear-gradient(to right, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.5), transparent);
    }
  }

  .duration-badge {
    position: absolute;
    bottom: 1rem;
    left: 1rem;
    padding: 0.5rem;
    background-color: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    border-radius: 0.5rem;
    border: 1px solid $glass-border;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: monospace;
  }
}

.info-content {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.5rem;
  position: relative;
  z-index: 10;
  width: 100%;

  @media (min-width: 768px) {
    padding: 2rem;
    width: 58.333333%; // 7/12
  }

  .video-title {
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.375;
    color: $text-slate-100;
    margin: 0;
    
    // Line clamp 2
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;  
    overflow: hidden;

    @media (min-width: 768px) {
      font-size: 1.5rem;
    }
  }
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-action {
  width: 100%;
  position: relative;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid $glass-border;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  font-weight: 500;
  color: $text-slate-100;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all $transition-snappy;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &.btn-video {
    &:hover {
      border-color: rgba(99, 102, 241, 0.5);
      
      .action-icon-wrapper {
        background-color: $primary-hover;
        color: white;
      }
      .action-text {
        color: white;
      }
    }
    .action-icon-wrapper {
      background-color: rgba(99, 102, 241, 0.2);
      color: #818cf8;
    }
  }

  &.btn-audio {
    &:hover {
      border-color: rgba(139, 92, 246, 0.5);
      
      .action-icon-wrapper {
        background-color: $secondary-hover;
        color: white;
      }
      .action-text {
        color: white;
      }
    }
    .action-icon-wrapper {
      background-color: rgba(139, 92, 246, 0.2);
      color: #a78bfa;
    }
  }

  .btn-action-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .action-icon-wrapper {
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: all $transition-snappy;
  }

  .action-icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  .action-text {
    color: #e2e8f0; // Slate 200
    transition: color $transition-snappy;
  }

  .format-badge {
    font-size: 0.75rem;
    font-weight: 700;
    color: $text-slate-500;
    background-color: #1e293b; // Slate 800
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
  }
}

// Progress Card
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

// Transitions
.fade-slide-enter-active {
  transition: all 500ms ease-out;
}
.fade-slide-leave-active {
  transition: all 300ms ease-in;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(2rem) scale(0.95);
}
.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.slide-up-enter-active {
  transition: all 500ms ease-out;
}
.slide-up-leave-active {
  transition: all 300ms ease-in;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
.slide-up-enter-to,
.slide-up-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
