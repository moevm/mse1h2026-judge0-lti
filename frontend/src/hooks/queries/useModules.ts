import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { modulesApi, type Module } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'

export const useModules = () => {
    return useQuery<Module[], AxiosError<{ detail?: string }>>({
        queryKey: moduleKeys.lists(),
        queryFn: modulesApi.getModules,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}
