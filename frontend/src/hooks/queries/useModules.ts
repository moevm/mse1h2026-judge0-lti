import { useQuery } from '@tanstack/react-query'
import { modulesApi } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'

export const useModules = () => {
    return useQuery({
        queryKey: moduleKeys.all,
        queryFn: modulesApi.getModules,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}