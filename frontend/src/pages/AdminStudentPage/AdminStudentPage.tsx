import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { useUser, useUserModules } from '../../hooks/queries/useUsers'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminStudentPage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

// Локальный интерфейс фильтров (без импорта FilterValues)
interface FilterValues {
    [key: string]: string | undefined
    sort_by?: string
    sort_order?: string
    task_count_min?: string
    task_count_max?: string
    created_from?: string
    created_to?: string
}

// Группы фильтров для модулей студента
const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'tasks',
        title: 'Количество задач',
        fields: [
            {
                id: 'task_count_min',
                label: 'Мин. задач',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'task_count_max',
                label: 'Макс. задач',
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
                label: 'От',
                type: 'datetime-local',
            },
            {
                id: 'created_to',
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
                    { value: 'task_count', label: 'Количеству задач' },
                    { value: 'created_at', label: 'Дате создания' },
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

const AdminStudentPage = () => {
    const { userId } = useParams<{ userId: string }>()
    const navigate = useNavigate()
    const id = Number(userId)

    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'title',
        sort_order: 'asc',
    })

    const { data: user, isLoading: userLoading } = useUser(id)
    const { data: modules = [], isLoading: modulesLoading } = useUserModules(id)

    const isLoading = userLoading || modulesLoading

    // Фильтрация и сортировка модулей
    const getFilteredModules = () => {
        let result = [...modules]

        // Поиск по названию
        if (debouncedSearch) {
            result = result.filter(module =>
                module.title.toLowerCase().includes(debouncedSearch.toLowerCase())
            )
        }

        // Фильтр по количеству задач
        if (filters.task_count_min && filters.task_count_min !== '') {
            const minValue = Number(filters.task_count_min)
            result = result.filter(module => module.task_count >= minValue)
        }
        if (filters.task_count_max && filters.task_count_max !== '') {
            const maxValue = Number(filters.task_count_max)
            result = result.filter(module => module.task_count <= maxValue)
        }

        // Фильтр по дате создания
        if (filters.created_from && filters.created_from !== '') {
            const fromDate = new Date(filters.created_from as string)
            result = result.filter(module => new Date(module.created_at) >= fromDate)
        }
        if (filters.created_to && filters.created_to !== '') {
            const toDate = new Date(filters.created_to as string)
            result = result.filter(module => new Date(module.created_at) <= toDate)
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
            if (sortBy === 'created_at') {
                valA = new Date(valA)
                valB = new Date(valB)
            }

            if (valA < valB) return sortOrder === 'asc' ? -1 : 1
            if (valA > valB) return sortOrder === 'asc' ? 1 : -1
            return 0
        })

        return result
    }

    const filteredModules = getFilteredModules()
    const filterGroups = getFilterGroups()

    const formatDate = (value: string) =>
        new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric'
        }).format(new Date(value))

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({
            ...prev,
            [fieldId]: value !== undefined ? String(value) : undefined
        }))
    }

    if (isLoading) return <div className={styles.state}><Spinner /></div>
    if (!user) return <div className={styles.state}><span>Пользователь не найден</span></div>

    return (
        <div className="page">
            <md-icon className={styles.profileIcon}>account_circle</md-icon>

            {/* Карточка пользователя */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <div className={styles.avatarCircle}>
                        {user.full_name[0]?.toUpperCase()}
                    </div>
                    <div>
                        <div className={styles.name}>{user.full_name}</div>
                        <div className={styles.username}>@{user.username}</div>
                    </div>
                    <button className={styles.menuBtn}>
                        <md-icon>more_vert</md-icon>
                    </button>
                </div>
                <div className={styles.cardBody}>
                    <div className={styles.infoLabel}>Основная информация</div>
                    <div className={styles.role}>
                        {user.role === 'student' ? 'Студент' : user.role === 'teacher' ? 'Преподаватель' : 'Админ'}
                    </div>
                    <div className={styles.date}>
                        Дата регистрации: {formatDate(user.created_at)}
                    </div>
                </div>
            </div>

            {/* Поиск и фильтры через AdminToolbar */}
            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={filterGroups}
                filterValues={filters}
                onFilterChange={handleFilterChange}
                placeholder="Поиск модулей..."
                variant="page"
                showFilters={true}
            />

            {/* Список модулей */}
            <div className={styles.modulesGrid}>
                {filteredModules.map(module => (
                    <div
                        key={module.id}
                        className={styles.moduleCard}
                        onClick={() => navigate(`/admin/students/${id}/modules/${module.id}`)}
                    >
                        <div className={styles.moduleThumb} />
                        <div className={styles.moduleTitle}>{module.title}</div>
                        <div className={styles.moduleDate}>
                            {formatDate(module.created_at)} · {module.task_count} задач
                        </div>
                    </div>
                ))}
                {filteredModules.length === 0 && modules.length === 0 && (
                    <div className={styles.empty}>Модули не найдены</div>
                )}
                {filteredModules.length === 0 && modules.length > 0 && (
                    <div className={styles.empty}>Модули не найдены по запросу</div>
                )}
            </div>
        </div>
    )
}

export default AdminStudentPage
