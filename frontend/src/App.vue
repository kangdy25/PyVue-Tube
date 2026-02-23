<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-hidden relative flex items-center justify-center p-4 selection:bg-indigo-500/30 selection:text-indigo-200">
    
    <!-- Background Ambient Glow -->
    <div class="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/20 blur-[120px] pointer-events-none"></div>

    <div class="w-full max-w-3xl relative z-10 flex flex-col gap-8">
      
      <!-- Header -->
      <header class="text-center space-y-3 mt-4">
        <div class="inline-flex items-center justify-center p-4 rounded-3xl bg-white/5 backdrop-blur-xl border border-white/10 shadow-[0_0_40px_-10px_rgba(99,102,241,0.3)] mb-2">
          <Youtube class="w-10 h-10 text-indigo-400" />
        </div>
        <h1 class="text-4xl md:text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-indigo-300 via-white to-violet-400">
          PyVue-Tube
        </h1>
        <p class="text-slate-400 font-medium tracking-wide">Premium YouTube Downloader</p>
      </header>

      <!-- Main Input Card -->
      <div class="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-3xl p-2 shadow-2xl transition-all duration-300 focus-within:bg-white/[0.05] focus-within:border-indigo-500/50 focus-within:shadow-[0_0_30px_-5px_rgba(99,102,241,0.2)] flex items-center gap-2 group">
        <div class="pl-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors">
          <LinkIcon class="w-5 h-5" />
        </div>
        <input 
          v-model="url" 
          type="text" 
          placeholder="Paste YouTube URL here..." 
          class="flex-1 bg-transparent border-none outline-none py-4 px-2 text-slate-100 placeholder-slate-600 text-lg"
          @keyup.enter="fetchInfo"
        />
        <button 
          @click="fetchInfo" 
          :disabled="isLoading"
          class="relative overflow-hidden group/btn bg-indigo-600 hover:bg-indigo-500 text-white p-4 rounded-2xl font-semibold shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[140px]"
        >
          <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:animate-[shimmer_1.5s_infinite]"></div>
          <span v-if="!isLoading" class="flex items-center gap-2">
            <Search class="w-5 h-5" />
            Analyze
          </span>
          <span v-else class="flex items-center gap-2">
            <Loader2 class="w-5 h-5 animate-spin" />
            Loading
          </span>
        </button>
      </div>

      <!-- Video Info & Actions (Animated Entrance) -->
      <transition 
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="opacity-0 translate-y-8 scale-95"
        enter-to-class="opacity-100 translate-y-0 scale-100"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="videoInfo" class="bg-slate-900/60 backdrop-blur-xl rounded-3xl overflow-hidden border border-white/10 shadow-2xl flex flex-col md:flex-row items-stretch">
          
          <!-- Thumbnail Section -->
          <div class="relative w-full md:w-5/12 aspect-video md:aspect-auto overflow-hidden group">
            <img :src="videoInfo.thumbnail" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" alt="Thumbnail" />
            <div class="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-slate-900/90 via-slate-900/50 to-transparent"></div>
            <div class="absolute bottom-4 left-4 p-2 bg-black/50 backdrop-blur-md rounded-lg border border-white/10 text-xs font-bold font-mono">
              <span v-if="videoInfo.duration">{{ formatDuration(videoInfo.duration) }}</span>
              <span v-else>LIVE</span>
            </div>
          </div>
          
          <!-- Info & Actions Section -->
          <div class="p-6 md:p-8 flex-1 flex flex-col justify-between space-y-6 relative z-10 w-full md:w-7/12">
            <h2 class="text-xl md:text-2xl font-bold leading-snug line-clamp-2 text-slate-100">
              {{ videoInfo.title }}
            </h2>
            
            <div class="flex flex-col gap-3">
              <button @click="startDownload('video')" class="w-full relative group overflow-hidden bg-white/5 hover:bg-white/10 border border-white/10 hover:border-indigo-500/50 px-5 py-4 rounded-xl font-medium transition-all flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                    <Video class="w-5 h-5" />
                  </div>
                  <span class="text-slate-200 group-hover:text-white transition-colors">Best Quality Video</span>
                </div>
                <span class="text-xs font-bold text-slate-500 bg-slate-800 px-2 py-1 rounded-md">MP4</span>
              </button>
              
              <button @click="startDownload('audio')" class="w-full relative group overflow-hidden bg-white/5 hover:bg-white/10 border border-white/10 hover:border-violet-500/50 px-5 py-4 rounded-xl font-medium transition-all flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="p-2 bg-violet-500/20 text-violet-400 rounded-lg group-hover:bg-violet-500 group-hover:text-white transition-colors">
                    <Music class="w-5 h-5" />
                  </div>
                  <span class="text-slate-200 group-hover:text-white transition-colors">Extract Audio 192k</span>
                </div>
                <span class="text-xs font-bold text-slate-500 bg-slate-800 px-2 py-1 rounded-md">MP3</span>
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- Progress Section -->
      <transition 
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="isDownloading" class="bg-slate-900/80 backdrop-blur-md p-6 rounded-3xl border border-white/10 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] flex flex-col gap-4">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
              <Loader2 v-if="progress < 100 && !downloadStatus.includes('완료')" class="w-5 h-5 animate-spin text-indigo-400" />
              <CheckCircle2 v-else class="w-5 h-5 text-emerald-400" />
              <span class="text-slate-300 font-medium tracking-wide">{{ downloadStatus }}</span>
            </div>
            <span class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">
              {{ progress.toFixed(1) }}<span class="text-lg">%</span>
            </span>
          </div>
          
          <!-- Premium Animated Progress Bar -->
          <div class="w-full bg-slate-950 rounded-full h-4 p-1 shadow-inner border border-white/5">
            <div 
              class="h-full rounded-full transition-all duration-300 ease-out relative overflow-hidden flex items-center"
              :class="progress >= 100 ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : 'bg-gradient-to-r from-indigo-500 to-violet-500'"
              :style="{ width: Math.max(progress, 3) + '%' }"
            >
              <div class="absolute inset-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.15)_50%,rgba(255,255,255,0.15)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem] animate-[stripes_1s_linear_infinite] opacity-50"></div>
            </div>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Youtube, Search, Video, Music, LinkIcon, Loader2, CheckCircle2 } from 'lucide-vue-next'

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

<style>
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
</style>
