import { useQuery } from '@tanstack/react-query'
import { tasksApi } from '../../api/modules.api'
import { taskKeys } from '../../lib/query-keys'

export const useTask = (taskId: number | null) => {
    return useQuery({
        queryKey: taskKeys.detail(taskId ?? 0),
        queryFn: () => tasksApi.getTask(taskId!),
        enabled: taskId !== null,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}