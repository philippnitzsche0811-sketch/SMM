<template>
  <div class="mode-selector">
    <div class="mode-header">
      <h2>New Upload</h2>
      <p>Choose how you want to upload your video</p>
    </div>

    <div class="mode-cards">
      <button class="mode-card" @click="$emit('select', 'simple')">
        <div class="mode-icon mode-icon--simple">
          <i class="pi pi-upload"></i>
        </div>
        <div class="mode-body">
          <h3>Simple Upload</h3>
          <p>Add a video, let AI optimize your title, description and tags, then publish immediately or schedule it.</p>
          <ul class="mode-features">
            <li><i class="pi pi-check"></i> AI title &amp; tag optimization</li>
            <li><i class="pi pi-check"></i> Publish now or schedule</li>
            <li><i class="pi pi-check"></i> Add to an Upload Group</li>
          </ul>
        </div>
        <div class="mode-arrow"><i class="pi pi-arrow-right"></i></div>
      </button>

      <button class="mode-card" @click="$emit('select', 'smart')">
        <div class="mode-icon mode-icon--smart">
          <i class="pi pi-eye"></i>
        </div>
        <div class="mode-body">
          <h3>Smart Upload</h3>
          <p>Claude Vision analyzes your video frames and gives you actionable feedback on pacing, cuts, and sound before you publish.</p>
          <ul class="mode-features">
            <li><i class="pi pi-check"></i> AI video frame analysis</li>
            <li><i class="pi pi-check"></i> Pacing &amp; cut feedback</li>
            <li><i class="pi pi-check"></i> Sound recommendations</li>
          </ul>
        </div>
        <div class="mode-arrow"><i class="pi pi-arrow-right"></i></div>
      </button>

      <button class="mode-card mode-card--group" @click="$emit('select', 'groups')">
        <div class="mode-icon mode-icon--group">
          <i class="pi pi-calendar"></i>
        </div>
        <div class="mode-body">
          <h3>Upload Groups</h3>
          <p>Collect videos in a named queue. The scheduler automatically uploads them at the best times — the fuller the queue, the more flexible the timing.</p>
          <ul class="mode-features">
            <li><i class="pi pi-check"></i> Queue multiple videos</li>
            <li><i class="pi pi-check"></i> Density-based scheduling</li>
            <li><i class="pi pi-check"></i> Auto-upload at peak times</li>
          </ul>
        </div>
        <div class="mode-arrow"><i class="pi pi-arrow-right"></i></div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ select: [mode: 'simple' | 'smart' | 'groups'] }>();
</script>

<style scoped>
.mode-selector { max-width: 860px; margin: 0 auto; }

.mode-header {
  margin-bottom: 2rem;
}
.mode-header h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}
.mode-header p { color: var(--text-secondary); font-size: 0.9rem; margin: 0; }

.mode-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mode-card {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.5rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
  position: relative;
  overflow: hidden;
}
.mode-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(79,127,255,0.4), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.mode-card:hover {
  border-color: rgba(79,127,255,0.35);
  background: rgba(79,127,255,0.04);
  transform: translateY(-2px);
}
.mode-card:hover::before { opacity: 1; }

.mode-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.375rem;
  flex-shrink: 0;
}
.mode-icon--simple  { background: rgba(79,127,255,0.15);  color: #7da5ff; border: 1px solid rgba(79,127,255,0.25); }
.mode-icon--smart   { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.25); }
.mode-icon--group   { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.25); }

.mode-body { flex: 1; min-width: 0; }
.mode-body h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.375rem;
}
.mode-body > p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 0.75rem;
}

.mode-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1rem;
}
.mode-features li {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.mode-features li i { color: #4f7fff; font-size: 0.7rem; }

.mode-arrow {
  color: var(--text-disabled);
  font-size: 0.9rem;
  flex-shrink: 0;
  margin-top: 0.2rem;
  transition: color 0.2s, transform 0.2s;
}
.mode-card:hover .mode-arrow { color: #4f7fff; transform: translateX(3px); }

@media (max-width: 640px) {
  .mode-card { padding: 1.125rem; gap: 1rem; }
  .mode-icon { width: 42px; height: 42px; font-size: 1.125rem; }
}
</style>
