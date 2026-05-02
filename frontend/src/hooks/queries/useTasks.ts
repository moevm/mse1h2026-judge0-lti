import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { tasksApi, type Task, type TaskFilters } from '../../api/modules.api'

export const useTasks = (filters?: TaskFilters) => {
    return useQuery<Task[], AxiosError<{ detail?: string }>>({
        queryKey: ['tasks', 'list', filters || {}],
        queryFn: () => tasksApi.getTasks(filters),
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}