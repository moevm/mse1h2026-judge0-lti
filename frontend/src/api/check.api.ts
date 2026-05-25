import api from "../lib/api.ts";

export const checkApi = {
    checkSolution: async (taskId: number, data: { code: string; language: string, submitted_at: string }) => {
        const response = await api.post(`/check/${taskId}`, data)
        return response.data
    },
    getAttemptsInfo: async (taskId: number) => {
        const response = await api.get(`/check/${taskId}/attempts`)
        return response.data
    },
}