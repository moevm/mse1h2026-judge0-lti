import { useMutation } from '@tanstack/react-query'
import { checkApi } from '../../api/check.api'

interface CheckPayload {
    taskId: number
    code: string
    language: string
    submitted_at: string
}
const MAX_ATTEMPTS = 100

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
export const useCheckSolution = () => {
    return useMutation({
        mutationFn: async (payload: CheckPayload) => {
            const ctx = await checkApi.submit(payload.taskId, {
                code: payload.code,
                language: payload.language,
                submitted_at: payload.submitted_at,
            })

            for (let i = 0; i < MAX_ATTEMPTS; i++) {
                const result = await checkApi.getResult(payload.taskId, {
                    tokens: ctx.tokens,
                    solution_id: ctx.solution_id,
                    language_id: ctx.language_id,
                    language: ctx.language,
                    code: payload.code,
                })

                if (result.done) return result

                await sleep(1500)
            }

            throw new Error('Превышено время ожидания результата')
        }
    })
}