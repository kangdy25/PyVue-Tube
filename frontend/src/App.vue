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
        :isLoading="isLoading || isDownloading"
        @submit="fetchInfo"
      />

      <!-- Video Info & Actions (Animated Entrance) -->
      <transition name="fade-slide">
        <VideoInfoCard
          v-if="videoInfo"
          :videoInfo="videoInfo"
          :isDownloading="isDownloading"
          @download="startDownload"
        />
      </transition>

      <!-- Progress Section -->
      <transition name="slide-up">
        <ProgressCard
          v-if="showProgress"
          :progress="progress"
          :downloadStatus="downloadStatus"
          :current="currentItem"
          :total="totalItems"
          :completed="completedItems"
          :failed="failedItems"
          :remaining="remainingItems"
          :isActive="isDownloading"
          :canRetry="canRetry"
          :cancelled="wasCancelled"
          @cancel="cancelDownload"
          @retry="retryDownload"
        />
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import AppHeader from './components/AppHeader.vue'
import UrlInputCard from './components/UrlInputCard.vue'
import VideoInfoCard from './components/VideoInfoCard.vue'
import ProgressCard from './components/ProgressCard.vue'

const url = ref('')
const videoInfo = ref(null)
const isLoading = ref(false)
const isDownloading = ref(false)
const showProgress = ref(false)
const progress = ref(0)
const downloadStatus = ref('')
const currentItem = ref(null)
const totalItems = ref(null)
const completedItems = ref(0)
const failedItems = ref(0)
const remainingItems = ref(0)
const currentJobId = ref(null)
const canRetry = ref(false)
const wasCancelled = ref(false)

let mockInterval = null
let mockContext = null

const resetProgress = () => {
  showProgress.value = true
  isDownloading.value = true
  progress.value = 0
  downloadStatus.value = '다운로드 준비 중...'
  currentItem.value = null
  totalItems.value = null
  completedItems.value = 0
  failedItems.value = 0
  remainingItems.value = 0
  canRetry.value = false
  wasCancelled.value = false
  currentJobId.value = null
}

onMounted(() => {
  window.updateProgress = (update) => {
    if (update.job_id && currentJobId.value && update.job_id !== currentJobId.value) return
    if (update.job_id && !currentJobId.value) currentJobId.value = update.job_id
    progress.value = update.percent
    downloadStatus.value = update.status || '다운로드 중...'
    currentItem.value = update.current ?? null
    totalItems.value = update.total ?? null
    completedItems.value = update.completed ?? 0
    failedItems.value = update.failed ?? 0
  }
  window.updateStatus = (update) => {
    downloadStatus.value = update.status || update
  }
  window.downloadComplete = (result) => {
    if (result.job_id && currentJobId.value && result.job_id !== currentJobId.value) return
    if (result.job_id) currentJobId.value = result.job_id
    progress.value = result.cancelled ? (result.progress ?? progress.value) : 100
    downloadStatus.value = result.message
    totalItems.value = result.total || totalItems.value
    completedItems.value = result.completed || 0
    failedItems.value = result.failed || 0
    remainingItems.value = result.remaining || 0
    canRetry.value = Boolean(result.can_retry)
    wasCancelled.value = Boolean(result.cancelled)
    isDownloading.value = false
    showProgress.value = true
  }
})

