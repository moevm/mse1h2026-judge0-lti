import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { useSolutionAttempts } from '../../hooks/queries/useTaskSolutions'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminTaskSolutionAttempts.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

interface FilterValues {
    [key: string]: string | number | undefined
    status?: string
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
                    { value: 'Accepted', label: 'Принято' },
                    { value: 'Wrong Answer', label: 'Ошибка' },
                    { value: 'Time Limit', label: 'Превышение времени' },
                    { value: 'Memory Limit', label: 'Превышение памяти' },
                    { value: 'Runtime Error', label: 'Ошибка выполнения' },
                    { value: 'Compilation Error', label: 'Ошибка компиляции' },
                ],
            },
        ],
    },
    {
        id: 'memory',
        title: 'Память (КБ)',
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
                    { value: 'memory_kb', label: 'Памяти' },
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

const AdminTaskSolutionAttempts = () => {
    const { solutionId } = useParams<{ solutionId: string }>()
    const navigate = useNavigate()
    const sid = Number(solutionId)

    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })

    const { data: attempts = [], isLoading, isError } = useSolutionAttempts(sid)

    const getFilteredAttempts = () => {
        let result = [...attempts]

        if (debouncedSearch) {
            result = result.filter(attempt =>
                attempt.message?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
                attempt.stdout?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
                attempt.stderr?.toLowerCase().includes(debouncedSearch.toLowerCase())
            )
        }

        if (filters.status && filters.status !== '') {
            result = result.filter(a => a.status === filters.status)
        }

        const memoryMin = filters.memory_min
        const memoryMax = filters.memory_max
        if (memoryMin && memoryMin !== '') {
            const minValue = Number(memoryMin)
            result = result.filter(a => (a.memory_kb ?? 0) >= minValue)
        }
        if (memoryMax && memoryMax !== '') {
            const maxValue = Number(memoryMax)
            result = result.filter(a => (a.memory_kb ?? 0) <= maxValue)
        }

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

        if (filters.from_date && filters.from_date !== '') {
            const fromDate = new Date(filters.from_date as string)
            result = result.filter(a => new Date(a.created_at) >= fromDate)
        }
        if (filters.to_date && filters.to_date !== '') {
            const toDate = new Date(filters.to_date as string)
            result = result.filter(a => new Date(a.created_at) <= toDate)
        }

        const sortBy = filters.sort_by as string || 'created_at'
        const sortOrder = filters.sort_order as string || 'desc'

        result.sort((a, b) => {
            let valA: any = a[sortBy as keyof typeof a]
            let valB: any = b[sortBy as keyof typeof b]

            if (sortBy === 'created_at') {
                valA = new Date(valA)
                valB = new Date(valB)
            }
            if (sortBy === 'memory_kb') {
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

    const formatMemory = (kb: number | null | undefined) => {
        if (kb === null || kb === undefined) return '—'
        if (kb < 1024) return `${kb} КБ`
        return `${(kb / 1024).toFixed(1)} МБ`
    }

    const formatTime = (ms: number | null | undefined) => {
        if (ms === null || ms === undefined) return '—'
        if (ms < 1000) return `${ms} мс`
        return `${(ms / 1000).toFixed(2)} с`
    }

    const formatScore = (score: number | null | undefined) => (
        typeof score === 'number' ? `${score} баллов` : '—'
    )

    const getStatusIcon = (status: string, isSolved: boolean) => {
        if (status === 'Accepted' && isSolved) return '✓'
        return '✗'
    }

    const getStatusClass = (status: string, isSolved: boolean) => {
        if (status === 'Accepted' && isSolved) return styles.solvedIcon
        return styles.failedIcon
    }

    const getStatusText = (status: string) => {
        switch (status) {
            case 'Accepted': return 'Принято'
            case 'Wrong Answer': return 'Неверный ответ'
            case 'Time Limit': return 'Превышение времени'
            case 'Memory Limit': return 'Превышение памяти'
            case 'Runtime Error': return 'Ошибка выполнения'
            case 'Compilation Error': return 'Ошибка компиляции'
            default: return status
        }
    }

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({ ...prev, [fieldId]: value }))
    }

    const handleBack = () => {
        if (window.history.length > 1) {
            navigate(-1)
        } else {
            navigate('/admin/tasks')
        }
    }

    return (
        <div className="page">
            <md-icon className={styles.profileIcon}>account_circle</md-icon>

            <button className={styles.backBtn} onClick={handleBack}>
                <md-icon>arrow_back</md-icon>
            </button>

            <h1 className={styles.title}>Попытки решения #{solutionId}</h1>

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
                        <div key={attempt.id} className={styles.item}>
                            <div className={styles.itemThumb}>
                                <span className={getStatusClass(attempt.status, attempt.is_solved)}>
                                    {getStatusIcon(attempt.status, attempt.is_solved)}
                                </span>
                            </div>
                            <div className={styles.itemContent}>
                                <div className={styles.itemTitle}>
                                    {attempt.language} · {getStatusText(attempt.status)}
                                </div>
                                <div className={styles.itemMeta}>
                                    {formatDate(attempt.created_at)}
                                    {' · '}{formatScore(attempt.score)}
                                    {' · '}{formatTime(attempt.time_ms)}
                                    {' · '}{formatMemory(attempt.memory_kb)}
                                </div>
                                {attempt.message && (
                                    <div className={`${styles.itemMessage} ${attempt.is_solved ? styles.messageSuccess : styles.messageError}`}>
                                        {attempt.message}
                                    </div>
                                )}
                                <details className={styles.itemDetails}>
                                    <summary>Код решения</summary>
                                    <pre className={styles.codeBlock}>
                                        <code>{attempt.source_code}</code>
                                    </pre>
                                </details>
                                {attempt.stdout && (
                                    <details className={styles.itemDetails}>
                                        <summary>Вывод программы</summary>
                                        <pre className={styles.outputBlock}>
                                            {attempt.stdout}
                                        </pre>
                                    </details>
                                )}
                                {attempt.stderr && (
                                    <details className={styles.itemDetails}>
                                        <summary>Ошибка (stderr)</summary>
                                        <pre className={styles.errorBlock}>
                                            {attempt.stderr}
                                        </pre>
                                    </details>
                                )}
                                {attempt.compile_output && (
                                    <details className={styles.itemDetails}>
                                        <summary>Ошибка компиляции</summary>
                                        <pre className={styles.errorBlock}>
                                            {attempt.compile_output}
                                        </pre>
                                    </details>
                                )}
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

export default AdminTaskSolutionAttempts
