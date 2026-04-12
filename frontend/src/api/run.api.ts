import api from "../lib/api.ts";

export const runApi = {
    checkSolution: async (data: { code: string, language: string, stdin: string, submitted_at: string }) => {
        const response = await api.post(`/run`, data);
        return {
            success: !response.data.stderr && !response.data.compile_output,
            error: response.data.stderr || response.data.compile_output,
            comment: response.data.stdout,
            passed: response.data.stdout,
        };
    },
}