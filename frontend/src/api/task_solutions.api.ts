import api from '../lib/api'

export type SortByField = 'id' | 'score' | 'is_solved' | 'created_at' | 'updated_at'
export type SortOrder = 'asc' | 'desc'

export interface TaskSolutionFilters {
    is_solved?: boolean
    score_min?: number
    score_max?: number
    updated_from?: string
    updated_to?: string
    sort_by?: SortByField
    sort_order?: SortOrder
}

export interface TaskSolution {
    id: number
    task_id: number
    user_id: number
    username: string
    full_name: string
    is_solved: boolean
    score: number
    created_at: string
    updated_at: string
}

export interface SolutionAttempt {
    id: number
    solution_id: number
    code: string
    output?: string
    error?: string
    execution_time?: number
    memory_used?: number
    status: 'pending' | 'success' | 'error'
    created_at: string
}

export const taskSolutionsApi = {
    getByTask: async (taskId: number | string, filters?: TaskSolutionFilters) => {
        const { data } = await api.get<TaskSolution[]>(
            `/solutions/tasks/${taskId}`,
            { params: filters }
        )
        return data
    },

    getAttempts: async (solutionId: number | string) => {
        const { data } = await api.get<SolutionAttempt[]>(`/solutions/${solutionId}/attempts`)
        return data
    },
}