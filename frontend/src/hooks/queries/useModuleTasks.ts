import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { modulesApi, type Task } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'

export const useModuleTasks = (moduleId: number | null) => {
    return useQuery<Task[], AxiosError<{ detail?: string }>>({
        queryKey: moduleKeys.tasks(moduleId ?? 0),
        queryFn: () => modulesApi.getModuleTasks(moduleId!),
        enabled: moduleId !== null,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}