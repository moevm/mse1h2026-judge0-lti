import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { tasksApi, type Task } from '../../api/modules.api'
import { taskKeys } from '../../lib/query-keys'

export const useTask = (taskId: number | null) => {
    return useQuery<Task, AxiosError<{ detail?: string }>>({
        queryKey: taskKeys.detail(taskId ?? 0),
        queryFn: () => tasksApi.getTask(taskId!),
        enabled: taskId !== null,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}