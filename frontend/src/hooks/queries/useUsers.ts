import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../../api/users.api'
import { userKeys } from '../../lib/query-keys'

export const useUsers = () => {
    return useQuery({
        queryKey: userKeys.all,
        queryFn: usersApi.getUsers,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
}