onBeforeUnmount(() => {
  if (mockInterval) clearInterval(mockInterval)
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
        if (url.value.includes('list=')) {
          videoInfo.value = {
            success: true,
            is_playlist: true,
            title: "Mock Playlist: Vue.js & Python Integration Tutorial",
            thumbnail: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop",
            video_count: 5,
            url: url.value,
            entries: [
              { index: 1, id: 'mock-1', title: '프로젝트 소개와 개발 환경 준비', duration: 365, is_available: true },
              { index: 2, id: 'mock-2', title: 'Vue 3 인터페이스 구성', duration: 428, is_available: true },
              { index: 3, id: 'mock-3', title: 'pywebview 브리지 연결', duration: 512, is_available: true },
              { index: 4, id: 'mock-4', title: 'yt-dlp 다운로드 구현', duration: 476, is_available: true },
              { index: 5, id: 'mock-5', title: 'PyInstaller 앱 패키징', duration: 391, is_available: true }
            ],
            video_title: "Mock Video: 1. Setup pywebview and Vite",
            video_thumbnail: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop",
            video_duration: 365,
            video_url: url.value.split('&list=')[0]
          }
        } else {
          videoInfo.value = {
            success: true,
            title: "UI Design Preview Mode (No Backend Connected)",
            thumbnail: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1000&auto=format&fit=crop",
            duration: 365
          }
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

const startDownload = async (type, targetUrl, scope = 'single', playlistItems = null) => {
  if (isDownloading.value) return
  resetProgress()
  const downloadUrl = targetUrl || url.value
  try {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.download(downloadUrl, type, scope, playlistItems)
      if (!res.success) {
        alert('Error: ' + res.error)
        isDownloading.value = false
        showProgress.value = false
      } else {
        currentJobId.value = res.job_id
      }
    } else {
      const selectedItems = scope === 'playlist'
        ? (playlistItems?.length ? playlistItems : videoInfo.value.entries.map(entry => entry.index))
        : [1]
      mockContext = { type, targetUrl: downloadUrl, scope, playlistItems: selectedItems }
      currentJobId.value = `mock-${Date.now()}`
      totalItems.value = selectedItems.length
      let p = 0
      mockInterval = setInterval(() => {
        p += 2.5
        const currentVideo = Math.min(Math.ceil((p / 100) * selectedItems.length), selectedItems.length)
        const isPlaylist = scope === 'playlist'
        window.updateProgress({
          job_id: currentJobId.value,
          percent: p,
          status: isPlaylist
            ? `다운로드 중 (${currentVideo}/${selectedItems.length}): 선택한 영상 ${selectedItems[currentVideo - 1]}`
            : '다운로드 중: 현재 영상',
          current: isPlaylist ? currentVideo : null,
          total: selectedItems.length,
          completed: Math.max(0, currentVideo - 1),
          failed: 0
        })
        if (p >= 100) {
          clearInterval(mockInterval)
          mockInterval = null
          window.downloadComplete({
            job_id: currentJobId.value,
            success: true,
            cancelled: false,
            can_retry: false,
            completed: selectedItems.length,
            failed: 0,
            total: selectedItems.length,
            progress: 100,
            message: '다운로드 완료! (테스트 모드)'
          })
        }
      }, 50)
    }
  } catch (e) {
    isDownloading.value = false
  }
}

const cancelDownload = async () => {
  if (!isDownloading.value || !currentJobId.value) return
  downloadStatus.value = '취소 요청 중...'

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.cancel_download(currentJobId.value)
    if (!res.success) downloadStatus.value = res.error
    return
  }

  if (mockInterval) {
    clearInterval(mockInterval)
    mockInterval = null
  }
  const total = totalItems.value || 1
  const remaining = Math.max(0, total - completedItems.value)
  window.downloadComplete({
    job_id: currentJobId.value,
    success: false,
    cancelled: true,
    can_retry: remaining > 0,
    completed: completedItems.value,
    failed: 0,
    remaining,
    total,
    progress: progress.value,
    message: '다운로드가 취소되었습니다.'
  })
}

const retryDownload = async () => {
  if (!canRetry.value || !currentJobId.value) return

  if (window.pywebview && window.pywebview.api) {
    const previousJobId = currentJobId.value
    resetProgress()
    const res = await window.pywebview.api.retry_download(previousJobId)
    if (!res.success) {
      isDownloading.value = false
      downloadStatus.value = res.error
      return
    }
    currentJobId.value = res.job_id
    return
  }

  const remaining = mockContext?.playlistItems?.slice(completedItems.value) || [1]
  await startDownload(
    mockContext?.type || 'video',
    mockContext?.targetUrl || url.value,
    mockContext?.scope || 'single',
    remaining
  )
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
  overflow-x: hidden;
  overflow-y: auto;
  position: relative;
  display: flex;
  align-items: flex-start;
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
  margin: auto 0;
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
