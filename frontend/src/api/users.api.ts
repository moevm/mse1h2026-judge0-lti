import api from '../lib/api'

export interface User {
    id: number
    username: string
    full_name: string
    role: 'admin' | 'teacher' | 'student'
    solved_count: number
    created_at: string
    updated_at: string | null
    deleted_at: string | null
}

export interface UserModule {
    id: number
    title: string
    description: string
    task_count: number
    created_at: string
}

export interface UserTask {
    id: number
    title: string
    attempt_count: number
    is_solved: boolean
    last_attempt_at: string | null
    test_count: number
}

export interface UserAttempt {
    id: number
    message: string
    language: string | null
    memory_mb: number | null
    time_ms: number | null
    is_solved: boolean
    created_at: string
    source_code: string | null
}

export interface UsersFilter {
    search?: string
    include_deleted?: boolean
    role?: 'admin' | 'teacher' | 'student'
}

export interface UserUpdateRequest {
    full_name?: string
    role?: 'admin' | 'teacher' | 'student'
}

export const usersApi = {
    getAll: async (filters?: UsersFilter): Promise<User[]> => {
        const { data } = await api.get<User[]>('/users/', { params: filters })
        return data
    },

    getById: async (userId: number): Promise<User> => {
        const { data } = await api.get<User>(`/users/${userId}`)
        return data
    },

    update: async (userId: number, payload: UserUpdateRequest): Promise<User> => {
        const { data } = await api.patch<User>(`/users/${userId}`, payload)
        return data
    },

    delete: async (userId: number): Promise<void> => {
        await api.delete(`/users/${userId}`)
    },

    getModules: async (userId: number): Promise<UserModule[]> => {
        const { data } = await api.get<UserModule[]>(`/users/${userId}/modules`)
        return data
    },

    getModuleTasks: async (userId: number, moduleId: number): Promise<UserTask[]> => {
        const { data } = await api.get<UserTask[]>(`/users/${userId}/modules/${moduleId}/tasks`)
        return data
    },

    getTaskAttempts: async (taskId: number, userId: number): Promise<UserAttempt[]> => {
        const { data } = await api.get<UserAttempt[]>(`/tasks/${taskId}/attempts`, {
            params: { user_id: userId }
        })
        return data
    },

    getAttempt: async (attemptId: number): Promise<UserAttempt> => {
        const { data } = await api.get<UserAttempt>(`/attempts/${attemptId}`)
        return data
    },
}
