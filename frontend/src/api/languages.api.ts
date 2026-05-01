import api from "../lib/api.ts";

export interface Language {
    id: number
    language: string
}

export const languageApi = {
    getLanguages: async (): Promise<Language[]> => {
        const response = await api.get<Language[]>("/languages/");
        return response.data;
    },
}
