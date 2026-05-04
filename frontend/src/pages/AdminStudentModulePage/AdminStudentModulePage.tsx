import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { useUser, useUserModuleTasks } from '../../hooks/queries/useUsers'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminStudentModulePage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

// Тип для фильтров (определяем локально)
interface FilterValues {
    [key: string]: string | number | undefined
    sort_by?: string
    sort_order?: string
    status?: string
    attempt_count_min?: number
    test_count_min?: number
    last_attempt_from?: string
    last_attempt_to?: string
}

// Группы фильтров
const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'status',
        title: 'Статус',
        fields: [
            {
                id: 'status',
                label: 'Статус решения',
                type: 'select',
                options: [
                    { value: '', label: 'Все' },
                    { value: 'passed', label: 'Пройдено' },
                    { value: 'failed', label: 'Не пройдено' },
                ],
            },
        ],
    },
    {
        id: 'attempts',
        title: 'Количество попыток',
        fields: [
            {
                id: 'attempt_count_min',
                label: 'Мин. попыток',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
        ],
    },
    {
        id: 'tests',
        title: 'Тесты',
        fields: [
            {
                id: 'test_count_min',
                label: 'Мин. тестов',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
        ],
    },
    {
        id: 'dates',
        title: 'Последняя попытка',
        fields: [
            {
                id: 'last_attempt_from',
                label: 'От',
                type: 'datetime-local',
            },
            {
                id: 'last_attempt_to',
                label: 'До',
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
                    { value: 'title', label: 'Названию' },
                    { value: 'attempt_count', label: 'Количеству попыток' },
                    { value: 'last_attempt_at', label: 'Дате последней попытки' },
                    { value: 'test_count', label: 'Количеству тестов' },
                ],
            },
            {
                id: 'sort_order',
                label: 'Порядок',
                type: 'select',
                options: [
                    { value: 'asc', label: 'По возрастанию' },
                    { value: 'desc', label: 'По убыванию' },
                ],
            },
        ],
    },
]

const AdminStudentModulePage = () => {
    const { userId, moduleId } = useParams<{ userId: string; moduleId: string }>()
    const navigate = useNavigate()
    const id = Number(userId)
    const mid = Number(moduleId)

    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'title',
        sort_order: 'asc',
    })

    const { data: user, isLoading: userLoading } = useUser(id)
    const { data: tasks = [], isLoading: tasksLoading } = useUserModuleTasks(id, mid)

    const isLoading = userLoading || tasksLoading

    // Фильтрация и сортировка задач
    const getFilteredTasks = () => {
        let result = [...tasks]

        // Поиск по названию
        if (debouncedSearch) {
            result = result.filter(task =>
                task.title.toLowerCase().includes(debouncedSearch.toLowerCase())
            )
        }

        // Фильтр по статусу
        if (filters.status === 'passed') {
            result = result.filter(task => task.is_solved)
        } else if (filters.status === 'failed') {
            result = result.filter(task => !task.is_solved)
        }

        // Фильтр по мин. попыткам
        if (filters.attempt_count_min) {
            result = result.filter(task => task.attempt_count >= Number(filters.attempt_count_min))
        }

        // Фильтр по мин. тестам
        if (filters.test_count_min) {
            result = result.filter(task => task.test_count >= Number(filters.test_count_min))
        }

        // Фильтр по дате последней попытки
        if (filters.last_attempt_from) {
            const fromDate = new Date(filters.last_attempt_from as string)
            result = result.filter(task =>
                task.last_attempt_at && new Date(task.last_attempt_at) >= fromDate
            )
        }
        if (filters.last_attempt_to) {
            const toDate = new Date(filters.last_attempt_to as string)
            result = result.filter(task =>
                task.last_attempt_at && new Date(task.last_attempt_at) <= toDate
            )
        }

        // Сортировка
        const sortBy = filters.sort_by as string || 'title'
        const sortOrder = filters.sort_order as string || 'asc'

        result.sort((a, b) => {
            let valA: any = a[sortBy as keyof typeof a]
            let valB: any = b[sortBy as keyof typeof b]

            if (sortBy === 'title') {
                valA = valA?.toLowerCase() || ''
                valB = valB?.toLowerCase() || ''
            }
            if (sortBy === 'last_attempt_at') {
                valA = valA ? new Date(valA) : new Date(0)
                valB = valB ? new Date(valB) : new Date(0)
            }

            if (valA < valB) return sortOrder === 'asc' ? -1 : 1
            if (valA > valB) return sortOrder === 'asc' ? 1 : -1
            return 0
        })

        return result
    }

    const filteredTasks = getFilteredTasks()
    const filterGroups = getFilterGroups()

    const formatDate = (value: string | null) => {
        if (!value) return '—'
        return new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric'
        }).format(new Date(value))
    }

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({ ...prev, [fieldId]: value }))
    }

    if (isLoading) return <div className={styles.state}><Spinner /></div>
    if (!user) return <div className={styles.state}>Пользователь не найден</div>

    return (
        <div className="page">
            <div className={styles.header}>
                <button className={styles.backButton} onClick={() => navigate(-1)}>
                    <md-icon>arrow_back</md-icon>
                </button>
                <div>
                    <h1 className={styles.title}>Задачи модуля</h1>
                    <p className={styles.subtitle}>
                        {user.full_name} · Модуль #{mid}
                    </p>
                </div>
            </div>

            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={filterGroups}
                filterValues={filters}
                onFilterChange={handleFilterChange}
                placeholder="Поиск задач..."
                variant="page"
                showFilters={true}
            />

            <div className={styles.tableWrapper}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>Задача</th>
                            <th>Попытки</th>
                            <th>Тесты</th>
                            <th>Статус</th>
                            <th>Последняя попытка</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredTasks.map(task => (
                            <tr key={task.id}>
                                <td className={styles.taskTitle}>
                                    {task.title}
                                </td>
                                <td className={styles.attemptCount}>
                                    {task.attempt_count}
                                </td>
                                <td className={styles.testCount}>
                                    {task.test_count}
                                </td>
                                <td className={styles.status}>
                                    <span className={task.is_solved ? styles.statusPassed : styles.statusFailed}>
                                        {task.is_solved ? 'Пройдено' : 'Не пройдено'}
                                    </span>
                                </td>
                                <td className={styles.lastAttempt}>
                                    {formatDate(task.last_attempt_at)}
                                </td>
                                <td className={styles.actions}>
                                    <button
                                        className={styles.viewButton}
                                        onClick={() => navigate(`/admin/students/${id}/modules/${mid}/tasks/${task.id}`)}
                                    >
                                        <md-icon>visibility</md-icon>
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {filteredTasks.length === 0 && tasks.length === 0 && (
                    <div className={styles.empty}>Задачи не найдены</div>
                )}
                {filteredTasks.length === 0 && tasks.length > 0 && (
                    <div className={styles.empty}>Задачи не найдены по запросу</div>
                )}
            </div>
        </div>
    )
}

export default AdminStudentModulePage
