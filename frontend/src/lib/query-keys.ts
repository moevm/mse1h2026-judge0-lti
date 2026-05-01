export const moduleKeys = {
    all: ['modules'] as const,
    lists: () => [...moduleKeys.all, 'list'] as const,
    detail: (id: number | string) => [...moduleKeys.all, 'detail', id] as const,
    tasks: (moduleId: number | string) => [...moduleKeys.all, 'tasks', moduleId] as const,
}

export const taskKeys = {
    all: ['tasks'] as const,
    lists: () => [...taskKeys.all, 'list'] as const,
    list: (filters: Record<string, unknown>) => [...taskKeys.lists(), filters] as const,
    detail: (id: number | string) => [...taskKeys.all, 'detail', id] as const,
}

export const languageKeys = {
    all: ['languages'] as const,
    lists: () => [...languageKeys.all, 'list'] as const,
}

export const solutionKeys = {
    byUser: (userId: number | string) => ['solutions', 'user', userId] as const,
    detail: (userId: number | string, taskId: number | string) =>
        ['solutions', 'user', userId, 'task', taskId] as const,
    attempts: (userId: number | string, taskId: number | string) =>
        ['solutions', 'user', userId, 'task', taskId, 'attempts'] as const,
}
