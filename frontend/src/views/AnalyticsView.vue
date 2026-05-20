<template>
  <div class="analytics-page">
    <div class="page-header">
      <h1 class="page-title">Performance Analytics</h1>
      <p class="page-subtitle">Views, likes and comments for your uploaded videos</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;color:var(--color-primary)"></i>
      <p>Loading videos…</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="!videos.length" class="empty-state">
      <i class="pi pi-chart-bar" style="font-size:3rem;color:#94a3b8"></i>
      <h3>No uploaded videos yet</h3>
      <p>Upload a video to see performance data here.</p>
      <router-link to="/upload" class="btn-primary">Upload a video</router-link>
    </div>

    <!-- Video list -->
    <div v-else class="video-list">
      <div
        v-for="video in videos"
        :key="video.id"
        class="video-card"
        :class="{ 'video-card--active': selectedVideoId === video.id }"
      >
        <div class="video-card-header">
          <div class="video-info">
            <h3 class="video-title">{{ video.title }}</h3>
            <span class="video-date">{{ formatDate(video.created_at) }}</span>
          </div>
          <div class="video-actions">
            <button
              class="btn-icon"
              title="Stats aktualisieren"
              :disabled="refreshingId === video.id"
              @click="refreshStats(video.id)"
            >
              <i class="pi" :class="refreshingId === video.id ? 'pi-spin pi-spinner' : 'pi-refresh'"></i>
            </button>
            <button
              class="btn-icon btn-icon--comment"
              title="Kommentare anzeigen"
              :class="{ active: selectedVideoId === video.id }"
              @click="toggleComments(video)"
            >
              <i class="pi pi-comments"></i>
            </button>
          </div>
        </div>

        <!-- Platform stats grid -->
        <div class="platform-stats">
          <div
            v-for="platform in video.platforms"
            :key="platform"
            class="platform-stat-row"
          >
            <div class="platform-label">
              <img :src="platformIcon(platform)" :alt="platform" class="platform-icon" />
              <span>{{ capitalize(platform) }}</span>
            </div>
            <template v-if="video.stats[platform]">
              <div class="stat-item">
                <i class="pi pi-eye"></i>
                <span>{{ fmt(video.stats[platform].view_count) }}</span>
              </div>
              <div class="stat-item">
                <i class="pi pi-heart"></i>
                <span>{{ fmt(video.stats[platform].like_count) }}</span>
              </div>
              <div class="stat-item">
                <i class="pi pi-comments"></i>
                <span>{{ fmt(video.stats[platform].comment_count) }}</span>
              </div>
              <div class="stat-item">
                <i class="pi pi-share-alt"></i>
                <span>{{ fmt(video.stats[platform].share_count) }}</span>
              </div>
              <span class="stat-freshness" :title="'Aktualisiert: ' + (video.stats[platform].fetched_at || '–')">
                {{ freshness(video.stats[platform].fetched_at) }}
              </span>
            </template>
            <template v-else>
              <span class="no-stats">
                No data yet —
                <button class="link-btn" @click="refreshStats(video.id)">load now</button>
              </span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Creator Loop CTA -->
    <div v-if="!loading && videos.length > 0" class="loop-cta">
      <div class="loop-cta-content">
        <i class="pi pi-lightbulb loop-cta-icon"></i>
        <div>
          <p class="loop-cta-title">Ready for the next round?</p>
          <p class="loop-cta-sub">Use your performance data to spark your next idea</p>
        </div>
      </div>
      <router-link to="/plan" class="loop-cta-btn">
        Create New Idea <i class="pi pi-arrow-right"></i>
      </router-link>
    </div>

    <!-- Comments panel (slides in below selected video) -->
    <Transition name="slide-down">
      <div v-if="selectedVideoId" class="comments-panel">
        <div class="comments-header">
          <h2>Comments — {{ selectedVideo?.title }}</h2>
          <div class="comment-filters">
            <button
              v-for="f in filters"
              :key="f.value"
              class="filter-btn"
              :class="{ active: activeFilter === f.value }"
              @click="loadComments(f.value)"
            >
              {{ f.label }}
            </button>
          </div>
          <button class="btn-close" @click="selectedVideoId = null">
            <i class="pi pi-times"></i>
          </button>
        </div>

        <div v-if="commentsLoading" class="comments-loading">
          <i class="pi pi-spin pi-spinner"></i>
          <span>Loading comments…</span>
        </div>

        <div v-else-if="comments.length === 0" class="comments-empty">
          <i class="pi pi-comment"></i>
          <span v-if="mockComments">Comments are not available in mock mode.</span>
          <span v-else>No comments found for this filter.</span>
        </div>

        <div v-else class="comment-list">
          <div v-for="comment in comments" :key="comment.id || comment.timestamp" class="comment-item">
            <div class="comment-meta">
              <span class="comment-user">@{{ comment.username }}</span>
              <span class="comment-time">{{ formatDate(comment.timestamp) }}</span>
              <span v-if="comment.like_count" class="comment-likes">
                <i class="pi pi-heart-fill"></i> {{ comment.like_count }}
              </span>
            </div>
            <p class="comment-text">{{ comment.text }}</p>
            <span v-if="isQuestion(comment.text)" class="comment-tag comment-tag--question">Frage</span>
            <span v-else-if="isIdea(comment.text)" class="comment-tag comment-tag--idea">Idee</span>

            <!-- Reply -->
            <div v-if="comment.id" class="comment-reply-section">
              <button
                v-if="!replyingTo || replyingTo !== comment.id"
                class="btn-reply"
                @click="replyingTo = comment.id; replyTexts[comment.id] = replyTexts[comment.id] || ''"
              >
                <i class="pi pi-reply"></i> Antworten
              </button>

              <div v-if="replyingTo === comment.id" class="reply-form">
                <textarea
                  v-model="replyTexts[comment.id]"
                  class="reply-textarea"
                  placeholder="Deine Antwort…"
                  rows="2"
                  :disabled="replyLoading[comment.id]"
                />
                <div class="reply-actions">
                  <button class="btn-reply-cancel" @click="replyingTo = null">Abbrechen</button>
                  <button
                    class="btn-reply-send"
                    :disabled="!replyTexts[comment.id]?.trim() || replyLoading[comment.id]"
                    @click="sendReply(comment)"
                  >
                    <i v-if="replyLoading[comment.id]" class="pi pi-spin pi-spinner"></i>
                    <span v-else>Senden</span>
                  </button>
                </div>
                <p v-if="replySuccess[comment.id]" class="reply-success">
                  <i class="pi pi-check"></i> Antwort gesendet
                </p>
                <p v-if="replyError[comment.id]" class="reply-error">{{ replyError[comment.id] }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import {
  getAnalyticsVideos,
  refreshVideoStats,
  getVideoComments,
  postCommentReply,
  type AnalyticsVideo,
  type AnalyticsComment,
} from '@/services/api';

const authStore = useAuthStore();

const loading = ref(true);
const videos = ref<AnalyticsVideo[]>([]);
const refreshingId = ref<string | null>(null);
const selectedVideoId = ref<string | null>(null);
const activeFilter = ref('all');
const comments = ref<AnalyticsComment[]>([]);
const commentsLoading = ref(false);
const mockComments = ref(false);
const replyingTo = ref<string | null>(null);
const replyTexts = ref<Record<string, string>>({});
const replyLoading = ref<Record<string, boolean>>({});
const replySuccess = ref<Record<string, boolean>>({});
const replyError = ref<Record<string, string>>({});

const filters = [
  { label: 'All',       value: 'all' },
  { label: 'Questions', value: 'questions' },
  { label: 'Ideas',     value: 'ideas' },
];

const IDEA_KEYWORDS = ['solltest', 'könntest', 'wäre cool', 'idea', 'idee', 'würde', 'vorschlag', 'suggestion'];

const selectedVideo = computed(() => videos.value.find(v => v.id === selectedVideoId.value));

onMounted(async () => {
  await loadVideos();
});

async function loadVideos() {
  loading.value = true;
  try {
    const userId = authStore.userId;
    if (!userId) return;
    const data = await getAnalyticsVideos(userId);
    videos.value = data.videos;
  } catch (e) {
    console.error('Analytics load failed:', e);
  } finally {
    loading.value = false;
  }
}

async function refreshStats(videoId: string) {
  refreshingId.value = videoId;
  try {
    await refreshVideoStats(videoId);
    await loadVideos();
  } catch (e) {
    console.error('Refresh failed:', e);
  } finally {
    refreshingId.value = null;
  }
}

async function toggleComments(video: AnalyticsVideo) {
  if (selectedVideoId.value === video.id) {
    selectedVideoId.value = null;
    return;
  }
  selectedVideoId.value = video.id;
  activeFilter.value = 'all';
  await loadComments('all');
}

async function loadComments(filter: string) {
  if (!selectedVideoId.value) return;
  activeFilter.value = filter;
  commentsLoading.value = true;
  mockComments.value = false;
  try {
    const result = await getVideoComments(selectedVideoId.value, 'instagram', filter);
    comments.value = result.comments;
    mockComments.value = result.mock === true;
  } catch (e) {
    comments.value = [];
  } finally {
    commentsLoading.value = false;
  }
}

async function sendReply(comment: AnalyticsComment) {
  const id = comment.id;
  if (!id || !replyTexts.value[id]?.trim() || !selectedVideoId.value) return;
  replyLoading.value[id] = true;
  replyError.value[id] = '';
  try {
    await postCommentReply(selectedVideoId.value, id, replyTexts.value[id]);
    replySuccess.value[id] = true;
    replyTexts.value[id] = '';
    setTimeout(() => {
      replySuccess.value[id] = false;
      replyingTo.value = null;
    }, 2500);
  } catch {
    replyError.value[id] = 'Antwort fehlgeschlagen. Bitte erneut versuchen.';
  } finally {
    replyLoading.value[id] = false;
  }
}

function isQuestion(text: string) {
  return text.includes('?');
}

function isIdea(text: string) {
  const lower = text.toLowerCase();
  return IDEA_KEYWORDS.some(k => lower.includes(k));
}

function fmt(n: number): string {
  if (!n) return '0';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'k';
  return String(n);
}

function formatDate(iso: string | null): string {
  if (!iso) return '–';
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: 'short', year: 'numeric' });
}

