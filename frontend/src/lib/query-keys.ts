import type {ModuleFilters} from "../api/modules.api.ts";
import type { TaskSolutionFilters } from "../api/task_solutions.api.ts";

export const moduleKeys = {
    all: ['modules'] as const,
    lists: (filters?: ModuleFilters) => [...moduleKeys.all, 'list', filters] as const,
    detail: (id: number | string) => [...moduleKeys.all, 'detail', id] as const,
    tasks: (moduleId: number | string) => [...moduleKeys.all, 'tasks', moduleId] as const,
}

export const moduleSessionKeys = {
    all: ['module-sessions'] as const,
    detail: (moduleId: number | string) => [...moduleSessionKeys.all, 'detail', moduleId] as const,
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

export const taskSolutionsKeys = {
    all: ['admin', 'task-solutions'] as const,
    byTask: (taskId: number | string) => [...taskSolutionsKeys.all, 'task', taskId] as const,
    byTaskWithFilters: (taskId: number | string, filters?: TaskSolutionFilters) => 
        [...taskSolutionsKeys.byTask(taskId), filters] as const,
    attempts: (solutionId: number | string) => 
        [...taskSolutionsKeys.all, 'attempts', solutionId] as const,
}