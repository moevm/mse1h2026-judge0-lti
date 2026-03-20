import api from '../lib/api'

// ─── Типы (соответствуют схемам бэкенда) ────────────────────────────────────

export interface Module {
    id: number
    title: string
    description: string
    tasks: number[]
    created_at: string
    updated_at: string | null
}

export interface Task {
    id: number
    title: string
    description: string
    timeout: number
    languages: string[]
    created_at: string
    updated_at: string | null
}

// ─── API методы ─────────────────────────────────────────────────────────────

export const modulesApi = {
    getModules: async (): Promise<Module[]> => {
        const { data } = await api.get<Module[]>('/modules/', { silent: true })
        return data
    },

    getModuleTasks: async (moduleId: number): Promise<Task[]> => {
        const { data } = await api.get<Task[]>(`/modules/${moduleId}/tasks`, { silent: true })
        return data
    },
}

export const tasksApi = {
    getTask: async (taskId: number): Promise<Task> => {
        const { data } = await api.get<Task>(`/tasks/${taskId}`, { silent: true })
        return data
    },
}