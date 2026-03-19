import api from '../lib/api'

export interface User {
    id: number
    username: string
    full_name: string
    role: 'admin' | 'student' | 'teacher'
}

export const usersApi = {
    getUser: async (id: number): Promise<User> => {
        const { data } = await api.get<User>(`/users/${id}`, { silent: true })
        return data
    },

    getUsers: async (): Promise<User[]> => {
        const { data } = await api.get<User[]>('/users', { silent: true })
        return data
    },
}