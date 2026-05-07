import { ref } from 'vue';
import {
  createUploadGroup,
  listUploadGroups,
  getUploadGroup,
  addVideoToGroup,
  removeVideoFromGroup,
  patchUploadGroup,
  deleteUploadGroup,
} from '@/services/api';
import type { UploadGroup } from '@/types/upload_group.types';

export function useUploadGroups() {
  const groups = ref<UploadGroup[]>([]);
  const currentGroup = ref<UploadGroup | null>(null);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref<string | null>(null);

  async function fetchGroups(userId: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const data = await listUploadGroups(userId);
      groups.value = data.groups;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load groups';
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchGroup(groupId: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const data = await getUploadGroup(groupId);
      currentGroup.value = data;
      return data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load group';
    } finally {
      isLoading.value = false;
    }
  }

  async function createGroup(userId: string, name: string, platforms: string[], privacyStatus: string = 'private', category: string = 'entertainment') {
    isSaving.value = true;
    error.value = null;
    try {
      const group = await createUploadGroup({ user_id: userId, name, platforms, privacy_status: privacyStatus, category });
      groups.value.unshift(group);
      return group;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create group';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function addVideo(groupId: string, formData: FormData, onProgress?: (pct: number) => void) {
    isSaving.value = true;
    error.value = null;
    try {
      const result = await addVideoToGroup(groupId, formData, onProgress);
      if (currentGroup.value?.id === groupId) {
        await fetchGroup(groupId);
      }
      return result;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to add video';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function removeVideo(groupId: string, gvId: string, userId: string) {
    error.value = null;
    try {
      await removeVideoFromGroup(groupId, gvId, userId);
      if (currentGroup.value?.id === groupId) {
        await fetchGroup(groupId);
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to remove video';
      throw err;
    }
  }

  async function updateGroup(groupId: string, userId: string, updates: { name?: string; status?: string }) {
    isSaving.value = true;
    error.value = null;
    try {
      const updated = await patchUploadGroup(groupId, { user_id: userId, ...updates });
      const idx = groups.value.findIndex(g => g.id === groupId);
      if (idx !== -1) groups.value[idx] = updated;
      if (currentGroup.value?.id === groupId) currentGroup.value = updated;
      return updated;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update group';
      throw err;
    } finally {
      isSaving.value = false;
    }
  }

  async function removeGroup(groupId: string, userId: string) {
    error.value = null;
    try {
      await deleteUploadGroup(groupId, userId);
      groups.value = groups.value.filter(g => g.id !== groupId);
      if (currentGroup.value?.id === groupId) currentGroup.value = null;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete group';
      throw err;
    }
  }

  return {
    groups,
    currentGroup,
    isLoading,
    isSaving,
    error,
    fetchGroups,
    fetchGroup,
    createGroup,
    addVideo,
    removeVideo,
    updateGroup,
    removeGroup,
  };
}
