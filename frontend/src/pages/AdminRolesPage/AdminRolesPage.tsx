import { useState } from 'react'
import { useDebounce } from 'use-debounce'
import { toast } from 'sonner'
import { useUsers, useUpdateUser, useDeleteUser } from '../../hooks/queries/useUsers'
import type { User, UserUpdateRequest, UsersFilter } from '../../api/users.api'
import AdminToolbar from '../../components/AdminToolbar/AdminToolbar'
import type { FilterGroup } from '../../components/FilterDialog/FilterDialog'
import styles from './AdminRolesPage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'
import ConfirmModal from '../../UI/ConfirmModal/ConfirmModal'

interface FilterValues {
    [key: string]: string | undefined
    role?: string
    include_deleted?: string
    sort_by?: string
    sort_order?: string
}

const roleLabel: Record<string, string> = {
    admin: 'Админ',
    teacher: 'Преподаватель',
    student: 'Студент',
}

const roleOptions = [
    { value: '', label: 'Все роли' },
    { value: 'admin', label: 'Админ' },
    { value: 'teacher', label: 'Преподаватель' },
    { value: 'student', label: 'Студент' },
]

const getFilterGroups = (): FilterGroup[] => [
    {
        id: 'role',
        title: 'Роль',
        fields: [
            {
                id: 'role',
                label: 'Роль пользователя',
                type: 'select',
                options: roleOptions,
            },
        ],
    },
    {
        id: 'deleted',
        title: 'Статус',
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

const AdminRolesPage = () => {
    const [search, setSearch] = useState('')
    const [debouncedSearch] = useDebounce(search, 400)
    const [filters, setFilters] = useState<FilterValues>({
        sort_by: 'full_name',
        sort_order: 'asc',
    })
    const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set())
    const [editingUser, setEditingUser] = useState<User | null>(null)
    const [editForm, setEditForm] = useState<UserUpdateRequest>({})
    const [deletingUser, setDeletingUser] = useState<User | null>(null)
    const [bulkAction, setBulkAction] = useState<'delete' | null>(null)
    const [bulkRole, setBulkRole] = useState<string>('')

    const queryFilters: UsersFilter = {
        search: debouncedSearch || undefined,
        role: (filters.role as 'admin' | 'teacher' | 'student') || undefined,
        include_deleted: filters.include_deleted === 'true' ? true : undefined,
    }

    const { data: users = [], isLoading, isError, refetch } = useUsers(queryFilters)
    const updateUser = useUpdateUser()
    const deleteUser = useDeleteUser()

    const handleSelectAll = () => {
        if (selectedUsers.size === users.length) {
            setSelectedUsers(new Set())
        } else {
            setSelectedUsers(new Set(users.map(u => u.id)))
        }
    }

    const handleSelectUser = (userId: number) => {
        const newSet = new Set(selectedUsers)
        if (newSet.has(userId)) {
            newSet.delete(userId)
        } else {
            newSet.add(userId)
        }
        setSelectedUsers(newSet)
    }

    const handleEditClick = (user: User) => {
        setEditingUser(user)
        setEditForm({ role: user.role })
    }

    const handleEditSave = async () => {
        if (!editingUser) return
        try {
            await updateUser.mutateAsync({ userId: editingUser.id, payload: editForm })
            toast.success('Роль пользователя обновлена')
            setEditingUser(null)
            refetch()
        } catch {
            toast.error('Ошибка при обновлении')
        }
    }

    const handleDeleteClick = (user: User) => {
        setDeletingUser(user)
    }

    const handleConfirmDelete = async () => {
        if (!deletingUser) return
        try {
            await deleteUser.mutateAsync(deletingUser.id)
            toast.success('Пользователь удалён')
            setDeletingUser(null)
            setSelectedUsers(new Set())
            refetch()
        } catch {
            toast.error('Ошибка при удалении')
        }
    }

    const handleBulkDelete = async () => {
        if (selectedUsers.size === 0) return
        try {
            for (const userId of selectedUsers) {
                await deleteUser.mutateAsync(userId)
            }
            toast.success(`Удалено ${selectedUsers.size} пользователей`)
            setSelectedUsers(new Set())
            setBulkAction(null)
            refetch()
        } catch {
            toast.error('Ошибка при массовом удалении')
        }
    }

    const handleBulkRoleChange = async () => {
        if (selectedUsers.size === 0 || !bulkRole) return
        try {
            for (const userId of selectedUsers) {
                await updateUser.mutateAsync({ userId, payload: { role: bulkRole as User['role'] } })
            }
            toast.success(`Роль обновлена у ${selectedUsers.size} пользователей`)
            setSelectedUsers(new Set())
            setBulkAction(null)
            setBulkRole('')
            refetch()
        } catch {
            toast.error('Ошибка при массовом изменении роли')
        }
    }

    const handleFilterChange = (fieldId: string, value: string | number | undefined) => {
        setFilters((prev: FilterValues) => ({ ...prev, [fieldId]: value !== undefined ? String(value) : undefined }))
        setSelectedUsers(new Set())
    }

    return (
        <div className="page">
            <md-icon className={styles.profileIcon}>admin_panel_settings</md-icon>

            <AdminToolbar
                search={search}
                onSearchChange={setSearch}
                filterGroups={getFilterGroups()}
                filterValues={filters}
                onFilterChange={handleFilterChange}
                placeholder="Поиск по имени или нику..."
                variant="page"
                showFilters={true}
            />

            {selectedUsers.size > 0 && (
                <div className={styles.bulkBar}>
                    <span className={styles.bulkInfo}>Выбрано: {selectedUsers.size}</span>
                    <div className={styles.bulkActions}>
                        <select
                            className={styles.bulkRoleSelect}
                            value={bulkRole}
                            onChange={e => setBulkRole(e.target.value)}
                        >
                            <option value="">Изменить роль</option>
                            <option value="student">Студент</option>
                            <option value="teacher">Преподаватель</option>
                            <option value="admin">Админ</option>
                        </select>
                        <button
                            className={styles.bulkApplyBtn}
                            onClick={handleBulkRoleChange}
                            disabled={!bulkRole}
                        >
                            Применить
                        </button>
                        <button
                            className={styles.bulkDeleteBtn}
                            onClick={() => setBulkAction('delete')}
                        >
                            Удалить выбранных
                        </button>
                    </div>
                </div>
            )}

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
                                <th className={styles.checkboxColumn}>
                                    <input
                                        type="checkbox"
                                        className={styles.checkbox}
                                        checked={selectedUsers.size === users.length && users.length > 0}
                                        onChange={handleSelectAll}
                                    />
                                </th>
                                <th className={styles.avatarColumn}></th>
                                <th>Пользователь</th>
                                <th className={styles.roleColumn}>Текущая роль</th>
                                <th className={styles.actionsColumn}>Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td className={styles.checkboxColumn}>
                                        <input
                                            type="checkbox"
                                            className={styles.checkbox}
                                            checked={selectedUsers.has(user.id)}
                                            onChange={() => handleSelectUser(user.id)}
                                        />
                                    </td>
                                    <td className={styles.avatarColumn}>
                                        <div className={styles.avatarCircle}>
                                            {user.full_name[0]?.toUpperCase()}
                                        </div>
                                    </td>
                                    <td className={styles.infoColumn}>
                                        <span className={styles.name}>{user.full_name}</span>
                                        <span className={styles.meta}>@{user.username}</span>
                                        {user.deleted_at && <span className={styles.deletedBadge}>Удалён</span>}
                                    </td>
                                    <td className={styles.roleColumn}>
                                        <span className={`${styles.roleTag} ${styles[user.role]}`}>
                                            {roleLabel[user.role] ?? user.role}
                                        </span>
                                    </td>
                                    <td className={styles.actionsColumn}>
                                        <div className={styles.actions}>
                                            <button
                                                className={styles.editBtn}
                                                onClick={() => handleEditClick(user)}
                                            >
                                                <md-icon>edit</md-icon>
                                            </button>
                                            <button
                                                className={styles.deleteBtn}
                                                onClick={() => handleDeleteClick(user)}
                                            >
                                                <md-icon>delete</md-icon>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {users.length === 0 && (
                        <div className={styles.empty}>
                            <span>Пользователи не найдены</span>
                        </div>
                    )}
                </div>
            )}

            {editingUser && (
                <div className={styles.modalOverlay} onClick={() => setEditingUser(null)}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <h2>Изменение роли</h2>
                        <div className={styles.userInfo}>
                            <div className={styles.userAvatar}>
                                {editingUser.full_name[0]?.toUpperCase()}
                            </div>
                            <div>
                                <div className={styles.userName}>{editingUser.full_name}</div>
                                <div className={styles.userUsername}>@{editingUser.username}</div>
                            </div>
                        </div>
                        <label className={styles.field}>
                            <span>Новая роль</span>
                            <select
                                value={editForm.role ?? editingUser.role}
                                onChange={e => setEditForm(f => ({ ...f, role: e.target.value as User['role'] }))}
                            >
                                <option value="student">Студент</option>
                                <option value="teacher">Преподаватель</option>
                                <option value="admin">Администратор</option>
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

            <ConfirmModal
                isOpen={!!deletingUser}
                title="Удаление пользователя"
                message={`Вы уверены, что хотите удалить пользователя ${deletingUser?.full_name}?`}
                confirmText="Удалить"
                cancelText="Отмена"
                confirmVariant="danger"
                isLoading={deleteUser.isPending}
                onConfirm={handleConfirmDelete}
                onCancel={() => setDeletingUser(null)}
            />

            <ConfirmModal
                isOpen={bulkAction === 'delete'}
                title="Массовое удаление"
                message={`Вы уверены, что хотите удалить ${selectedUsers.size} пользователей?`}
                confirmText="Удалить"
                cancelText="Отмена"
                confirmVariant="danger"
                isLoading={deleteUser.isPending}
                onConfirm={handleBulkDelete}
                onCancel={() => setBulkAction(null)}
            />
        </div>
    )
}

export default AdminRolesPage
