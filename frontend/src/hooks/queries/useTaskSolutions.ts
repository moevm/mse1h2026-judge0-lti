import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { taskSolutionsApi, type TaskSolution, type SolutionAttempt, type TaskSolutionFilters } from '../../api/task_solutions.api'
import { taskSolutionsKeys } from '../../lib/query-keys'


export const useTaskSolutions = (taskId: number | string, filters?: TaskSolutionFilters) => {
    return useQuery<TaskSolution[], AxiosError<{ detail?: string }>>({
        queryKey: taskSolutionsKeys.byTaskWithFilters(taskId, filters),
        queryFn: () => taskSolutionsApi.getByTask(taskId, filters),
        staleTime: 2 * 60 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: false,
        enabled: !!taskId,
    })
}

export const useSolutionAttempts = (solutionId: number | string) => {
    return useQuery<SolutionAttempt[], AxiosError<{ detail?: string }>>({
        queryKey: taskSolutionsKeys.attempts(solutionId),
        queryFn: () => taskSolutionsApi.getAttempts(solutionId),
        staleTime: 5 * 60 * 1000,
        gcTime: 10 * 60 * 1000,
        retry: false,
        enabled: !!solutionId,
    })
}

export const useTaskSolutionsWithDefaults = (taskId: number | string) => {
    const defaultFilters: TaskSolutionFilters = {
        sort_by: 'created_at',
        sort_order: 'desc',
    }
    
    return useTaskSolutions(taskId, defaultFilters)
}