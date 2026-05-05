import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi, type UsersFilter, type UserUpdateRequest } from '../../api/users.api'

const userKeys = {
    all: ['users'] as const,
    list: (filters?: UsersFilter) => [...userKeys.all, 'list', filters] as const,
    detail: (id: number) => [...userKeys.all, 'detail', id] as const,
    modules: (id: number) => [...userKeys.all, id, 'modules'] as const,
    moduleTasks: (userId: number, moduleId: number) => [...userKeys.all, userId, 'modules', moduleId, 'tasks'] as const,
    taskAttempts: (taskId: number, userId: number) => [...userKeys.all, userId, 'tasks', taskId, 'attempts'] as const,
}

export const useUsers = (filters?: UsersFilter) =>
    useQuery({
        queryKey: userKeys.list(filters),
        queryFn: () => usersApi.getAll(filters),
    })

export const useUser = (userId: number) =>
    useQuery({
        queryKey: userKeys.detail(userId),
        queryFn: () => usersApi.getById(userId),
        enabled: !!userId,
    })

export const useUserModules = (userId: number) =>
    useQuery({
        queryKey: userKeys.modules(userId),
        queryFn: () => usersApi.getModules(userId),
        enabled: !!userId,
    })

export const useUserModuleTasks = (userId: number, moduleId: number) =>
    useQuery({
        queryKey: userKeys.moduleTasks(userId, moduleId),
        queryFn: () => usersApi.getModuleTasks(userId, moduleId),
        enabled: !!userId && !!moduleId,
    })

export const useUserTaskAttempts = (taskId: number, userId: number) =>
    useQuery({
        queryKey: userKeys.taskAttempts(taskId, userId),
        queryFn: () => usersApi.getTaskAttempts(taskId, userId),
        enabled: !!taskId && !!userId,
    })

export const useAttempt = (attemptId: number) =>
    useQuery({
        queryKey: ['attempt', attemptId],
        queryFn: () => usersApi.getAttempt(attemptId),
        enabled: !!attemptId,
    })

export const useUpdateUser = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ userId, payload }: { userId: number; payload: UserUpdateRequest }) =>
            usersApi.update(userId, payload),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: userKeys.all })
        },
    })
}

export const useDeleteUser = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (userId: number) => usersApi.delete(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: userKeys.all })
        },
    })
}
