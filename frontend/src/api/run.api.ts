import api from "../lib/api.ts";

export const runApi = {
    checkSolution: async (data: { code: string, language: string, stdin: string, submitted_at: string }) => {
        const response = await api.post(`/run`, data)
        return response.data
    },
}