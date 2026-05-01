import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AdminToolbar, { type FilterGroup } from '../../components/AdminToolbar/AdminToolbar'
import { useModules } from '../../hooks/queries/useModules'
import { getGeneratedArtworkStyle } from '../../lib/generatedArtwork'
import styles from './AdminModulesPage.module.scss'

const filterGroups: FilterGroup[] = [
    {
        id: 'tasks',
        title: 'Задачи',
        options: [
            { value: 'withTasks', label: 'С задачами' },
            { value: 'empty', label: 'Без задач' },
        ],
    },
    {
        id: 'updated',
        title: 'Обновления',
        options: [
            { value: 'recent', label: 'Недавно обновленные' },
            { value: 'old', label: 'Давно не обновлялись' },
        ],
    },
    {
        id: 'sort',
        title: 'Сортировка',
        options: [
            { value: 'titleAsc', label: 'Название А-Я' },
            { value: 'newest', label: 'Сначала новые' },
            { value: 'tasksDesc', label: 'Больше задач' },
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

const getModuleTaskCount = (tasks: unknown[]) => tasks.length

const ModuleArtwork = ({ seed }: { seed: string | number }) => (
    <div className={styles.artwork} style={getGeneratedArtworkStyle(seed)} aria-hidden="true">
        <span className={styles.triangle} />
        <span className={styles.starburst} />
        <span className={styles.square} />
        <span className={styles.orbit} />
        <span className={styles.bar} />
    </div>
)

const AdminModulesPage = () => {
    const navigate = useNavigate()
    const { data: modules = [], isLoading, isError } = useModules()
    const [search, setSearch] = useState('')
    const [selectedFilters, setSelectedFilters] = useState<Record<string, string | undefined>>({})

    const updateFilter = (groupId: string, value: string | null) => {
        setSelectedFilters(current => ({
            ...current,
            [groupId]: value ?? undefined,
        }))
    }

    const filteredModules = useMemo(() => {
        const query = search.trim().toLowerCase()
        const now = Date.now()
        const week = 7 * 24 * 60 * 60 * 1000
        const month = 30 * 24 * 60 * 60 * 1000

        const result = modules.filter(module => {
            const taskCount = getModuleTaskCount(module.tasks)
            const updatedTime = new Date(module.updated_at ?? module.created_at).getTime()
            const matchesSearch = !query
                || module.title.toLowerCase().includes(query)
                || module.description.toLowerCase().includes(query)

            const matchesTasks = !selectedFilters.tasks
                || (selectedFilters.tasks === 'withTasks' && taskCount > 0)
                || (selectedFilters.tasks === 'empty' && taskCount === 0)

            const matchesUpdated = !selectedFilters.updated
                || (selectedFilters.updated === 'recent' && now - updatedTime <= week)
                || (selectedFilters.updated === 'old' && now - updatedTime > month)

            return matchesSearch && matchesTasks && matchesUpdated
        })

        return result.sort((a, b) => {
            if (selectedFilters.sort === 'titleAsc') {
                return a.title.localeCompare(b.title, 'ru')
            }

            if (selectedFilters.sort === 'newest') {
                return new Date(b.updated_at ?? b.created_at).getTime() - new Date(a.updated_at ?? a.created_at).getTime()
            }

            if (selectedFilters.sort === 'tasksDesc') {
                return getModuleTaskCount(b.tasks) - getModuleTaskCount(a.tasks)
            }

            return 0
        })
    }, [modules, search, selectedFilters])

    return (
        <section className={styles.page}>
            <md-icon className={styles.profileIcon}>account_circle</md-icon>

            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={filterGroups}
                selectedFilters={selectedFilters}
                onFilterChange={updateFilter}
                placeholder="Поиск модулей"
                action={(
                    <md-filled-button type="button" onClick={() => navigate('/admin/modules/new')}>
                        Добавить модуль
                        <md-icon slot="icon">upload</md-icon>
                    </md-filled-button>
                )}
            />

            {isLoading ? <div className={styles.state}>Загрузка модулей...</div> : null}
            {isError ? <div className={styles.state}>Не удалось загрузить модули</div> : null}

            <div className={styles.cards}>
                {!isLoading && !isError && filteredModules.map(module => {
                    const updatedAt = formatDate(module.updated_at ?? module.created_at)
                    const taskCount = getModuleTaskCount(module.tasks)
                    const meta = [
                        `${taskCount} задач`,
                        updatedAt ? `обновлен ${updatedAt}` : null,
                    ].filter(Boolean).join(' · ')

                    return (
                        <Link className={styles.card} to={`/admin/modules/${module.id}`} key={module.id}>
                            <ModuleArtwork seed={`${module.id}-${module.title}`} />
                            <h2>{module.title}</h2>
                            {meta ? <p>{meta}</p> : null}
                            {module.description ? <p className={styles.description}>{module.description}</p> : null}
                        </Link>
                    )
                })}

                {!isLoading && !isError && filteredModules.length === 0 ? (
                    <div className={styles.state}>Модули не найдены</div>
                ) : null}
            </div>
        </section>
    )
}

export default AdminModulesPage
