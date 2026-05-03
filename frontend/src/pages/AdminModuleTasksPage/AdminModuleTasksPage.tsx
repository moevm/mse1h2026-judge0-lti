import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { DndContext, PointerSensor, closestCenter, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core'
import { SortableContext, arrayMove, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { toast } from 'sonner'
import TaskModal from '../../components/TaskModal/TaskModal'
import { modulesApi, type Task } from '../../api/modules.api'
import { useModuleTasks } from '../../hooks/queries/useModuleTasks'
import { useLanguages } from '../../hooks/queries/useLanguages'
import { getGeneratedArtworkStyle } from '../../lib/generatedArtwork'
import { moduleKeys, taskKeys } from '../../lib/query-keys'
import styles from './AdminModuleTasksPage.module.scss'

const Artwork = ({ seed, large = false }: { seed: string | number, large?: boolean }) => (
    <div className={large ? `${styles.artwork} ${styles.large}` : styles.artwork} style={getGeneratedArtworkStyle(seed)} aria-hidden="true">
        <span className={styles.triangle} />
        <span className={styles.starburst} />
        <span className={styles.square} />
        <span className={styles.orbit} />
        <span className={styles.bar} />
    </div>
)

const SortableTaskRow = ({
    task,
    moduleId,
    onUnlink,
    isUnlinking,
}: {
    task: Task
    moduleId: number
    onUnlink: (task: Task) => void
    isUnlinking: boolean
}) => {
    const {
        attributes,
        listeners,
        setActivatorNodeRef,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: task.id })
    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        zIndex: isDragging ? 2 : undefined,
    } as CSSProperties
    const meta = [
        task.timeout ? `${task.timeout} сек` : null,
        task.tests.length ? `${task.tests.length} тестов` : null,
    ].filter(Boolean).join(' · ')

    return (
        <article
            ref={setNodeRef}
            style={style}
            className={isDragging ? `${styles.taskRow} ${styles.dragging}` : styles.taskRow}
        >
            <button
                ref={setActivatorNodeRef}
                className={styles.dragHandleButton}
                type="button"
                aria-label={`Переместить задачу ${task.title}`}
                {...attributes}
                {...listeners}
            >
                <md-icon className={styles.dragHandle}>drag_handle</md-icon>
            </button>
            <Artwork seed={`${task.id}-${task.title}`} />
            <div className={styles.taskText}>
                <h3>{task.title}</h3>
                {task.description ? <p>{task.description}</p> : null}
                {meta ? <small>{meta}</small> : null}
            </div>
            <div className={styles.taskActions}>
                <button
                    className={styles.unlinkButton}
                    type="button"
                    disabled={isUnlinking}
                    onClick={() => onUnlink(task)}
                    aria-label={`Отвязать задачу ${task.title} от модуля`}
                >
                    <span className={styles.linkIcon} aria-hidden="true">
                        <md-icon>link</md-icon>
                    </span>
                    <span className={styles.unlinkIcon} aria-hidden="true">
                        <md-icon>link_off</md-icon>
                    </span>
                </button>
                <Link className={styles.editLink} to={`/admin/modules/${moduleId}/tasks/${task.id}/edit`}>
                    <span>ред.</span>
                    <md-icon>play_arrow</md-icon>
                </Link>
            </div>
        </article>
    )
}

