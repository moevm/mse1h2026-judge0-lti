import { useState } from 'react'
import { useModules } from '../../hooks/queries/useModules'
import { useModuleTasks } from '../../hooks/queries/useModuleTasks'
import { useTask } from '../../hooks/queries/useTask'
import Skeleton from '../../UI/Skeleton/Skeleton'
import ErrorState from '../../UI/ErrorState/ErrorState'
import { toast } from 'sonner'

type Tab = 'modules' | 'tasks' | 'errors'

// ─── Таб: Модули ─────────────────────────────────────────────────────────────
function ModulesTab() {
    const { data: modules, isLoading, isError, error, refetch } = useModules()

    if (isLoading) return (
        <div className="flex flex-col gap-3">
            {Array.from({ length: 2 }).map((_, i) => (
                <div key={i} className="flex flex-col gap-2 p-4 rounded-xl bg-zinc-800 border border-zinc-700">
                    <Skeleton className="h-5 w-40" />
                    <Skeleton className="h-4 w-64" />
                    <Skeleton className="h-3 w-24 mt-1" />
                </div>
            ))}
        </div>
    )

    if (isError) return <ErrorState message="Не удалось загрузить модули" error={error} onRetry={refetch} />

    return (
        <div className="flex flex-col gap-3">
            {modules?.map(m => (
                <div key={m.id} className="flex flex-col gap-1 p-4 rounded-xl bg-zinc-800 border border-zinc-700 animate-in fade-in duration-300">
                    <div className="flex justify-between items-center">
                        <p className="text-sm font-medium text-zinc-100">{m.title}</p>
                        <span className="text-[10px] font-mono text-zinc-500">ID: {m.id}</span>
                    </div>
                    <p className="text-xs text-zinc-400">{m.description}</p>
                    <p className="text-[10px] text-zinc-500 mt-1">{m.tasks.length} задач</p>
                </div>
            ))}
        </div>
    )
}

