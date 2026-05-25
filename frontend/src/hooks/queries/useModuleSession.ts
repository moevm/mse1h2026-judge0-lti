import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { modulesApi, type ModuleSessionResponse } from '../../api/modules.api'
import { moduleSessionKeys } from '../../lib/query-keys'

export const useModuleSession = (moduleId: number | null) => {
    return useQuery<ModuleSessionResponse, AxiosError<{ detail?: string }>>({
        queryKey: moduleSessionKeys.detail(moduleId!),
        queryFn: () => modulesApi.getModuleSession(moduleId!),
        enabled: !!moduleId,
        staleTime: 30 * 1000,
        refetchOnMount: 'always',
    });
}

export const useStartModuleSession = () => {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (moduleId: number) => modulesApi.startModuleSession(moduleId),
        onSuccess: (data, moduleId) => {
            queryClient.setQueryData(moduleSessionKeys.detail(moduleId), data)
            queryClient.invalidateQueries({ queryKey: moduleSessionKeys.detail(moduleId) })
        },
    })
}

export const useFinishModuleSession = () => {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (moduleId: number) => modulesApi.finishModuleSession(moduleId),
        onSuccess: (data, moduleId) => {
            queryClient.setQueryData(moduleSessionKeys.detail(moduleId), data)
            queryClient.invalidateQueries({ queryKey: moduleSessionKeys.detail(moduleId) })
        },
    })
}
