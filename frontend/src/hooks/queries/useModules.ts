import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { modulesApi, type Module, type ModuleFilters } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'

export const useModules = (filters?: ModuleFilters) => {
    return useQuery<Module[], AxiosError<{ detail?: string }>>({
        queryKey: moduleKeys.lists(filters),
        queryFn: () => modulesApi.getModules(filters),
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}