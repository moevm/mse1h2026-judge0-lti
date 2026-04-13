import {useMutation} from '@tanstack/react-query'
import {runApi} from '../../api/run.api'

interface RunPayload {
    code: string
    stdin: string
    language: string
    submitted_at: string
}

export const useRunSolution = () => {
    return useMutation({
        mutationFn: (payload: RunPayload) =>
            runApi.checkSolution({
                code: payload.code,
                stdin: payload.stdin,
                language: payload.language,
                submitted_at: payload.submitted_at,
            })
    })
}