function freshness(iso: string | null): string {
  if (!iso) return '';
  const diff = (Date.now() - new Date(iso).getTime()) / 1000 / 60;
  if (diff < 60) return `vor ${Math.round(diff)} Min.`;
  if (diff < 1440) return `vor ${Math.round(diff / 60)} Std.`;
  return `vor ${Math.round(diff / 1440)} Tagen`;
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function platformIcon(platform: string): string {
  const icons: Record<string, string> = {
    youtube: 'https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg',
    tiktok: 'https://upload.wikimedia.org/wikipedia/en/thumb/a/a9/TikTok_logo.svg/1200px-TikTok_logo.svg.png',
    instagram: 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg',
  };
  return icons[platform] || '';
}
</script>

<style scoped>
.analytics-page {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary, #f1f5f9);
  margin: 0 0 0.25rem;
}

.page-subtitle {
  color: var(--text-secondary, #94a3b8);
  margin: 0;
}

/* Loading / Empty */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
  text-align: center;
  color: var(--text-secondary, #94a3b8);
}

.empty-state h3 { color: var(--text-primary, #f1f5f9); margin: 0; }
.empty-state p  { margin: 0; }

.btn-primary {
  display: inline-block;
  padding: 0.6rem 1.5rem;
  background: var(--color-primary, #667eea);
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Video list */
.video-list { display: flex; flex-direction: column; gap: 1rem; }

.video-card {
  background: var(--bg-card, rgba(30,41,59,0.8));
  border: 1px solid var(--border-color, rgba(255,255,255,0.08));
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  transition: border-color 0.2s;
}

.video-card--active {
  border-color: var(--color-primary, #667eea);
}

.video-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.video-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
  margin: 0 0 0.2rem;
  word-break: break-word;
}

.video-date {
  font-size: 0.8rem;
  color: var(--text-secondary, #94a3b8);
}

.video-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }

.btn-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border-color, rgba(255,255,255,0.1));
  background: transparent;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover,
.btn-icon.active {
  background: var(--color-primary, #667eea);
  color: #fff;
  border-color: transparent;
}

.btn-icon:disabled { opacity: 0.5; cursor: not-allowed; }

/* Platform stats */
.platform-stats { display: flex; flex-direction: column; gap: 0.6rem; }

.platform-stat-row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.platform-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 110px;
  font-size: 0.85rem;
  color: var(--text-secondary, #94a3b8);
}

.platform-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.9rem;
  color: var(--text-primary, #f1f5f9);
}

.stat-item .pi {
  font-size: 0.8rem;
  color: var(--text-secondary, #94a3b8);
}

.stat-freshness {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
}

.no-stats {
  font-size: 0.85rem;
  color: var(--text-secondary, #94a3b8);
}

.link-btn {
  background: none;
  border: none;
  color: var(--color-primary, #667eea);
  cursor: pointer;
  padding: 0;
  font-size: inherit;
  text-decoration: underline;
}

/* Comments panel */
.comments-panel {
  margin-top: 1.5rem;
  background: var(--bg-card, rgba(30,41,59,0.8));
  border: 1px solid var(--color-primary, #667eea);
  border-radius: 12px;
  padding: 1.5rem;
}

.comments-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.comments-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
  flex: 1;
  min-width: 200px;
}

.comment-filters { display: flex; gap: 0.4rem; }

.filter-btn {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  border: 1px solid var(--border-color, rgba(255,255,255,0.15));
  background: transparent;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active,
.filter-btn:hover {
  background: var(--color-primary, #667eea);
  color: #fff;
  border-color: transparent;
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
}

.comments-loading,
.comments-empty {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
  color: var(--text-secondary, #94a3b8);
  font-size: 0.9rem;
}

.comment-list { display: flex; flex-direction: column; gap: 0.75rem; }

.comment-item {
  padding: 0.85rem 1rem;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.06);
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.4rem;
  flex-wrap: wrap;
}

.comment-user {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-primary, #667eea);
}

.comment-time,
.comment-likes {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
}

.comment-text {
  font-size: 0.9rem;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
  line-height: 1.6;
}

.comment-tag {
  display: inline-block;
  margin-top: 0.4rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
}

.comment-tag--question {
  background: rgba(251,191,36,0.15);
  color: #fbbf24;
}

.comment-tag--idea {
  background: rgba(102,126,234,0.15);
  color: #667eea;
}

/* Transition */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* Reply UI */
.comment-reply-section {
  margin-top: 0.6rem;
}

.btn-reply {
  background: none;
  border: none;
  color: var(--color-primary, #667eea);
  cursor: pointer;
  font-size: 0.78rem;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  opacity: 0.8;
  transition: opacity 0.15s;
}

.btn-reply:hover { opacity: 1; }

.reply-form {
  margin-top: 0.5rem;
  padding-left: 0.75rem;
  border-left: 2px solid var(--color-primary, #667eea);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.reply-textarea {
  width: 100%;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: var(--text-primary, #f1f5f9);
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  resize: none;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}

.reply-textarea:focus {
  border-color: var(--color-primary, #667eea);
}

.reply-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-reply-cancel {
  background: none;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 6px;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0.3rem 0.75rem;
  transition: background 0.15s;
}

.btn-reply-cancel:hover { background: rgba(255,255,255,0.06); }

.btn-reply-send {
  background: var(--color-primary, #667eea);
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.3rem 0.9rem;
  transition: opacity 0.15s;
  min-width: 60px;
}

.btn-reply-send:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-reply-send:not(:disabled):hover { opacity: 0.85; }

.reply-success {
  font-size: 0.8rem;
  color: #4ade80;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.reply-error {
  font-size: 0.8rem;
  color: #f87171;
  margin: 0;
}

/* Loop CTA */
.loop-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1.25rem 1.5rem;
  background: rgba(124,58,237,0.07);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 12px;
  flex-wrap: wrap;
}

.loop-cta-content {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.loop-cta-icon {
  font-size: 1.5rem;
  color: #a78bfa;
  flex-shrink: 0;
}

.loop-cta-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary, #f1f5f9);
  margin: 0 0 0.2rem;
}

.loop-cta-sub {
  font-size: 0.825rem;
  color: var(--text-secondary, #94a3b8);
  margin: 0;
}

.loop-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.125rem;
  background: linear-gradient(135deg, #4f7fff, #7c3aed);
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  transition: opacity 0.15s;
}
.loop-cta-btn:hover { opacity: 0.85; }
</style>
