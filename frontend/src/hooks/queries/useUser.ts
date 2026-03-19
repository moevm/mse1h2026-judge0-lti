import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../../api/users.api'
import { userKeys } from '../../lib/query-keys'

export const useUser = (userId: number | null) => {
    return useQuery({
        queryKey: userKeys.detail(userId ?? 0),
        queryFn: () => usersApi.getUser(userId!),
        enabled: userId !== null,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}