import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import AdminToolbar, { type FilterGroup } from '../AdminToolbar/AdminToolbar'
import type { Language } from '../../api/languages.api'
import { tasksApi, type Task, type TaskFilters, type TaskPayload } from '../../api/modules.api'
import { taskKeys } from '../../lib/query-keys'
import styles from './TaskModal.module.scss'

interface TaskModalProps {
    moduleTitle?: string
    languages: Language[]
    excludedTaskIds?: number[]
    isOpen: boolean
    isSaving: boolean
    onClose: () => void
    onSubmit?: (payload: TaskPayload) => void
    onAddExisting?: (tasks: Task[]) => void
    onCreateNew?: () => void
}

const baseFilterGroups: FilterGroup[] = [
    {
        id: 'timeout',
        title: 'Время',
        options: [
            { value: 'fast', label: 'До 2 секунд' },
            { value: 'normal', label: '3-5 секунд' },
            { value: 'long', label: 'Больше 5 секунд' },
        ],
    },
    {
        id: 'tests',
        title: 'Тесты',
        options: [
            { value: 'withTests', label: 'С тестами' },
            { value: 'withoutTests', label: 'Без тестов' },
        ],
    },
    {
        id: 'sort',
        title: 'Сортировка',
        options: [
            { value: 'titleAsc', label: 'Название А-Я' },
            { value: 'newest', label: 'Сначала новые' },
            { value: 'timeoutAsc', label: 'Быстрее сначала' },
        ],
    },
]

const buildTaskFilters = (search: string, selectedFilters: Record<string, string | undefined>): TaskFilters => {
    const filters: TaskFilters = {}
    const query = search.trim()

    if (query) filters.search = query

    if (selectedFilters.timeout === 'fast') {
        filters.timeout_to = 2
    }

    if (selectedFilters.timeout === 'normal') {
        filters.timeout_from = 3
        filters.timeout_to = 5
    }

    if (selectedFilters.timeout === 'long') {
        filters.timeout_from = 6
    }

    if (selectedFilters.sort === 'titleAsc') {
        filters.sort_by = 'title'
        filters.sort_order = 'asc'
    }

    if (selectedFilters.sort === 'newest') {
        filters.sort_by = 'created_at'
        filters.sort_order = 'desc'
    }

    if (selectedFilters.sort === 'timeoutAsc') {
        filters.sort_by = 'timeout'
        filters.sort_order = 'asc'
    }

    return filters
}

const TaskModal = ({ moduleTitle, languages, excludedTaskIds = [], isOpen, isSaving, onClose, onAddExisting, onCreateNew }: TaskModalProps) => {
    const [search, setSearch] = useState('')
    const [selectedFilters, setSelectedFilters] = useState<Record<string, string | undefined>>({})
    const [selectedTaskIds, setSelectedTaskIds] = useState<Set<number>>(() => new Set())

    const apiFilters = useMemo(() => buildTaskFilters(search, selectedFilters), [search, selectedFilters])
    const filterGroups = useMemo<FilterGroup[]>(() => [
        {
            id: 'language',
            title: 'Язык',
            options: languages.map(item => ({
                value: item.language,
                label: item.language,
            })),
        },
        ...baseFilterGroups,
    ], [languages])

    const {
        data: tasks = [],
        isLoading,
        isError,
    } = useQuery({
        queryKey: taskKeys.list({ ...apiFilters }),
        queryFn: () => tasksApi.getTasks(apiFilters),
        enabled: isOpen,
        retry: false,
    })

    const visibleTasks = useMemo(() => tasks.filter(task => {
        if (excludedTaskIds.includes(task.id)) return false
        if (selectedFilters.language && !task.languages.includes(selectedFilters.language)) return false
        if (selectedFilters.tests === 'withTests') return task.tests.length > 0
        if (selectedFilters.tests === 'withoutTests') return task.tests.length === 0
        return true
    }), [excludedTaskIds, selectedFilters.language, selectedFilters.tests, tasks])

    if (!isOpen) {
        return null
    }

    const updateFilter = (groupId: string, value: string | null) => {
        setSelectedFilters(current => ({
            ...current,
            [groupId]: value ?? undefined,
        }))
    }

    const toggleTask = (taskId: number) => {
        setSelectedTaskIds(current => {
            const next = new Set(current)

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
                        selectedFilters={selectedFilters}
                        onFilterChange={updateFilter}
                        placeholder="Поиск задач"
                        variant="compact"
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
