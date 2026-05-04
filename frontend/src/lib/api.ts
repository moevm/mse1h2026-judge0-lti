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

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
        ?? localStorage.getItem('accessToken')
        ?? localStorage.getItem('token')

    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }

    return config
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

api.interceptors.response.use(
  res => res,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const res = await api.post('/auth/refresh', {}, { withCredentials: true })

      const access = res.data.access_token
      localStorage.setItem('access_token', access)

      originalRequest.headers = {
        ...originalRequest.headers,
        Authorization: `Bearer ${access}`,
      }

      return api(originalRequest)
    } catch (e) {
      localStorage.removeItem('access_token')
      return Promise.reject(e)
    }
  }
)
export default api
