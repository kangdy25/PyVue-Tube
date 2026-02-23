<template>
  <div class="app-container">
    
    <!-- Background Ambient Glow -->
    <div class="ambient-glow glow-indigo"></div>
    <div class="ambient-glow glow-violet"></div>

    <div class="main-wrapper">
      
      <!-- Header -->
      <AppHeader />

      <!-- Main Input Card -->
      <UrlInputCard
        v-model="url"
        :isLoading="isLoading"
        @submit="fetchInfo"
      />

      <!-- Video Info & Actions (Animated Entrance) -->
      <transition name="fade-slide">
        <VideoInfoCard
          v-if="videoInfo"
          :videoInfo="videoInfo"
          @download="startDownload"
        />
      </transition>

      <!-- Progress Section -->
      <transition name="slide-up">
        <ProgressCard
          v-if="isDownloading"
          :progress="progress"
          :downloadStatus="downloadStatus"
        />
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import UrlInputCard from './components/UrlInputCard.vue'
import VideoInfoCard from './components/VideoInfoCard.vue'
import ProgressCard from './components/ProgressCard.vue'

const url = ref('')
const videoInfo = ref(null)
const isLoading = ref(false)
const isDownloading = ref(false)
const progress = ref(0)
const downloadStatus = ref('')

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
</script>

<style lang="scss" scoped>
$bg-slate-950: #020617;
$text-slate-100: #f1f5f9;

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