// ─── Таб: Задачи ─────────────────────────────────────────────────────────────
function TasksTab() {
    // Модуль 1 — всегда, для простоты демо
    const { data: tasks, isLoading, isError, error, refetch } = useModuleTasks(1)

    if (isLoading) return (
        <div className="flex flex-col gap-3">
            {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex flex-col gap-2 p-4 rounded-xl bg-zinc-800 border border-zinc-700">
                    <Skeleton className="h-5 w-36" />
                    <Skeleton className="h-4 w-56" />
                    <div className="flex gap-2 mt-1">
                        <Skeleton className="h-5 w-16 rounded-full" />
                        <Skeleton className="h-5 w-20 rounded-full" />
                    </div>
                </div>
            ))}
        </div>
    )

    if (isError) return <ErrorState message="Не удалось загрузить задачи" error={error} onRetry={refetch} />

    return (
        <div className="flex flex-col gap-3">
            {tasks?.map(t => (
                <div key={t.id} className="flex flex-col gap-2 p-4 rounded-xl bg-zinc-800 border border-zinc-700 animate-in fade-in duration-300">
                    <div className="flex justify-between items-center">
                        <p className="text-sm font-medium text-zinc-100">{t.title}</p>
                        <span className="text-[10px] font-mono text-zinc-500">⏱ {t.timeout}с</span>
                    </div>
                    <p className="text-xs text-zinc-400">{t.description}</p>
                    <div className="flex gap-1.5 flex-wrap">
                        {t.languages.map(lang => (
                            <span key={lang} className="px-2 py-0.5 rounded-full text-[10px] font-medium
                                                        bg-pink-500/15 text-pink-400 border border-pink-500/30">
                                {lang}
                            </span>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    )
}

// ─── Таб: Ошибки ─────────────────────────────────────────────────────────────
function ErrorsTab() {
    // Несуществующая задача — вызовет 404 и ErrorState (без toast, silent: true)
    const [showBroken, setShowBroken] = useState(false)
    const { isLoading, isError, error } = useTask(showBroken ? 999 : null)
    // refetch здесь не поможет (задача 999 не существует), поэтому
    // onRetry сбрасывает состояние — пользователь может попробовать снова

    return (
        <div className="flex flex-col gap-4">

            {/* Toast */}
            <div className="p-4 rounded-xl bg-zinc-800 border border-zinc-700 flex flex-col gap-3">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Toast</p>
                <div className="flex flex-wrap gap-2">
                    <button onClick={() => toast.success('Готово!')}
                            className="px-3 py-1.5 rounded-lg text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-200 cursor-pointer transition-colors">
                        success
                    </button>
                    <button onClick={() => toast.error('Что-то пошло не так', { description: 'Подробности об ошибке' })}
                            className="px-3 py-1.5 rounded-lg text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-200 cursor-pointer transition-colors">
                        error
                    </button>
                    <button onClick={() => toast.info('Информация')}
                            className="px-3 py-1.5 rounded-lg text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-200 cursor-pointer transition-colors">
                        info
                    </button>
                    <button onClick={() => toast.warning('Осторожно')}
                            className="px-3 py-1.5 rounded-lg text-xs bg-zinc-700 hover:bg-zinc-600 text-zinc-200 cursor-pointer transition-colors">
                        warning
                    </button>
                </div>
            </div>

            {/* Skeleton */}
            <div className="p-4 rounded-xl bg-zinc-800 border border-zinc-700 flex flex-col gap-3">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Skeleton</p>
                <div className="flex flex-col gap-2">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-64" />
                    <Skeleton className="h-4 w-40" />
                </div>
            </div>

            {/* ErrorState — запрос к несуществующей задаче */}
            <div className="p-4 rounded-xl bg-zinc-800 border border-zinc-700 flex flex-col gap-3">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider">ErrorState</p>
                <p className="text-xs text-zinc-500">
                    Запрос к <code className="text-pink-400">GET /tasks/999</code> — 404, без toast
                </p>

                {!showBroken && (
                    <button
                        onClick={() => setShowBroken(true)}
                        className="w-fit px-3 py-1.5 rounded-lg text-xs bg-red-700/40 hover:bg-red-700/60
                                   text-red-300 border border-red-700/50 cursor-pointer transition-colors"
                    >
                        💀 сломать запрос
                    </button>
                )}

                {isLoading && <Skeleton className="h-20 w-full" />}

                {isError && (
                    <ErrorState
                        message="Задача #999 не найдена"
                        error={error ?? undefined}
                        onRetry={() => setShowBroken(false)}
                    />
                )}
            </div>

        </div>
    )
}

// ─── Главная страница ────────────────────────────────────────────────────────
const TABS: { id: Tab; label: string }[] = [
    { id: 'modules', label: 'Модули' },
    { id: 'tasks',   label: 'Задачи' },
    { id: 'errors',  label: 'UI-состояния' },
]

export default function TestPage() {
    const [tab, setTab] = useState<Tab>('modules')

    return (
        <div className="min-h-screen bg-zinc-900 text-white px-4 py-10">
            <div className="max-w-xl mx-auto flex flex-col gap-6">

                <div>
                    <h1 className="text-2xl font-semibold text-zinc-100">🧪 Test page</h1>
                    <p className="text-sm text-zinc-500 mt-1">
                        API · Skeleton · ErrorState · Toast
                    </p>
                </div>

                {/* Табы */}
                <div className="flex gap-1 p-1 rounded-xl bg-zinc-800 border border-zinc-700 w-fit">
                    {TABS.map(t => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer
                                        ${tab === t.id
                                ? 'bg-pink-500 text-white shadow'
                                : 'text-zinc-400 hover:text-zinc-200'}`}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                {/* Контент */}
                {tab === 'modules' && <ModulesTab />}
                {tab === 'tasks'   && <TasksTab />}
                {tab === 'errors'  && <ErrorsTab />}

            </div>
        </div>
    )
}