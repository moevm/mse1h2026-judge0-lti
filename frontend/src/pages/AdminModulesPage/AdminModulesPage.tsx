import { useMemo, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import { useModules } from '../../hooks/queries/useModules'
import { getGeneratedArtworkStyle } from '../../lib/generatedArtwork'
import { modulesApi, type Module, type ModuleFilters } from '../../api/modules.api'
import { moduleKeys } from '../../lib/query-keys'
import type { FilterGroup } from "../../components/FilterDialog/FilterDialog"
import type { FilterValues } from '../../components/AdminToolbar/AdminToolbar'
import styles from './AdminModulesPage.module.scss'
import Spinner from "../../UI/Spinner/Spinner.tsx";
import ConfirmModal from "../../UI/ConfirmModal/ConfirmModal.tsx";

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

const ModuleCard = ({
    module,
    onDelete,
    isDeleting,
}: {
    module: Module
    onDelete: (module: Module) => void
    isDeleting: boolean
}) => {
    const taskCount = module.tasks.length
    const updatedAt = formatDate(module.updated_at ?? module.created_at)
    const meta = [updatedAt && `обновлён ${updatedAt}`, `${taskCount} задач`]
        .filter(Boolean)
        .join(' · ')

    return (
        <article className={styles.card}>
            <Link className={styles.cardLink} to={`/admin/modules/${module.id}`}>
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
            <button
                type="button"
                className={styles.deleteButton}
                disabled={isDeleting}
                onClick={() => onDelete(module)}
                aria-label={`Удалить модуль ${module.title}`}
                title="Удалить модуль"
            >
                <md-icon>delete</md-icon>
            </button>
        </article>
    )
}

const AdminModulesPage = () => {
    const queryClient = useQueryClient()
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'created_at',
        sort_order: 'desc',
    })
    const [moduleToDelete, setModuleToDelete] = useState<Module | null>(null)
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

    const deleteModuleMutation = useMutation({
        mutationFn: (moduleId: number) => modulesApi.deleteModule(moduleId),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: moduleKeys.all })
            toast.success('Модуль удалён')
            setModuleToDelete(null)
        },
        onError: () => {
            toast.error('Не удалось удалить модуль')
        },
    })

    const handleFilterChange = useCallback((fieldId: string, value: string | number | undefined) => {
        setFilters(prev => ({ ...prev, [fieldId]: value }))
    }, [])

    const handleConfirmDelete = () => {
        if (!moduleToDelete) return
        deleteModuleMutation.mutate(moduleToDelete.id)
    }

    return (
        <>
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
                                <ModuleCard
                                    key={module.id}
                                    module={module}
                                    onDelete={setModuleToDelete}
                                    isDeleting={deleteModuleMutation.isPending && moduleToDelete?.id === module.id}
                                />
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
            <ConfirmModal
                isOpen={Boolean(moduleToDelete)}
                title="Удаление модуля"
                message={`Вы уверены, что хотите удалить модуль «${moduleToDelete?.title ?? ''}»?`}
                confirmText="Удалить"
                cancelText="Отмена"
                confirmVariant="danger"
                isLoading={deleteModuleMutation.isPending}
                onConfirm={handleConfirmDelete}
                onCancel={() => setModuleToDelete(null)}
            />
        </>
    )
}

export default AdminModulesPage
