<template>
  <header class="app-header">
    <div class="logo-icon-wrapper">
      <Youtube class="logo-icon" />
    </div>
    <h1 class="app-title">PyVue-Tube</h1>
    <p class="app-subtitle">Premium YouTube Downloader</p>
  </header>
</template>

<script setup>
import { Youtube } from 'lucide-vue-next'
</script>

<style lang="scss" scoped>
$bg-slate-950: #020617;
$bg-slate-900: #0f172a;
$text-slate-100: #f1f5f9;
$text-slate-400: #94a3b8;
$text-slate-500: #64748b;

$glass-bg: rgba(255, 255, 255, 0.03);
$glass-border: rgba(255, 255, 255, 0.1);
$glass-blur: blur(12px);

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
</style>
