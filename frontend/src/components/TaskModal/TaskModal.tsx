import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useDebounce } from 'use-debounce'
import AdminToolbar from '../AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../FilterDialog/FilterDialog'
import type { Language } from '../../api/languages.api'
import { tasksApi, type Task, type TaskFilters } from '../../api/modules.api'
import styles from './TaskModal.module.scss'

interface TaskModalProps {
    moduleTitle?: string
    languages: Language[]
    excludedTaskIds?: number[]
    isOpen: boolean
    isSaving: boolean
    onClose: () => void
    onAddExisting?: (tasks: Task[]) => void
    onCreateNew?: () => void
}

const getFilterGroups = (languages: Language[]): FilterGroup[] => [
    {
        id: 'language',
        title: 'Язык',
        fields: [
            {
                id: 'language',
                label: 'Язык',
                type: 'select',
                options: [
                    { value: '', label: 'Все языки' },
                    ...languages.map(lang => ({
                        value: lang.language,
                        label: lang.language,
                    })),
                ],
            },
        ],
    },
    {
        id: 'timeout',
        title: 'Время выполнения',
        fields: [
            {
                id: 'timeout_from',
                label: 'Мин. время (сек)',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'timeout_to',
                label: 'Макс. время (сек)',
                type: 'number',
                min: 0,
                placeholder: 'до',
            },
        ],
    },
    {
        id: 'dates',
        title: 'Дата создания',
        fields: [
            {
                id: 'created_from',
                label: 'Создан от',
                type: 'datetime-local',
            },
            {
                id: 'created_to',
                label: 'Создан до',
                type: 'datetime-local',
            },
        ],
    },
    {
        id: 'updates',
        title: 'Дата обновления',
        fields: [
            {
                id: 'updated_from',
                label: 'Обновлён от',
                type: 'datetime-local',
            },
            {
                id: 'updated_to',
                label: 'Обновлён до',
                type: 'datetime-local',
            },
        ],
    },
    {
        id: 'sorting',
        title: 'Сортировка',
        fields: [
            {
                id: 'sort_by',
                label: 'Сортировать по',
                type: 'select',
                options: [
                    { value: 'created_at', label: 'Дате создания' },
                    { value: 'updated_at', label: 'Дате обновления' },
                    { value: 'timeout', label: 'Времени выполнения' },
                    { value: 'title', label: 'Названию' },
                ],
            },
            {
                id: 'sort_order',
                label: 'Порядок',
                type: 'select',
                options: [
                    { value: 'desc', label: 'По убыванию' },
                    { value: 'asc', label: 'По возрастанию' },
                ],
            },
        ],
    },
]

