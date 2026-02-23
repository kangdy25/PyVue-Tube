<template>
  <div class="video-info-card">
    
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
        <button @click="$emit('download', 'video')" class="btn-action btn-video">
          <div class="btn-action-content">
            <div class="action-icon-wrapper">
              <Video class="action-icon" />
            </div>
            <span class="action-text">Best Quality Video</span>
          </div>
          <span class="format-badge">MP4</span>
        </button>
        
        <button @click="$emit('download', 'audio')" class="btn-action btn-audio">
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
</template>

<script setup>
import { Video, Music } from 'lucide-vue-next'

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
</style>
