import {useMemo, useState, useCallback} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useDebounce} from 'use-debounce'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import {useTasks} from '../../hooks/queries/useTasks'
import {useLanguages} from '../../hooks/queries/useLanguages'
import {tasksApi, type TaskFilters} from '../../api/modules.api'
import type {FilterGroup} from "../../components/FilterDialog/FilterDialog"
import type {FilterValues} from '../../components/AdminToolbar/AdminToolbar'
import styles from './AdminTasksPage.module.scss'
import {useMutation, useQueryClient} from "@tanstack/react-query"
import {toast} from "sonner"
import {taskKeys} from "../../lib/query-keys"
import Spinner from "../../UI/Spinner/Spinner.tsx"
import ConfirmModal from "../../UI/ConfirmModal/ConfirmModal.tsx";

const getFilterGroups = (languages: Array<{ language: string }>): FilterGroup[] => [
    {
        id: 'language',
        title: 'Язык',
        fields: [
            {
                id: 'language',
                label: 'Язык',
                type: 'select',
                options: [
                    {value: '', label: 'Все языки'},
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
                    {value: 'created_at', label: 'Дате создания'},
                    {value: 'updated_at', label: 'Дате обновления'},
                    {value: 'timeout', label: 'Времени выполнения'},
                    {value: 'title', label: 'Названию'},
                ],
            },
            {
                id: 'sort_order',
                label: 'Порядок',
                type: 'select',
                options: [
                    {value: 'desc', label: 'По убыванию'},
                    {value: 'asc', label: 'По возрастанию'},
                ],
            },
        ],
    },
]

const formatDate = (value: string | null) => {
    if (!value) return '—'
    return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    }).format(new Date(value))
}

const AdminTasksPage = () => {
    const queryClient = useQueryClient()
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })
    const [debouncedSearch] = useDebounce(search, 500)

    const {data: languages = []} = useLanguages()
    const filterGroups = useMemo(() => getFilterGroups(languages), [languages])

    const queryFilters: TaskFilters = useMemo(() => ({
        search: debouncedSearch || undefined,
        timeout_from: filters.timeout_from as number | undefined,
        timeout_to: filters.timeout_to as number | undefined,
        created_from: filters.created_from as string | undefined,
        created_to: filters.created_to as string | undefined,
        updated_from: filters.updated_from as string | undefined,
        updated_to: filters.updated_to as string | undefined,
        sort_by: filters.sort_by as 'created_at' | 'updated_at' | 'timeout' | 'title' | undefined,
        sort_order: filters.sort_order as 'asc' | 'desc' | undefined,
    }), [debouncedSearch, filters])

    const {data: tasks = [], isLoading, isError} = useTasks(queryFilters)

    const filteredTasks = useMemo(() => {
        const languageFilter = filters.language as string
        if (!languageFilter || languageFilter === '') return tasks
        return tasks.filter(task => task.languages.includes(languageFilter))
    }, [tasks, filters.language])

    const handleFilterChange = useCallback((fieldId: string, value: string | number | undefined) => {
        setFilters(prev => ({...prev, [fieldId]: value}))
    }, [])

    const deleteTaskMutation = useMutation({
        mutationFn: (taskId: number) => tasksApi.deleteTask(taskId),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: taskKeys.all})
            toast.success('Задача удалена')
            setDeleteModalOpen(false)
            setTaskToDelete(null)
        },
        onError: () => {
            toast.error('Не удалось удалить задачу')
            setDeleteModalOpen(false)
            setTaskToDelete(null)
        },
    })
    const [deleteModalOpen, setDeleteModalOpen] = useState(false)
    const [taskToDelete, setTaskToDelete] = useState<number | null>(null)

    const handleDeleteClick = (taskId: number) => {
        setTaskToDelete(taskId)
        setDeleteModalOpen(true)
    }

    const handleConfirmDelete = () => {
        if (taskToDelete) {
            deleteTaskMutation.mutate(taskToDelete)
        }
    }

    const handleCancelDelete = () => {
        setDeleteModalOpen(false)
        setTaskToDelete(null)
    }

    return (<>
            <div className="page">
                <div className={styles.header}>
                    <md-icon className={styles.profileIcon}>account_circle</md-icon>
                </div>

                <AdminToolbar
                    search={search}
                    onSearchChange={setSearch}
                    filterGroups={filterGroups}
                    filterValues={filters}
                    onFilterChange={handleFilterChange}
                    action={
                        <md-filled-button type="button" onClick={() => navigate('/admin/tasks/new')}>
                            Создать задачу
                            <md-icon slot="icon">add</md-icon>
                        </md-filled-button>
                    }
                    placeholder="Название или описание..."
                    variant="page"
                />

                {isLoading && (
                    <div className={styles.state}>
                        <Spinner/>
                    </div>
                )}

                {isError && (
                    <div className={styles.state}>
                        <md-icon>error</md-icon>
                        <span>Не удалось загрузить задачи</span>
                    </div>
                )}

                {!isLoading && !isError && (
                    <div className={styles.tableWrapper}>
                        <table className={styles.table}>
                            <thead>
                            <tr>
                                <th>Название</th>
                                <th>Языки</th>
                                <th>Таймаут</th>
                                <th>Тесты</th>
                                <th>Создана</th>
                                <th>Обновлена</th>
                                <th></th>
                            </tr>
                            </thead>
                            <tbody>
                            {filteredTasks.map(task => (
                                <tr key={task.id} className={styles.tableRow}>
                                    <td className={styles.title}>
                                        <Link to={`/admin/tasks/${task.id}`}>
                                            {task.title}
                                        </Link>
                                    </td>
                                    <td className={styles.languages}>
                                        <div className={styles.languageTags}>
                                            {task.languages.map(lang => (
                                                <span key={lang} className={styles.languageTag}>
                                                    {lang}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className={styles.timeout}>
                                        {task.timeout} сек
                                    </td>
                                    <td className={styles.tests}>
                                        {task.tests.length}
                                    </td>
                                    <td className={styles.date}>
                                        {formatDate(task.created_at)}
                                    </td>
                                    <td className={styles.date}>
                                        {formatDate(task.updated_at)}
                                    </td>
                                    <td className={styles.actions}>
                                        <button
                                            type="button"
                                            className={styles.deleteButton}
                                            onClick={() => handleDeleteClick(task.id)}
                                        >
                                            <md-icon>delete</md-icon>
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>

                        {filteredTasks.length === 0 && (
                            <div className={`${styles.state} ${styles.notFoundTasks}`}>
                                <span>Задачи не найдены</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
            <ConfirmModal
                isOpen={deleteModalOpen}
                title="Удаление задачи"
                message="Вы уверены, что хотите удалить эту задачу?"
                confirmText="Удалить"
                cancelText="Отмена"
                confirmVariant="danger"
                isLoading={deleteTaskMutation.isPending}
                onConfirm={handleConfirmDelete}
                onCancel={handleCancelDelete}
            />
        </>
    )
}

export default AdminTasksPage