import {useMutation} from '@tanstack/react-query'
import {checkApi} from '../../api/check.api'

interface CheckPayload {
    taskId: number
    code: string
    language: string
    submitted_at: string
}

export const useCheckSolution = () => {
    return useMutation({
        mutationFn: (payload: CheckPayload) =>
            checkApi.checkSolution(payload.taskId, {
                code: payload.code,
                language: payload.language,
                submitted_at: payload.submitted_at,
            })
    })
}