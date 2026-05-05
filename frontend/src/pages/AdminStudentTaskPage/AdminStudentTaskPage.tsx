import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { useUserTaskAttempts } from '../../hooks/queries/useUsers'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminStudentTaskPage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

interface FilterValues {
    [key: string]: string | number | undefined  // ← разрешить number
    status?: string
    language?: string
    memory_min?: string
    memory_max?: string
    time_min?: string
    time_max?: string
    from_date?: string
    to_date?: string
    sort_by?: string
    sort_order?: string
}

const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'status',
        title: 'Статус',
        fields: [
            {
                id: 'status',
                label: 'Статус',
                type: 'select',
                options: [
                    { value: '', label: 'Все' },
                    { value: 'passed', label: 'Успешные' },
                    { value: 'failed', label: 'Неудачные' },
                ],
            },
        ],
    },
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
                    { value: 'Python', label: 'Python' },
                    { value: 'JavaScript', label: 'JavaScript' },
                    { value: 'Java', label: 'Java' },
                    { value: 'C++', label: 'C++' },
                    { value: 'Go', label: 'Go' },
                    { value: 'Rust', label: 'Rust' },
                ],
            },
        ],
    },
    {
        id: 'memory',
        title: 'Память (МБ)',
        fields: [
            {
                id: 'memory_min',
                label: 'От',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'memory_max',
                label: 'До',
                type: 'number',
                min: 0,
                placeholder: 'до',
            },
        ],
    },
    {
        id: 'time',
        title: 'Время (мс)',
        fields: [
            {
                id: 'time_min',
                label: 'От',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'time_max',
                label: 'До',
                type: 'number',
                min: 0,
                placeholder: 'до',
            },
        ],
    },
    {
        id: 'dates',
        title: 'Дата попытки',
        fields: [
            {
                id: 'from_date',
                label: 'От',
                type: 'datetime-local',
            },
            {
                id: 'to_date',
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
                    { value: 'created_at', label: 'Дате' },
                    { value: 'memory_mb', label: 'Памяти' },
                    { value: 'time_ms', label: 'Времени' },
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

const AdminStudentTaskPage = () => {
    const { userId, taskId } = useParams<{ userId: string; taskId: string }>()
    const navigate = useNavigate()
    const uid = Number(userId)
    const tid = Number(taskId)

    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })

    const { data: attempts = [], isLoading, isError } = useUserTaskAttempts(tid, uid)

    // Фильтрация и сортировка попыток
    const getFilteredAttempts = () => {
        let result = [...attempts]

        // Поиск по сообщению
        if (debouncedSearch) {
            result = result.filter(attempt =>
                attempt.message?.toLowerCase().includes(debouncedSearch.toLowerCase())
            )
        }

        // Фильтр по статусу
        if (filters.status === 'passed') {
            result = result.filter(a => a.is_solved)
        } else if (filters.status === 'failed') {
            result = result.filter(a => !a.is_solved)
        }

        // Фильтр по языку
        if (filters.language && filters.language !== '') {
            result = result.filter(a => a.language === filters.language)
        }

        // Фильтр по памяти
        const memoryMin = filters.memory_min
        const memoryMax = filters.memory_max
        if (memoryMin && memoryMin !== '') {
            const minValue = Number(memoryMin)
            result = result.filter(a => (a.memory_mb ?? 0) >= minValue)
        }
        if (memoryMax && memoryMax !== '') {
            const maxValue = Number(memoryMax)
            result = result.filter(a => (a.memory_mb ?? 0) <= maxValue)
        }

        // Фильтр по времени
        const timeMin = filters.time_min
        const timeMax = filters.time_max
        if (timeMin && timeMin !== '') {
            const minValue = Number(timeMin)
            result = result.filter(a => (a.time_ms ?? 0) >= minValue)
        }
        if (timeMax && timeMax !== '') {
            const maxValue = Number(timeMax)
            result = result.filter(a => (a.time_ms ?? 0) <= maxValue)
        }

        // Фильтр по дате
        if (filters.from_date && filters.from_date !== '') {
            const fromDate = new Date(filters.from_date as string)
            result = result.filter(a => new Date(a.created_at) >= fromDate)
        }
        if (filters.to_date && filters.to_date !== '') {
            const toDate = new Date(filters.to_date as string)
            result = result.filter(a => new Date(a.created_at) <= toDate)
        }

        // Сортировка
        const sortBy = filters.sort_by as string || 'created_at'
        const sortOrder = filters.sort_order as string || 'desc'

        result.sort((a, b) => {
            let valA: any = a[sortBy as keyof typeof a]
            let valB: any = b[sortBy as keyof typeof b]

            if (sortBy === 'created_at') {
                valA = new Date(valA)
                valB = new Date(valB)
            }
            if (sortBy === 'memory_mb') {
                valA = valA ?? 0
                valB = valB ?? 0
            }
            if (sortBy === 'time_ms') {
                valA = valA ?? 0
                valB = valB ?? 0
            }

            if (valA < valB) return sortOrder === 'asc' ? -1 : 1
            if (valA > valB) return sortOrder === 'asc' ? 1 : -1
            return 0
        })

        return result
    }

    const filteredAttempts = getFilteredAttempts()
    const filterGroups = getFilterGroups()

    const formatDate = (value: string) =>
        new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }).format(new Date(value))

    const formatMemory = (mb: number | null) => {
        if (mb === null) return '—'
        if (mb < 1024) return `${mb} МБ`
        return `${(mb / 1024).toFixed(1)} ГБ`
    }

    const formatTime = (ms: number | null) => {
        if (ms === null) return '—'
        if (ms < 1000) return `${ms} мс`
        return `${(ms / 1000).toFixed(2)} с`
    }

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({ ...prev, [fieldId]: value }))
    }

    return (
        <div className="page">
            <md-icon className={styles.profileIcon}>account_circle</md-icon>

            <button className={styles.backBtn} onClick={() => navigate(-1)}>
                <md-icon>arrow_back</md-icon>
            </button>

            <h1 className={styles.title}>Попытки решения</h1>

            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={filterGroups}
                filterValues={filters}
                onFilterChange={handleFilterChange}
                placeholder="Поиск по сообщению..."
                variant="page"
                showFilters={true}
            />

            {isLoading && <div className={styles.state}><Spinner /></div>}
            {isError && <div className={styles.state}><span>Не удалось загрузить попытки</span></div>}

            {!isLoading && !isError && (
                <div className={styles.list}>
                    {filteredAttempts.map(attempt => (
                        <div
                            key={attempt.id}
                            className={styles.item}
                            onClick={() => navigate(`/admin/students/${uid}/attempts/${attempt.id}`)}
                        >
                            <div className={styles.itemThumb}>
                                <span className={attempt.is_solved ? styles.solvedIcon : styles.failedIcon}>
                                    {attempt.is_solved ? '✓' : '✗'}
                                </span>
                            </div>
                            <div className={styles.itemContent}>
                                <div className={styles.itemTitle}>
                                    {attempt.language ?? 'Неизвестный язык'}
                                </div>
                                <div className={styles.itemMeta}>
                                    {formatDate(attempt.created_at)}
                                    {' · '}{formatTime(attempt.time_ms)}
                                    {' · '}{formatMemory(attempt.memory_mb)}
                                </div>
                                <div className={`${styles.itemMessage} ${attempt.is_solved ? styles.messageSuccess : styles.messageError}`}>
                                    {attempt.message || '—'}
                                </div>
                            </div>
                            <button className={styles.moreBtn} onClick={e => e.stopPropagation()}>
                                <md-icon>more_vert</md-icon>
                            </button>
                        </div>
                    ))}
                    {filteredAttempts.length === 0 && (
                        <div className={styles.state}><span>Попытки не найдены</span></div>
                    )}
                </div>
            )}
        </div>
    )
}

export default AdminStudentTaskPage
