// Фабрика ключей

export const userKeys = {
    all: ['users'] as const,
    detail: (id: number | string) => [...userKeys.all, 'detail', id] as const,
}

export const moduleKeys = {
    all: ['modules'] as const,
    detail: (id: number | string) => [...moduleKeys.all, 'detail', id] as const,
    // Задачи конкретного модуля (с порядком из module_tasks_order)
    tasks: (moduleId: number | string) => [...moduleKeys.all, 'tasks', moduleId] as const,
}

export const taskKeys = {
    all: ['tasks'] as const,
    detail: (id: number | string) => [...taskKeys.all, 'detail', id] as const,
    languages: (taskId: number | string) => [...taskKeys.all, 'languages', taskId] as const,
}

export const solutionKeys = {
    // Решения конкретного юзера
    byUser: (userId: number | string) => ['solutions', 'user', userId] as const,
    // Решение юзера по конкретной задаче
    detail: (userId: number | string, taskId: number | string) =>
        ['solutions', 'user', userId, 'task', taskId] as const,
    attempts: (userId: number | string, taskId: number | string) =>
        ['solutions', 'user', userId, 'task', taskId, 'attempts'] as const,
}

export const languageKeys = {
    all: ['languages'] as const,
}