const TaskModal = ({
    moduleTitle,
    languages,
    excludedTaskIds = [],
    isOpen,
    isSaving,
    onClose,
    onAddExisting,
    onCreateNew,
}: TaskModalProps) => {
    const [search, setSearch] = useState('')
    const [filterValues, setFilterValues] = useState<Record<string, string | number | undefined>>({})
    const [selectedTaskIds, setSelectedTaskIds] = useState<Set<number>>(new Set())
    const [debouncedSearch] = useDebounce(search, 500)

    const apiFilters = useMemo((): TaskFilters => {
        const filters: TaskFilters = {}
        const query = debouncedSearch.trim()
        if (query) filters.search = query

        const timeoutFrom = filterValues.timeout_from
        if (timeoutFrom !== undefined && timeoutFrom !== '') {
            filters.timeout_from = Number(timeoutFrom)
        }

        const timeoutTo = filterValues.timeout_to
        if (timeoutTo !== undefined && timeoutTo !== '') {
            filters.timeout_to = Number(timeoutTo)
        }

        const createdFrom = filterValues.created_from
        if (createdFrom && typeof createdFrom === 'string') {
            filters.created_from = createdFrom
        }

        const createdTo = filterValues.created_to
        if (createdTo && typeof createdTo === 'string') {
            filters.created_to = createdTo
        }

        const updatedFrom = filterValues.updated_from
        if (updatedFrom && typeof updatedFrom === 'string') {
            filters.updated_from = updatedFrom
        }

        const updatedTo = filterValues.updated_to
        if (updatedTo && typeof updatedTo === 'string') {
            filters.updated_to = updatedTo
        }

        const sortBy = filterValues.sort_by
        if (sortBy && typeof sortBy === 'string') {
            filters.sort_by = sortBy as TaskFilters['sort_by']
        }

        const sortOrder = filterValues.sort_order
        if (sortOrder && typeof sortOrder === 'string') {
            filters.sort_order = sortOrder as 'asc' | 'desc'
        }

        return filters
    }, [debouncedSearch, filterValues])

    const filterGroups = useMemo(() => getFilterGroups(languages), [languages])

    const {
        data: tasks = [],
        isLoading,
        isError,
    } = useQuery({
        queryKey: ['tasks', 'list', JSON.stringify(apiFilters)],
        queryFn: () => tasksApi.getTasks(apiFilters),
        enabled: isOpen,
        retry: false,
    })

    const visibleTasks = useMemo(() => {
        let result = tasks

        const lang = filterValues.language as string
        if (lang && lang !== '') {
            result = result.filter(t => t.languages.includes(lang))
        }

        result = result.filter(t => !excludedTaskIds.includes(t.id))

        return result
    }, [tasks, filterValues, excludedTaskIds])

    if (!isOpen) return null

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilterValues(prev => ({ ...prev, [fieldId]: value }))
    }

    const toggleTask = (taskId: number) => {
        setSelectedTaskIds(prev => {
            const next = new Set(prev)
            if (next.has(taskId)) {
                next.delete(taskId)
            } else {
                next.add(taskId)
            }
            return next
        })
    }

    const selectedTasks = visibleTasks.filter(task => selectedTaskIds.has(task.id))

    const addExisting = () => {
        onAddExisting?.(selectedTasks)
        setSelectedTaskIds(new Set())
    }

    return (
        <div className={styles.overlay} role="presentation" onMouseDown={onClose}>
            <section
                className={styles.modal}
                role="dialog"
                aria-modal="true"
                aria-label="Добавить задачу"
                onMouseDown={event => event.stopPropagation()}
            >
                <header className={styles.header}>
                    <md-icon-button type="button" onClick={onClose} aria-label="Назад">
                        <md-icon>arrow_back</md-icon>
                    </md-icon-button>
                    <div className={styles.title}>
                        <span>Добавить задачу</span>
                        {moduleTitle ? <small>{moduleTitle}</small> : null}
                    </div>
                    <md-icon-button type="button" onClick={onClose} aria-label="Закрыть">
                        <md-icon>close</md-icon>
                    </md-icon-button>
                </header>

                <div className={styles.toolbarBlock}>
                    <AdminToolbar
                        search={search}
                        onSearchChange={setSearch}
                        filterGroups={filterGroups}
                        filterValues={filterValues}
                        onFilterChange={handleFilterChange}
                        placeholder="Поиск задач"
                        variant="compact"
                        showFilters={true}
                    />
                </div>

                <div className={styles.divider} />

                <div className={styles.items}>
                    {isLoading ? <div className={styles.emptyState}>Загрузка задач...</div> : null}
                    {isError ? <div className={styles.emptyState}>Не удалось загрузить задачи</div> : null}

                    {!isLoading && !isError && visibleTasks.map(task => {
                        const meta = [
                            task.languages.join(', '),
                            task.timeout ? `${task.timeout} сек` : null,
                            task.tests.length ? `${task.tests.length} тестов` : null,
                        ].filter(Boolean).join(', ')

                        return (
                            <button className={styles.item} type="button" key={task.id} onClick={() => toggleTask(task.id)}>
                                <span className={styles.avatar}>{task.title.slice(0, 1).toUpperCase()}</span>
                                <span className={styles.itemText}>
                                    <strong>{task.title}</strong>
                                    {task.description ? <span>{task.description}</span> : null}
                                    {meta ? <small>{meta}</small> : null}
                                </span>
                                <md-checkbox checked={selectedTaskIds.has(task.id) || undefined} />
                            </button>
                        )
                    })}

                    {!isLoading && !isError && visibleTasks.length === 0 ? (
                        <div className={styles.emptyState}>Задачи не найдены</div>
                    ) : null}
                </div>

                <footer className={styles.footer}>
                    <md-text-button type="button" onClick={addExisting} disabled={selectedTasks.length === 0 || isSaving || undefined}>
                        Добавить
                    </md-text-button>
                    <md-filled-tonal-button type="button" onClick={onCreateNew} disabled={isSaving || undefined}>
                        Создать новую
                    </md-filled-tonal-button>
                </footer>
            </section>
        </div>
    )
}

export default TaskModal