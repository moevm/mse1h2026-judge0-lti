import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDebounce } from 'use-debounce'
import { toast } from 'sonner'
import { useUsers, useUpdateUser } from '../../hooks/queries/useUsers'
import type { User, UserUpdateRequest } from '../../api/users.api'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminStudentsPage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

// Локальный интерфейс фильтров
interface FilterValues {
    [key: string]: string | undefined
    role?: string
    include_deleted?: string
    created_from?: string
    created_to?: string
    solved_min?: string
    solved_max?: string
    sort_by?: string
    sort_order?: string
}

const roleLabel: Record<string, string> = {
    admin: 'Админ',
    teacher: 'Преподаватель',
    student: 'Студент',
}

// Группы фильтров для страницы студентов
const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'role',
        title: 'Роль',
        fields: [
            {
                id: 'role',
                label: 'Роль',
                type: 'select',
                options: [
                    { value: '', label: 'Все' },
                    { value: 'admin', label: 'Админ' },
                    { value: 'teacher', label: 'Преподаватель' },
                    { value: 'student', label: 'Студент' },
                ],
            },
        ],
    },
    {
        id: 'deleted',
        title: 'Удаленные',
        fields: [
            {
                id: 'include_deleted',
                label: 'Показывать удаленных',
                type: 'select',
                options: [
                    { value: '', label: 'Нет' },
                    { value: 'true', label: 'Да' },
                ],
            },
        ],
    },
    {
        id: 'dates',
        title: 'Дата регистрации',
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
        id: 'solved',
        title: 'Решенные задачи',
        fields: [
            {
                id: 'solved_min',
                label: 'Мин. решено',
                type: 'number',
                min: 0,
                placeholder: 'от',
            },
            {
                id: 'solved_max',
                label: 'Макс. решено',
                type: 'number',
                min: 0,
                placeholder: 'до',
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
                    { value: 'full_name', label: 'ФИО' },
                    { value: 'username', label: 'Нику' },
                    { value: 'solved_count', label: 'Решенным задачам' },
                    { value: 'created_at', label: 'Дате регистрации' },
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

const AdminStudentsPage = () => {
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'full_name',
        sort_order: 'asc',
    })
    const [editingUser, setEditingUser] = useState<User | null>(null)
    const [editForm, setEditForm] = useState<UserUpdateRequest>({})

    // Получаем всех пользователей (без фильтрации на бэке)
    const { data: allUsers = [], isLoading, isError } = useUsers({})

    // Фильтрация и сортировка на фронте
    const getFilteredUsers = () => {
        let result = [...allUsers]

        // Поиск по имени или нику
        if (debouncedSearch) {
            result = result.filter(user =>
                user.full_name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
                user.username.toLowerCase().includes(debouncedSearch.toLowerCase())
            )
        }

        // Фильтр по роли
        if (filters.role && filters.role !== '') {
            result = result.filter(user => user.role === filters.role)
        }

        // Фильтр по удаленным
        if (filters.include_deleted !== 'true') {
            result = result.filter(user => user.deleted_at === null)
        }

        // Фильтр по дате регистрации
        if (filters.created_from && filters.created_from !== '') {
            const fromDate = new Date(filters.created_from as string)
            result = result.filter(user => new Date(user.created_at) >= fromDate)
        }
        if (filters.created_to && filters.created_to !== '') {
            const toDate = new Date(filters.created_to as string)
            result = result.filter(user => new Date(user.created_at) <= toDate)
        }

        // Фильтр по количеству решенных задач
        if (filters.solved_min && filters.solved_min !== '') {
            const minValue = Number(filters.solved_min)
            result = result.filter(user => user.solved_count >= minValue)
        }
        if (filters.solved_max && filters.solved_max !== '') {
            const maxValue = Number(filters.solved_max)
            result = result.filter(user => user.solved_count <= maxValue)
        }

        // Сортировка
        const sortBy = filters.sort_by as string || 'full_name'
        const sortOrder = filters.sort_order as string || 'asc'

        result.sort((a, b) => {
            let valA: any = a[sortBy as keyof typeof a]
            let valB: any = b[sortBy as keyof typeof b]

            if (sortBy === 'full_name' || sortBy === 'username') {
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

    const users = getFilteredUsers()
    const filterGroups = getFilterGroups()

    const updateUser = useUpdateUser()

    const handleEditClick = (user: User) => {
        setEditingUser(user)
        setEditForm({ full_name: user.full_name, role: user.role })
    }

    const handleEditSave = async () => {
        if (!editingUser) return
        try {
            await updateUser.mutateAsync({ userId: editingUser.id, payload: editForm })
            toast.success('Пользователь обновлён')
            setEditingUser(null)
        } catch {
            toast.error('Ошибка при обновлении')
        }
    }

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({
            ...prev,
            [fieldId]: value !== undefined ? String(value) : undefined
        }))
    }

    return (
        <div className="page">
            <md-icon className={styles.profileIcon}>account_circle</md-icon>

            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={filterGroups}
                filterValues={filters}
                onFilterChange={handleFilterChange}
                placeholder="Поиск по имени или нику..."
                variant="page"
                showFilters={true}
            />

            {isLoading && (
                <div className={styles.state}>
                    <Spinner />
                </div>
            )}

            {isError && (
                <div className={styles.state}>
                    <md-icon>error</md-icon>
                    <span>Не удалось загрузить пользователей</span>
                </div>
            )}

            {!isLoading && !isError && (
                <div className={styles.tableWrapper}>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th></th>
                                <th>Пользователи</th>
                                <th>Роль</th>
                                <th>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr
                                    key={user.id}
                                    onClick={() => navigate(`/admin/students/${user.id}`)}
                                >
                                    <td className={styles.avatar}>
                                        <div className={styles.avatarCircle}>
                                            {user.full_name[0]?.toUpperCase()}
                                        </div>
                                    </td>
                                    <td className={styles.info}>
                                        <span className={styles.name}>{user.full_name}</span>
                                        <span className={styles.meta}>
                                            @{user.username} · {user.solved_count} задач решено
                                        </span>
                                    </td>
                                    <td className={styles.role}>
                                        <span className={styles.roleTag}>
                                            {roleLabel[user.role] ?? user.role}
                                        </span>
                                    </td>
                                    <td className={styles.actions} onClick={e => e.stopPropagation()}>
                                        <button
                                            className={styles.editBtn}
                                            onClick={() => handleEditClick(user)}
                                        >
                                            Ред.
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {users.length === 0 && (
                        <div className={`${styles.state} ${styles.notFoundUsers}`}>
                            <span>Пользователи не найдены</span>
                        </div>
                    )}
                </div>
            )}

            {editingUser && (
                <div className={styles.modalOverlay} onClick={() => setEditingUser(null)}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <h2>Редактировать пользователя</h2>
                        <label className={styles.field}>
                            <span>ФИО</span>
                            <input
                                value={editForm.full_name ?? ''}
                                onChange={e => setEditForm(f => ({ ...f, full_name: e.target.value }))}
                            />
                        </label>
                        <label className={styles.field}>
                            <span>Роль</span>
                            <select
                                value={editForm.role ?? ''}
                                onChange={e => setEditForm(f => ({ ...f, role: e.target.value as User['role'] }))}
                            >
                                <option value="student">Студент</option>
                                <option value="teacher">Преподаватель</option>
                                <option value="admin">Админ</option>
                            </select>
                        </label>
                        <div className={styles.modalActions}>
                            <button className={styles.cancelBtn} onClick={() => setEditingUser(null)}>
                                Отмена
                            </button>
                            <button
                                className={styles.saveBtn}
                                onClick={handleEditSave}
                                disabled={updateUser.isPending}
                            >
                                {updateUser.isPending ? 'Сохранение...' : 'Сохранить'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AdminStudentsPage
