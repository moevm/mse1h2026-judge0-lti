import { useState } from 'react'
import { useUser } from '../../hooks/queries/useUser'
import { useUsers } from '../../hooks/queries/useUsers.ts'
import Skeleton from '../../UI/Skeleton/Skeleton'
import ErrorState from '../../UI/ErrorState/ErrorState'

// ─── Роль → цвет бейджа ─────────────────────────────────────────────────────
const ROLE_STYLES: Record<string, string> = {
    admin:   'bg-red-500/20 text-red-400 border border-red-500/30',
    teacher: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
    student: 'bg-pink-500/20 text-pink-400 border border-pink-500/30',
}

// ─── Карточка одного пользователя (Skeleton при загрузке) ────────────────────
function UserCard({ userId }: { userId: number }) {
    const { data: user, isLoading, isError, refetch } = useUser(userId)

    if (isLoading) return (
        <div className="flex flex-col gap-3 p-5 rounded-xl bg-zinc-800 border border-zinc-700">
            <div className="flex justify-between">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-3 w-12" />
            </div>
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-4 w-28" />
        </div>
    )

    if (isError) return (
        <ErrorState
            message={`Пользователь #${userId} не найден`}
            onRetry={() => refetch()}
        />
    )

    if (!user) return null

    return (
        <div className="flex flex-col gap-3 p-5 rounded-xl bg-zinc-800 border border-zinc-700
                        shadow-lg animate-in fade-in duration-400">
            <div className="flex justify-between items-center">
                <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider
                                  ${ROLE_STYLES[user.role] ?? 'bg-zinc-700 text-zinc-400'}`}>
                    {user.role}
                </span>
                <span className="text-[10px] text-zinc-500 font-mono">ID: {user.id}</span>
            </div>
            <div>
                <p className="text-[10px] text-zinc-500 uppercase font-bold mb-0.5">Полное имя</p>
                <p className="text-base font-medium text-zinc-100">{user.full_name}</p>
            </div>
            <div>
                <p className="text-[10px] text-zinc-500 uppercase font-bold mb-0.5">Аккаунт</p>
                <p className="text-sm text-pink-400">@{user.username}</p>
            </div>
        </div>
    )
}

// ─── Список всех пользователей (Skeleton при загрузке) ───────────────────────
function UserList() {
    const { data: users, isLoading, isError, refetch } = useUsers()

    if (isLoading) return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex flex-col gap-3 p-5 rounded-xl bg-zinc-800 border border-zinc-700">
                    <div className="flex justify-between">
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-3 w-10" />
                    </div>
                    <Skeleton className="h-5 w-36" />
                    <Skeleton className="h-4 w-24" />
                </div>
            ))}
        </div>
    )

    if (isError) return (
        <ErrorState
            message="Не удалось загрузить список пользователей"
            onRetry={() => refetch()}
        />
    )

    if (!users?.length) return (
        <p className="text-zinc-500 text-sm italic text-center">Пользователи не найдены</p>
    )

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {users.map(user => (
                <div key={user.id}
                     className="flex flex-col gap-2 p-4 rounded-xl bg-zinc-800 border border-zinc-700
                                animate-in fade-in duration-300">
                    <div className="flex justify-between items-center">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider
                                          ${ROLE_STYLES[user.role] ?? 'bg-zinc-700 text-zinc-400'}`}>
                            {user.role}
                        </span>
                        <span className="text-[10px] text-zinc-500 font-mono">ID: {user.id}</span>
                    </div>
                    <p className="text-sm font-medium text-zinc-100">{user.full_name}</p>
                    <p className="text-xs text-pink-400">@{user.username}</p>
                </div>
            ))}
        </div>
    )
}

// ─── Главная страница ────────────────────────────────────────────────────────
export default function TestPage() {
    const [activeTab, setActiveTab] = useState<'single' | 'list'>('single')
    const [userId, setUserId] = useState<number | null>(null)

    const VALID_IDS = [1, 2, 3, 4]

    return (
        <div className="min-h-screen bg-zinc-900 text-white px-4 py-10">
            <div className="max-w-2xl mx-auto flex flex-col gap-8">

                <div>
                    <h1 className="text-2xl font-semibold text-zinc-100">
                        🧪 Тестирование API и обработки ошибок
                    </h1>
                    <p className="text-sm text-zinc-500 mt-1">
                        Демонстрация архитектуры: API layer → Custom Hook → UI states
                    </p>
                </div>

                <div className="flex gap-1 p-1 rounded-xl bg-zinc-800 border border-zinc-700 w-fit">
                    {(['single', 'list'] as const).map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer
                                       ${activeTab === tab
                                ? 'bg-pink-500 text-white shadow'
                                : 'text-zinc-400 hover:text-zinc-200'}`}
                        >
                            {tab === 'single' ? 'Один пользователь' : 'Все пользователи'}
                        </button>
                    ))}
                </div>

                {activeTab === 'single' && (
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-wrap gap-2">
                            {VALID_IDS.map(id => (
                                <button
                                    key={id}
                                    onClick={() => setUserId(id)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
                                               cursor-pointer active:scale-95
                                               ${userId === id
                                        ? 'bg-pink-600 ring-2 ring-pink-400/50 text-white'
                                        : 'bg-zinc-700 hover:bg-zinc-600 text-zinc-200'}`}
                                >
                                    #{id}
                                </button>
                            ))}

                            <button
                                onClick={() => setUserId(999)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
                                           cursor-pointer active:scale-95
                                           ${userId === 999
                                    ? 'bg-red-700 ring-2 ring-red-400/50 text-white'
                                    : 'bg-zinc-700 hover:bg-red-700/50 text-zinc-400 hover:text-red-300'}`}
                            >
                                💀 ID: 999 (ошибка)
                            </button>

                            {userId !== null && (
                                <button
                                    onClick={() => setUserId(null)}
                                    className="px-4 py-2 rounded-lg text-sm text-zinc-500
                                               hover:text-zinc-300 transition-all cursor-pointer"
                                >
                                    Сбросить
                                </button>
                            )}
                        </div>

                        <div className="min-h-30 flex items-center justify-center">
                            {userId === null ? (
                                <p className="text-zinc-500 text-sm italic">
                                    Выберите ID пользователя
                                </p>
                            ) : (
                                <div className="w-full">
                                    <UserCard userId={userId} />
                                </div>
                            )}
                        </div>

                        <div className="rounded-xl border border-zinc-700 bg-zinc-800/50 p-4 text-xs text-zinc-500 font-mono space-y-1">
                            <p className="text-zinc-400 font-sans font-medium text-sm mb-2">Цепочка вызовов:</p>
                            <p>UserCard → <span className="text-pink-400">useUser(id)</span></p>
                            <p>useUser → <span className="text-blue-400">usersApi.getUser(id)</span> + queryKey + options</p>
                            <p>usersApi → <span className="text-green-400">api.get('/users/id', {'{ silent: true }'})</span></p>
                            <p>silent: true → <span className="text-yellow-400">ErrorState показывается, toast — нет</span></p>
                        </div>
                    </div>
                )}

                {activeTab === 'list' && (
                    <div className="flex flex-col gap-4">
                        <p className="text-sm text-zinc-500">
                            Загружает всех пользователей из <code className="text-pink-400 text-xs">/users</code>.
                            При загрузке — Skeleton-сетка, при ошибке — ErrorState с кнопкой повтора.
                        </p>
                        <UserList />
                    </div>
                )}

            </div>
        </div>
    )
}