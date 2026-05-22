import { useNavigate, useParams } from "react-router-dom";
import styles from "./AdminTaskSolutions.module.scss"
import Spinner from "../../UI/Spinner/Spinner";
import AdminToolbar, { type FilterValues } from "../../components/AdminToolbar/AdminToolbar";
import type { FilterGroup } from "../../components/FilterDialog/FilterDialog";
import { useCallback, useMemo, useState } from "react";
import { useDebounce } from "use-debounce";
import type { TaskSolutionFilters } from "../../api/task_solutions.api";
import { useTaskSolutions } from "../../hooks/queries/useTaskSolutions";

const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'status',
        title: 'Статус решения',
        fields: [
            {
                id: 'is_solved',
                label: 'Статус',
                type: 'select',
                options: [
                    { value: '', label: 'Все' },
                    { value: 'true', label: 'Решено' },
                    { value: 'false', label: 'Не решено' },
                ],
            },
        ],
    },
    {
        id: 'score',
        title: 'Баллы',
        fields: [
            {
                id: 'score_min',
                label: 'Балл от',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'score_max',
                label: 'Балл до',
                type: 'number',
                min: 0,
                placeholder: 'до',
            },
        ],
    },
    {
        id: 'dates',
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
                    { value: 'updated_at', label: 'Дате обновления' },
                    { value: 'score', label: 'Баллу' },
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

const formatDate = (value: string | null) => {
    if (!value) return '—'
    return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(value))
}

const AdminTaskSolutions = () => {
    const { taskId } = useParams<{taskId: string}>()
    const navigate = useNavigate()
    const tid = Number(taskId)

    const [search, setSearch] = useState('')
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })
    const [debouncedSearch] = useDebounce(search, 500)
    
    const filterGroups = useMemo(() => getFilterGroups(), [])
    
    const queryFilters: TaskSolutionFilters = useMemo(() => ({
        is_solved: filters.is_solved === 'true' ? true : filters.is_solved === 'false' ? false : undefined,
        score_min: filters.score_min as number | undefined,
        score_max: filters.score_max as number | undefined,
        updated_from: filters.updated_from as string | undefined,
        updated_to: filters.updated_to as string | undefined,
        sort_by: filters.sort_by as 'id' | 'score' | 'is_solved' | 'created_at' | 'updated_at' | undefined,
        sort_order: filters.sort_order as 'asc' | 'desc' | undefined,
    }), [filters])
    
    const { data: solutions = [], isLoading, isError } = useTaskSolutions(tid, queryFilters)
    
        const filteredSolutions = useMemo(() => {
        if (!debouncedSearch) return solutions
        const searchLower = debouncedSearch.toLowerCase()
        return solutions.filter(solution => 
            solution.username.toLowerCase().includes(searchLower) ||
            solution.full_name.toLowerCase().includes(searchLower)
        )
    }, [solutions, debouncedSearch])
    
    const handleFilterChange = useCallback((fieldId: string, value: string | number | undefined) => {
        setFilters(prev => ({ ...prev, [fieldId]: value }))
    }, [])

    return (
        <>
            <div className="page">
                <div className={styles.header}>
                    <button className={styles.backButton} onClick={() => navigate(-1)}>
                        <md-icon>arrow_back</md-icon>
                    </button>
                    <div>
                        <h1 className={styles.title}>Решения задачи #{tid}</h1>
                    </div>
                </div>

                <AdminToolbar
                    search={search}
                    onSearchChange={setSearch}
                    filterGroups={filterGroups}
                    filterValues={filters}
                    onFilterChange={handleFilterChange}
                    placeholder="Поиск по имени пользователя..."
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
                        <span>Не удалось загрузить решения</span>
                    </div>
                )}

                {!isLoading && !isError && (
                    <div className={styles.tableWrapper}>
                        <table className={styles.table}>
                            <thead>
                            <tr>
                                <th>Пользователь</th>
                                <th>Результат</th>
                                <th>Статус</th>
                                <th>Обновлено</th>
                                <th></th>
                            </tr>
                            </thead>
                            <tbody>
                            {filteredSolutions.map(solution => (
                                <tr key={solution.id} className={styles.tableRow}>
                                        <td className={styles.user}>
                                            <div className={styles.userName}>{solution.full_name}</div>
                                            <div className={styles.userLogin}>@{solution.username}</div>
                                        </td>
                                    <td className={styles.score}>
                                        {solution.score}
                                    </td>
                                    <td className={styles.status}>
                                        <span className={solution.is_solved ? styles.statusPassed : styles.statusFailed}>
                                            {solution.is_solved ? 'Пройдено' : 'Не пройдено'}
                                        </span>
                                    </td>
                                    <td className={styles.date}>
                                        {formatDate(solution.updated_at)}
                                    </td>
                                    <td className={styles.actions}>
                                        <button
                                            type="button"
                                            className={styles.viewButton}
                                            onClick={() => navigate(`/admin/tasks`)}
                                        >
                                            <md-icon>visibility</md-icon>
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>

                        {filteredSolutions.length === 0 && (
                            <div className={`${styles.state} ${styles.notFoundSolutions}`}>
                                <span>Решения не найдены</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </>
    )
}

export default AdminTaskSolutions