/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'primevue/config' {
  import { Plugin } from 'vue'
  const plugin: Plugin
  export default plugin
}

declare module 'primevue/toastservice' {
  import { Plugin } from 'vue'
  const plugin: Plugin
  export default plugin
}

declare module 'primevue/confirmationservice' {
  import { Plugin } from 'vue'
  const plugin: Plugin
  export default plugin
}

declare module 'primevue/usetoast' {
  export interface ToastMessageOptions {
    severity?: 'success' | 'info' | 'warn' | 'error'
    summary?: string
    detail?: string
    life?: number
    closable?: boolean
  }

  export interface ToastService {
    add(message: ToastMessageOptions): void
    removeGroup(group: string): void
    removeAllGroups(): void
  }

  export function useToast(): ToastService
}

declare module 'primevue/*' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
