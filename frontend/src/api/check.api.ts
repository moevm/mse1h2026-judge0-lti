import api from "../lib/api.ts";

export const checkApi = {
    submit: async (taskId: number, data: {
        code: string
        language: string
        submitted_at: string
    }) => {
        const response = await api.post(`/check/${taskId}/submit`, data)
        return response.data as {
            tokens: string[]
            solution_id: number
            language_id: number
            language: string
        }
    },

    getResult: async (taskId: number, body: {
        tokens: string[]
        solution_id: number
        language_id: number
        language: string
        code: string
    }) => {
        const response = await api.post(`/check/${taskId}/result`, body)
        return response.data
    },
    getAttemptsInfo: async (taskId: number) => {
        const response = await api.get(`/check/${taskId}/attempts`)
        return response.data
    },
}