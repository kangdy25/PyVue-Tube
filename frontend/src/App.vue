<template>
  <div class="min-h-screen bg-gray-900 text-white p-8 font-sans selection:bg-purple-500 selection:text-white">
    <div class="max-w-2xl mx-auto space-y-8">
      
      <!-- 헤더 -->
      <header class="text-center pt-8">
        <h1 class="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 drop-shadow-lg">
          PyVue-Tube
        </h1>
        <p class="mt-2 text-gray-400 font-medium">유튜브 최고 화질 영상 & MP3 추출기</p>
      </header>

      <!-- URL 입력부 -->
      <div class="flex gap-3 backdrop-blur-md bg-white/5 p-2 rounded-2xl border border-white/10 shadow-2xl transition focus-within:border-purple-500/50">
        <input 
          v-model="url" 
          type="text" 
          placeholder="유튜브 URL을 붙여넣으세요..." 
          class="flex-1 bg-transparent border-none outline-none px-4 text-gray-100 placeholder-gray-500"
          @keyup.enter="fetchInfo"
        />
        <button 
          @click="fetchInfo" 
          :disabled="isLoading"
          class="bg-purple-600 hover:bg-purple-500 px-6 py-3 rounded-xl font-semibold shadow-lg shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isLoading ? '검색 중...' : '정보 가져오기' }}
        </button>
      </div>

      <!-- 영상 정보 및 다운로드 옵션 -->
      <transition name="fade">
        <div v-if="videoInfo" class="bg-gray-800/80 rounded-2xl overflow-hidden border border-gray-700 shadow-xl backdrop-blur-sm">
          <img :src="videoInfo.thumbnail" class="w-full h-64 object-cover" alt="썸네일" />
          <div class="p-6 space-y-6">
            <h2 class="text-xl font-bold line-clamp-2">{{ videoInfo.title }}</h2>
            
            <div class="flex gap-4">
              <button @click="startDownload('video')" class="flex-1 bg-blue-600 hover:bg-blue-500 px-4 py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                최고화질 영상 (MP4)
              </button>
              <button @click="startDownload('audio')" class="flex-1 bg-pink-600 hover:bg-pink-500 px-4 py-3 rounded-xl font-medium transition-colors flex items-center justify-center gap-2 shadow-lg shadow-pink-500/20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path></svg>
                음원 추출 (MP3)
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- 다운로드 진행률 프로그레스바 -->
      <transition name="fade">
        <div v-if="isDownloading" class="bg-gray-800/80 p-6 rounded-2xl border border-gray-700 space-y-3 backdrop-blur-sm">
          <div class="flex justify-between items-end">
            <span class="text-sm text-gray-300 font-medium">{{ downloadStatus }}</span>
            <span class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">{{ progress.toFixed(1) }}%</span>
          </div>
          <div class="w-full bg-gray-900 rounded-full h-3 overflow-hidden shadow-inner border border-gray-800">
            <div 
              class="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-300 ease-out relative"
              :style="{ width: progress + '%' }"
            >
              <div class="absolute top-0 right-0 bottom-0 left-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const url = ref('')
const videoInfo = ref(null)
const isLoading = ref(false)
const isDownloading = ref(false)
const progress = ref(0)
const downloadStatus = ref('')

onMounted(() => {
  window.updateProgress = (p) => {
    progress.value = p
    downloadStatus.value = '다운로드 중...'
  }
  window.updateStatus = (status) => {
    downloadStatus.value = status
  }
  window.downloadComplete = (success, msg) => {
    setTimeout(() => { isDownloading.value = false; progress.value = 0; url.value = ''; videoInfo.value = null; }, 2000)
    alert(success ? msg : msg)
    if(success) downloadStatus.value = '다운로드 완료!'
  }
})

const fetchInfo = async () => {
  if (!url.value) return
  isLoading.value = true
  try {
    // pywebview API가 주입될 때까지 약간 대기하는 로직 추가
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
        alert('오류: ' + res.error)
      }
    } else {
      setTimeout(() => {
        videoInfo.value = {
          success: true,
          title: "테스트 비디오",
          thumbnail: "https://via.placeholder.com/640x360"
        }
        isLoading.value = false
      }, 1000)
    }
  } catch (e) {
    alert('앱을 pywebview 환경(main.py)에서 실행해주세요.')
  } finally {
    isLoading.value = false
  }
}

const startDownload = async (type) => {
  isDownloading.value = true
  progress.value = 0
  downloadStatus.value = '연결 중...'
  try {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.download(url.value, type)
      if (!res.success) {
        alert('오류: ' + res.error)
        isDownloading.value = false
      }
    } else {
      // Mock progress
      let p = 0
      const interval = setInterval(() => {
        p += 5
        window.updateProgress(p)
        if (p >= 100) {
          clearInterval(interval)
          window.downloadComplete(true, "다운로드 완료 (테스트)")
        }
      }, 100)
    }
  } catch (e) {
    isDownloading.value = false
  }
}
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(15px); }
</style>
