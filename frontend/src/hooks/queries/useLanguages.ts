import { useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { languageApi, type Language } from '../../api/languages.api'
import { languageKeys } from '../../lib/query-keys'

export const useLanguages = () => {
    return useQuery<Language[], AxiosError<{ detail?: string }>>({
        queryKey: languageKeys.lists(),
        queryFn: languageApi.getLanguages,
        staleTime: 24 * 60 * 60 * 1000,
        retry: false,
    })
}
