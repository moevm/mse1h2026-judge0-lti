import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { toast } from 'sonner'

declare module 'axios' {
    interface AxiosRequestConfig {
        silent?: boolean
    }
}

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? '/api',
})

api.interceptors.response.use(
    response => response,
    (error) => {
        const config = error.config as InternalAxiosRequestConfig & { silent?: boolean }

        if (!config?.silent) {
            const message = error.response?.data?.detail
                ?? error.response?.data?.message
                ?? `Ошибка запроса: ${error.message}`
            toast.error('Что-то пошло не так', { description: message })
        }

        return Promise.reject(error)
    }
)

export default api