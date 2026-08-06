<template>
  <div class="video-info-card">
    
    <!-- Thumbnail Section -->
    <div class="thumbnail-wrapper" :class="{ 'is-playlist-card': videoInfo.is_playlist }">
      <img :src="videoInfo.thumbnail" class="thumbnail-img" alt="Thumbnail" />
      <div class="thumbnail-overlay"></div>
      
      <!-- Playlist Videos Counter Overlay -->
      <div v-if="videoInfo.is_playlist" class="playlist-overlay-badge">
        <ListVideo class="playlist-badge-icon" />
        <span class="count">{{ videoInfo.video_count }}</span>
        <span class="label">VIDEOS</span>
      </div>
      
      <div v-else class="duration-badge">
        <span v-if="videoInfo.duration">{{ formatDuration(videoInfo.duration) }}</span>
        <span v-else>LIVE</span>
      </div>
    </div>
    
    <!-- Info & Actions Section -->
    <div class="info-content">
      <!-- Playlist info -->
      <div v-if="videoInfo.is_playlist" class="playlist-info-header">
        <div class="playlist-label-tag">PLAYLIST</div>
        <h2 class="video-title" :title="videoInfo.title">
          {{ videoInfo.title }}
        </h2>
        <span class="playlist-count-text">{{ videoInfo.video_count }} videos to download</span>
      </div>
      
      <!-- Single Video info -->
      <h2 v-else class="video-title" :title="videoInfo.title">
        {{ videoInfo.title }}
      </h2>
      
      <!-- Action Buttons Section -->
      <div class="action-sections">
        <!-- Playlist download group -->
        <div v-if="videoInfo.is_playlist" class="action-group">
          <div class="action-buttons">
            <button @click="$emit('download', 'video', videoInfo.url, 'playlist')" class="btn-action btn-video">
              <div class="btn-action-content">
                <div class="action-icon-wrapper">
                  <Video class="action-icon" />
                </div>
                <span class="action-text">Download Entire Playlist</span>
              </div>
              <span class="format-badge">MP4</span>
            </button>
            
            <button @click="$emit('download', 'audio', videoInfo.url, 'playlist')" class="btn-action btn-audio">
              <div class="btn-action-content">
                <div class="action-icon-wrapper">
                  <Music class="action-icon" />
                </div>
                <span class="action-text">Extract All Audio (MP3)</span>
              </div>
              <span class="format-badge">MP3</span>
            </button>
          </div>
        </div>
        
        <!-- Single video download group (Original style) -->
        <div v-else class="action-buttons">
          <button @click="$emit('download', 'video', videoInfo.url, 'single')" class="btn-action btn-video">
            <div class="btn-action-content">
              <div class="action-icon-wrapper">
                <Video class="action-icon" />
              </div>
              <span class="action-text">Best Quality Video</span>
            </div>
            <span class="format-badge">MP4</span>
          </button>
          
          <button @click="$emit('download', 'audio', videoInfo.url, 'single')" class="btn-action btn-audio">
            <div class="btn-action-content">
              <div class="action-icon-wrapper">
                <Music class="action-icon" />
              </div>
              <span class="action-text">Extract Audio 192k</span>
            </div>
            <span class="format-badge">MP3</span>
          </button>
        </div>
        
        <!-- Watch + Playlist Dual mode (Option to download only this video) -->
        <div v-if="videoInfo.is_playlist && videoInfo.video_title" class="action-group single-video-shortcut">
          <div class="shortcut-divider">
            <span>OR DOWNLOAD CURRENT VIDEO ONLY</span>
          </div>
          
          <div class="shortcut-info">
            <Video class="shortcut-icon" />
            <div class="shortcut-text-container">
              <span class="shortcut-video-title">{{ videoInfo.video_title }}</span>
              <span class="shortcut-video-meta">Duration: {{ formatDuration(videoInfo.video_duration) }}</span>
            </div>
          </div>
          
          <div class="shortcut-buttons">
            <button @click="$emit('download', 'video', videoInfo.video_url, 'single')" class="btn-shortcut btn-video">
              <Video class="btn-icon" />
              <span>Video (MP4)</span>
            </button>
            <button @click="$emit('download', 'audio', videoInfo.video_url, 'single')" class="btn-shortcut btn-audio">
              <Music class="btn-icon" />
              <span>Audio (MP3)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Video, Music, ListVideo } from 'lucide-vue-next'

const props = defineProps({
  videoInfo: {
    type: Object,
    required: true
  }
})

defineEmits(['download'])

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
  
  .playlist-overlay-badge {
    position: absolute;
    top: 0;
    right: 0;
    width: 35%;
    height: 100%;
    background-color: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(8px);
    border-left: 1px solid $glass-border;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    z-index: 5;
    
    .playlist-badge-icon {
      width: 2rem;
      height: 2rem;
      color: #818cf8;
    }
    
    .count {
      font-size: 1.5rem;
      font-weight: 800;
      color: white;
      line-height: 1;
    }
    
    .label {
      font-size: 0.65rem;
      font-weight: 700;
      color: $text-slate-400;
      letter-spacing: 0.05em;
    }
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
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    box-orient: vertical;
    overflow: hidden;

    @media (min-width: 768px) {
      font-size: 1.5rem;
    }
  }
}

.playlist-info-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  .playlist-label-tag {
    align-self: flex-start;
    background-image: linear-gradient(to right, $primary-color, $secondary-color);
    color: white;
    font-size: 0.65rem;
    font-weight: 800;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
    letter-spacing: 0.05em;
  }
  
  .playlist-count-text {
    font-size: 0.875rem;
    color: $text-slate-400;
  }
}

.action-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

// Single video download option inside playlist card
.single-video-shortcut {
  background-color: rgba(255, 255, 255, 0.015);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  
  .shortcut-divider {
    display: flex;
    align-items: center;
    font-size: 0.65rem;
    font-weight: 800;
    color: #818cf8;
    letter-spacing: 0.05rem;
    
    &::after {
      content: '';
      flex: 1;
      height: 1px;
      background-color: rgba(255, 255, 255, 0.05);
      margin-left: 0.5rem;
    }
  }
  
  .shortcut-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    .shortcut-icon {
      width: 1rem;
      height: 1rem;
      color: $text-slate-400;
      flex-shrink: 0;
    }
    
    .shortcut-text-container {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1;
    }
    
    .shortcut-video-title {
      font-size: 0.8125rem;
      font-weight: 600;
      color: #cbd5e1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .shortcut-video-meta {
      font-size: 0.6875rem;
      color: $text-slate-500;
    }
  }
  
  .shortcut-buttons {
    display: flex;
    gap: 0.5rem;
    
    .btn-shortcut {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.375rem;
      background-color: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 0.5rem;
      border-radius: 0.5rem;
      color: #94a3b8;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 200ms ease;
      
      &:hover {
        background-color: rgba(255, 255, 255, 0.08);
        color: white;
      }
      
      &.btn-video:hover {
        border-color: rgba(99, 102, 241, 0.4);
        .btn-icon { color: #818cf8; }
      }
      
      &.btn-audio:hover {
        border-color: rgba(139, 92, 246, 0.4);
        .btn-icon { color: #a78bfa; }
      }
      
      .btn-icon {
        width: 0.875rem;
        height: 0.875rem;
        color: $text-slate-500;
        transition: color 200ms ease;
      }
    }
  }
}
</style>
