import api from '../lib/api'


export interface Module {
    id: number
    title: string
    description: string
    tasks: number[] | Task[]
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
    tests: TaskTest[]
}

export interface TaskTest {
    id?: number
    title: string
    stdin: string
    stdout: string
}

export interface TaskPayload {
    title: string
    description: string
    timeout: number
    languages: string[]
    tests?: TaskTest[]
}

export interface ModulePayload {
    title: string
    description: string
}

export interface ModuleFilters {
    search?: string
    created_from?: string
    created_to?: string
    updated_from?: string
    updated_to?: string
    sort_by?: 'created_at' | 'updated_at' | 'title'
    sort_order?: 'asc' | 'desc'
}

export interface TaskFilters {
    search?: string
    timeout_from?: number
    timeout_to?: number
    created_from?: string
    created_to?: string
    updated_from?: string
    updated_to?: string
    sort_by?: 'created_at' | 'updated_at' | 'timeout' | 'title'
    sort_order?: 'asc' | 'desc'
}


export const modulesApi = {
    getModules: async (filters?: ModuleFilters): Promise<Module[]> => {
        const { data } = await api.get<Module[]>('/modules/', {
            params: filters,
            silent: true
        })
        return data
    },

    getModule: async (moduleId: number): Promise<Module> => {
        const { data } = await api.get<Module>(`/modules/${moduleId}`, { silent: true })
        return data
    },

    getModuleTasks: async (moduleId: number): Promise<Task[]> => {
        const { data } = await api.get<Task[]>(`/modules/${moduleId}/tasks`, { silent: true })
        return data
    },

    createModule: async (payload: ModulePayload): Promise<Module> => {
        const { data } = await api.post<Module>('/modules/', payload)
        return data
    },

    updateModule: async (moduleId: number, payload: Partial<ModulePayload>): Promise<Module> => {
        const { data } = await api.patch<Module>(`/modules/${moduleId}`, payload)
        return data
    },

    addModuleTasks: async (moduleId: number, taskIds: number[]): Promise<Module> => {
        const { data } = await api.post<Module>(`/modules/${moduleId}/tasks`, { task_ids: taskIds })
        return data
    },

    removeModuleTask: async (moduleId: number, taskId: number): Promise<Module> => {
        const { data } = await api.delete<Module>(`/modules/${moduleId}/tasks/${taskId}`)
        return data
    },

    reorderModuleTasks: async (moduleId: number, taskIds: number[]): Promise<Module> => {
        const { data } = await api.patch<Module>(`/modules/${moduleId}/tasks/reorder`, {
            tasks: taskIds.map((taskId, index) => ({
                task_id: taskId,
                order: index + 1,
            })),
        })
        return data
    },
}

export const tasksApi = {
    getTasks: async (filters?: TaskFilters): Promise<Task[]> => {
        const { data } = await api.get<Task[]>('/tasks/', { params: filters, silent: true })
        return data
    },

    getTask: async (taskId: number): Promise<Task> => {
        const { data } = await api.get<Task>(`/tasks/${taskId}`, { silent: true })
        return data
    },

    createTask: async (payload: TaskPayload): Promise<Task> => {
        const { data } = await api.post<Task>('/tasks/', payload)
        return data
    },

    updateTask: async (taskId: number, payload: Partial<TaskPayload>): Promise<Task> => {
        const { data } = await api.patch<Task>(`/tasks/${taskId}`, payload)
        return data
    },

    deleteTask: async (taskId: number): Promise<void> => {
        await api.delete(`/tasks/${taskId}`)
    },
}