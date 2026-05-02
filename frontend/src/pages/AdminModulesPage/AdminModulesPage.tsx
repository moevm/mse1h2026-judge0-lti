import { useMemo, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import { useModules } from '../../hooks/queries/useModules'
import { getGeneratedArtworkStyle } from '../../lib/generatedArtwork'
import type { Module, ModuleFilters } from '../../api/modules.api'
import type { FilterGroup } from "../../components/FilterDialog/FilterDialog"
import type { FilterValues } from '../../components/AdminToolbar/AdminToolbar'
import styles from './AdminModulesPage.module.scss'
import Spinner from "../../UI/Spinner/Spinner.tsx";

const filterGroups: FilterGroup[] = [
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

const formatDate = (value: string | null) => {
    if (!value) return null
    return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    }).format(new Date(value))
}

const ModuleCard = ({ module }: { module: Module }) => {
    const taskCount = module.tasks.length
    const updatedAt = formatDate(module.updated_at ?? module.created_at)
    const meta = [updatedAt && `обновлён ${updatedAt}`, `${taskCount} задач`]
        .filter(Boolean)
        .join(' · ')

    return (
        <Link className={styles.card} to={`/admin/modules/${module.id}`}>
            <div className={styles.artwork} style={getGeneratedArtworkStyle(`${module.id}-${module.title}`)}>
                <span className={styles.triangle} />
                <span className={styles.starburst} />
                <span className={styles.square} />
                <span className={styles.orbit} />
                <span className={styles.bar} />
            </div>
            <h2>{module.title}</h2>
            {meta && <p className={styles.meta}>{meta}</p>}
            {module.description && <p className={styles.description}>{module.description}</p>}
        </Link>
    )
}

const AdminModulesPage = () => {
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })
    const [debouncedSearch] = useDebounce(search, 500)

    const queryFilters: ModuleFilters = useMemo(() => ({
        search: debouncedSearch || undefined,
        created_from: filters.created_from as string | undefined,
        created_to: filters.created_to as string | undefined,
        updated_from: filters.updated_from as string | undefined,
        updated_to: filters.updated_to as string | undefined,
        sort_by: filters.sort_by as 'created_at' | 'updated_at' | 'title' | undefined,
        sort_order: filters.sort_order as 'asc' | 'desc' | undefined,
    }), [debouncedSearch, filters])

    const { data: modules = [], isLoading, isError } = useModules(queryFilters)

    const handleFilterChange = useCallback((fieldId: string, value: string | number | undefined) => {
        setFilters(prev => ({ ...prev, [fieldId]: value }))
    }, [])

    return (
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
                    <md-filled-button type="button" onClick={() => navigate('/admin/modules/new')}>
                        Добавить модуль
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
                    <span>Не удалось загрузить модули</span>
                </div>
            )}

            {!isLoading && !isError && (
                <>
                    <div className={styles.cards}>
                        {modules.map(module => (
                            <ModuleCard key={module.id} module={module} />
                        ))}
                    </div>

                    {modules.length === 0 && (
                        <div className={styles.state}>
                            <span>Модули не найдены</span>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default AdminModulesPage