const AdminModuleTasksPage = () => {
    const params = useParams()
    const navigate = useNavigate()
    const moduleId = Number(params.moduleId)
    const isNewModule = params.moduleId === 'new'
    const queryClient = useQueryClient()
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [orderedTasks, setOrderedTasks] = useState<Task[]>([])
    const [moduleMenuOpen, setModuleMenuOpen] = useState(false)
    const [isEditingModule, setIsEditingModule] = useState(isNewModule)
    const [moduleTitle, setModuleTitle] = useState('')
    const [moduleDescription, setModuleDescription] = useState('')
    const [isReorderSyncing, setIsReorderSyncing] = useState(false)
    const moduleMenuRef = useRef<HTMLDivElement | null>(null)

    const { data: module } = useQuery({
        queryKey: moduleKeys.detail(moduleId),
        queryFn: () => modulesApi.getModule(moduleId),
        enabled: Number.isFinite(moduleId) && !isNewModule,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })
    const formatModuleDate = (value: string | null) => {
        if (!value) return null
        return new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        }).format(new Date(value))
    }

    const moduleCreatedAt = formatModuleDate(module?.created_at ?? null)
    const moduleUpdatedAt = formatModuleDate(module?.updated_at ?? null)

    const { data: tasks = [], isLoading, isError } = useModuleTasks(Number.isFinite(moduleId) && !isNewModule ? moduleId : null)
    const { data: languages = [] } = useLanguages()

    useEffect(() => {
        if (!module || isNewModule) return
        setModuleTitle(module.title)
        setModuleDescription(module.description)
    }, [isNewModule, module])

    useEffect(() => {
        if (isReorderSyncing) return
        setOrderedTasks(tasks)
    }, [isReorderSyncing, tasks])

    useEffect(() => {
        if (!moduleMenuOpen) return

        const handlePointerDown = (event: PointerEvent) => {
            if (!moduleMenuRef.current?.contains(event.target as Node)) {
                setModuleMenuOpen(false)
            }
        }

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setModuleMenuOpen(false)
            }
        }

        document.addEventListener('pointerdown', handlePointerDown)
        document.addEventListener('keydown', handleKeyDown)

        return () => {
            document.removeEventListener('pointerdown', handlePointerDown)
            document.removeEventListener('keydown', handleKeyDown)
        }
    }, [moduleMenuOpen])

    const sortedTasks = useMemo(() => orderedTasks, [orderedTasks])
    const sortedTaskIds = useMemo(() => sortedTasks.map(task => task.id), [sortedTasks])
    const sensors = useSensors(useSensor(PointerSensor, {
        activationConstraint: { distance: 6 },
    }))

    const addTasksMutation = useMutation({
        mutationFn: (selectedTasks: Task[]) => modulesApi.addModuleTasks(moduleId, selectedTasks.map(task => task.id)),
        onMutate: async selectedTasks => {
            await queryClient.cancelQueries({ queryKey: moduleKeys.tasks(moduleId) })

            const previousTasks = queryClient.getQueryData<Task[]>(moduleKeys.tasks(moduleId))
            const sourceTasks = orderedTasks.length ? orderedTasks : previousTasks ?? []
            const existingIds = new Set(sourceTasks.map(task => task.id))
            const nextTasks = [
                ...sourceTasks,
                ...selectedTasks.filter(task => !existingIds.has(task.id)),
            ]

            setOrderedTasks(nextTasks)
            queryClient.setQueryData(moduleKeys.tasks(moduleId), nextTasks)

            return { previousTasks }
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: moduleKeys.lists() })
            await queryClient.invalidateQueries({ queryKey: taskKeys.lists() })
            toast.success('Задачи добавлены в модуль')
            setIsModalOpen(false)
        },
        onError: (_error, _selectedTasks, context) => {
            if (context?.previousTasks) {
                setOrderedTasks(context.previousTasks)
                queryClient.setQueryData(moduleKeys.tasks(moduleId), context.previousTasks)
            }
            toast.error('Не удалось добавить задачи')
        },
    })

    const reorderTasksMutation = useMutation({
        mutationFn: (taskIds: number[]) => modulesApi.reorderModuleTasks(moduleId, taskIds),
        onMutate: async taskIds => {
            setIsReorderSyncing(true)
            await queryClient.cancelQueries({ queryKey: moduleKeys.tasks(moduleId) })

            const previousTasks = queryClient.getQueryData<Task[]>(moduleKeys.tasks(moduleId))
            const sourceTasks = orderedTasks.length ? orderedTasks : previousTasks ?? []
            const nextTasks = taskIds
                .map(taskId => sourceTasks.find(task => task.id === taskId))
                .filter((task): task is Task => Boolean(task))

            setOrderedTasks(nextTasks)
            queryClient.setQueryData(moduleKeys.tasks(moduleId), nextTasks)

            return { previousTasks }
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: moduleKeys.lists() })
        },
        onError: (_error, _taskIds, context) => {
            if (context?.previousTasks) {
                setOrderedTasks(context.previousTasks)
                queryClient.setQueryData(moduleKeys.tasks(moduleId), context.previousTasks)
            }
            toast.error('Не удалось сохранить порядок задач')
        },
        onSettled: () => {
            setIsReorderSyncing(false)
        },
    })

    const removeTaskMutation = useMutation({
        mutationFn: (task: Task) => modulesApi.removeModuleTask(moduleId, task.id),
        onMutate: async taskToRemove => {
            await queryClient.cancelQueries({ queryKey: moduleKeys.tasks(moduleId) })

            const previousTasks = queryClient.getQueryData<Task[]>(moduleKeys.tasks(moduleId))
            const sourceTasks = orderedTasks.length ? orderedTasks : previousTasks ?? []
            const nextTasks = sourceTasks.filter(task => task.id !== taskToRemove.id)

            setOrderedTasks(nextTasks)
            queryClient.setQueryData(moduleKeys.tasks(moduleId), nextTasks)

            return { previousTasks }
        },
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: moduleKeys.lists() })
            toast.success('Задача удалена из модуля')
        },
        onError: (_error, _taskToRemove, context) => {
            if (context?.previousTasks) {
                setOrderedTasks(context.previousTasks)
                queryClient.setQueryData(moduleKeys.tasks(moduleId), context.previousTasks)
            }
            toast.error('Не удалось удалить задачу из модуля')
        },
    })

    const createModuleMutation = useMutation({
        mutationFn: modulesApi.createModule,
        onSuccess: async createdModule => {
            setIsEditingModule(false)
            setModuleTitle(createdModule.title)
            setModuleDescription(createdModule.description)
            await queryClient.invalidateQueries({ queryKey: moduleKeys.lists() })
            toast.success('Модуль создан')
            navigate(`/admin/modules/${createdModule.id}`, { replace: true })
        },
    })

    const updateModuleMutation = useMutation({
        mutationFn: () => modulesApi.updateModule(moduleId, {
            title: moduleTitle.trim(),
            description: moduleDescription.trim(),
        }),
        onSuccess: async updatedModule => {
            setModuleTitle(updatedModule.title)
            setModuleDescription(updatedModule.description)
            setIsEditingModule(false)
            setModuleMenuOpen(false)
            await queryClient.invalidateQueries({ queryKey: moduleKeys.detail(moduleId) })
            await queryClient.invalidateQueries({ queryKey: moduleKeys.lists() })
            toast.success('Модуль обновлен')
        },
    })

    const addExistingTasks = (selectedTasks: Task[]) => {
        if (!selectedTasks.length || isNewModule) return
        addTasksMutation.mutate(selectedTasks)
    }

    const openCreateTaskPage = () => {
        if (isNewModule) return
        navigate(`/admin/modules/${moduleId}/tasks/new`)
    }

    const saveModule = () => {
        const title = moduleTitle.trim()
        const description = moduleDescription.trim()

        if (!title || !description) {
            toast.error('Введите название и описание модуля')
            return
        }

        if (isNewModule) {
            createModuleMutation.mutate({ title, description })
            return
        }

        updateModuleMutation.mutate()
    }

    const moduleActionPending = createModuleMutation.isPending || updateModuleMutation.isPending
    const handleDragEnd = ({ active, over }: DragEndEvent) => {
        if (!over || active.id === over.id) return

        const oldIndex = sortedTasks.findIndex(task => task.id === active.id)
        const newIndex = sortedTasks.findIndex(task => task.id === over.id)

        if (oldIndex === -1 || newIndex === -1) return

        const next = arrayMove(sortedTasks, oldIndex, newIndex)
        setOrderedTasks(next)
        reorderTasksMutation.mutate(next.map(task => task.id))
    }

    return (
        <section className="page">
            <Link className="backLink" to="/admin/modules">
                <md-icon>arrow_back</md-icon>
                <span>Вернуться</span>
            </Link>

            <section className={styles.hero}>
                <Artwork seed={module?.id ? `${module.id}-${module.title}` : `${moduleId}-${moduleTitle || 'new'}`} large />
                <div className={styles.heroText}>
                    <div className={styles.moduleHeader}>
                        {isEditingModule ? (
                            <label className={styles.moduleTitleInput}>
                                <input
                                    value={moduleTitle}
                                    onChange={event => setModuleTitle(event.target.value)}
                                    placeholder="Название модуля"
                                />
                            </label>
                        ) : (
                            <h1>{moduleTitle || module?.title || ''}</h1>
                        )}

                        {!isNewModule && !isEditingModule ? (
                            <div className={styles.moduleMenu} ref={moduleMenuRef}>
                                <md-icon-button
                                    type="button"
                                    onClick={() => setModuleMenuOpen(open => !open)}
                                    aria-label="Действия с модулем"
                                >
                                    <md-icon>more_vert</md-icon>
                                </md-icon-button>
                                {moduleMenuOpen ? (
                                    <button
                                        className={styles.moduleMenuItem}
                                        type="button"
                                        onClick={() => {
                                            setIsEditingModule(true)
                                            setModuleMenuOpen(false)
                                        }}
                                    >
                                        Переименовать
                                    </button>
                                ) : null}
                            </div>
                        ) : null}
                    </div>

                    {isEditingModule ? (
                        <label className={styles.moduleDescriptionInput}>
                            <textarea
                                value={moduleDescription}
                                onChange={event => setModuleDescription(event.target.value)}
                                placeholder="Описание модуля"
                                rows={4}
                            />
                        </label>
                    ) : moduleDescription || module?.description ? (
                        <p>{moduleDescription || module?.description}</p>
                    ) : null}
                                            {!isNewModule && (moduleCreatedAt || moduleUpdatedAt) && (
                        <div className={styles.moduleDates}>
                            {moduleCreatedAt && (
                                <div className={styles.dateRow}>
                                    <span>Создан: {moduleCreatedAt}</span>
                                </div>
                            )}
                            {moduleUpdatedAt && moduleUpdatedAt !== moduleCreatedAt && (
                                <div className={styles.dateRow}>
                                    <span>Обновлён: {moduleUpdatedAt}</span>
                                </div>
                            )}
                        </div>
                    )}

                    <div className={styles.heroActions}>
                        {isEditingModule ? (
                            <md-filled-tonal-button type="button" onClick={saveModule} disabled={moduleActionPending || undefined}>
                                Сохранить модуль
                            </md-filled-tonal-button>
                        ) : null}
                        {!isNewModule ? (
                            <md-filled-button type="button" onClick={() => setIsModalOpen(true)}>
                                Добавить задачу
                            </md-filled-button>
                        ) : null}
                    </div>
                </div>
            </section>

            <div className={styles.listTitle}>
                <h2>Список задач</h2>
                <md-icon>arrow_downward</md-icon>
            </div>

            {isLoading ? <div className={styles.state}>Загрузка задач...</div> : null}
            {isError ? <div className={styles.state}>Не удалось загрузить задачи</div> : null}
            {isNewModule ? <div className={styles.state}>Сохраните модуль, чтобы добавлять задачи</div> : null}

            <div className={styles.taskList}>
                {!isLoading && !isError ? (
                    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                        <SortableContext items={sortedTaskIds} strategy={verticalListSortingStrategy}>
                            {sortedTasks.map(task => (
                                <SortableTaskRow
                                    task={task}
                                    moduleId={moduleId}
                                    onUnlink={taskToRemove => removeTaskMutation.mutate(taskToRemove)}
                                    isUnlinking={removeTaskMutation.isPending}
                                    key={task.id}
                                />
                            ))}
                        </SortableContext>
                    </DndContext>
                ) : null}

                {!isLoading && !isError && sortedTasks.length === 0 ? (
                    <div className={styles.state}>Задачи не найдены</div>
                ) : null}
            </div>

            <TaskModal
                moduleTitle={module?.title}
                languages={languages}
                excludedTaskIds={sortedTaskIds}
                isOpen={isModalOpen}
                isSaving={addTasksMutation.isPending}
                onClose={() => setIsModalOpen(false)}
                onAddExisting={addExistingTasks}
                onCreateNew={openCreateTaskPage}
            />
        </section>
    )
}

export default AdminModuleTasksPage
