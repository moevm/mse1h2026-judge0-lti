import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { modulesApi, type Module } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'

export const useModule = (moduleId: number | null) => {
    return useQuery<Module, AxiosError<{ detail?: string }>>({
        queryKey: moduleKeys.detail(moduleId ?? 0),
        queryFn: () => modulesApi.getModule(moduleId!),
        enabled: !!moduleId && moduleId > 0,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });
};