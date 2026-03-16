// Фабрика ключей
export const userKeys = {
    // Для списка: ['users']
    all: ['users'] as const,

    // Для конкретного юзера: ['users', 'detail', 1]
    detail: (id: number | string) => [...userKeys.all, 'detail', id] as const,
};

export const courseKeys = {
    all: ['courses'] as const,
    tasks: (courseId: string) => [...courseKeys.all, 'tasks', courseId] as const,
}