import { useQuery } from "@tanstack/react-query"
import { checkApi } from "../../api/check.api"
import { taskKeys } from "../../lib/query-keys"

export const useCheckAttempts = (taskId: number | null) => {
    return useQuery({
        queryKey: [...taskKeys.detail(taskId || ''), 'attempts'],
        queryFn: () => checkApi.getAttemptsInfo(taskId!),
        enabled: !!taskId,
        staleTime: 0,
    })
}