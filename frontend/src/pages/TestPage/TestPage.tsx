import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LineWave } from 'react-loader-spinner'
import { userKeys } from '../../lib/query-keys'
import api from '../../lib/api'

const fetchUser = async (id: number) => {
    const r = await api.get(`/users/${id}`)
    return r.data
}

// Спиннер — переиспользуемый компонент
const Spinner = ({ showLabel = false }: { showLabel?: boolean }) => (
    <div className="flex flex-col items-center gap-1">
        <LineWave color="#FF1493" height={80} width={80} visible={true} />
        {showLabel && (
            <span className="text-sm" style={{ color: '#FF1493' }}>
                Загрузка
            </span>
        )}
    </div>
)

export default function TestPage() {
    const [userId, setUserId] = useState<number | null>(null)

    const { data, isLoading, isError } = useQuery({
        queryKey: userKeys.detail(userId ?? 0),
        queryFn: () => fetchUser(userId!),
        enabled: userId !== null,   // запрос только после нажатия кнопки
        staleTime: 1500,
        retry: false,
    })

    return (
        <div className="flex flex-col items-center gap-6 p-10">
            <h1 className="text-2xl font-semibold text-white">Тестовая страница</h1>

            {/* Кнопки */}
            <div className="flex gap-3">
                {[1, 2, 3].map(id => (
                    <button
                        key={id}
                        onClick={() => setUserId(id)}
                        className="px-4 py-2 rounded-lg bg-pink-500 text-white text-sm font-medium
                                   hover:bg-pink-600 active:scale-95 transition-all cursor-pointer"
                    >
                        Загрузить #{id}
                    </button>
                ))}

                {/* Кнопка которая точно даст ошибку */}
                <button
                    onClick={() => setUserId(999)}
                    className="px-4 py-2 rounded-lg bg-zinc-700 text-white text-sm font-medium
                               hover:bg-zinc-600 active:scale-95 transition-all cursor-pointer"
                >
                    Сломать запрос
                </button>
            </div>

            {/* Состояния */}
            {userId === null && (
                <p className="text-zinc-500 text-sm">Нажми кнопку чтобы загрузить пользователя</p>
            )}

            {isLoading && <Spinner showLabel />}

            {!isLoading && !isError && data && (
                <div className="flex flex-col gap-2 p-6 rounded-xl bg-zinc-800 text-white min-w-64">
                    <p><span className="text-zinc-400">Имя:</span> {data.name}</p>
                    <p><span className="text-zinc-400">Email:</span> {data.email}</p>
                    <p><span className="text-zinc-400">Город:</span> {data?.address?.city}</p>
                </div>
            )}
        </div>
    )
}