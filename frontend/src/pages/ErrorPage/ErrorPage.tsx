// src/pages/ErrorPage/ErrorPage.tsx
import { useNavigate } from 'react-router-dom'

interface ErrorPageProps {
    code: number
    title: string
    description: string
    icon: React.ReactNode
}

const ErrorPage = ({ code, title, description, icon }: ErrorPageProps) => {
    const navigate = useNavigate()

    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-[#1e1e1e]">
            <div className="absolute inset-0 flex items-center justify-center select-none pointer-events-none">
                <span className="text-[20rem] font-black text-white/3 leading-none">
                    {code}
                </span>
            </div>

            <div className="relative text-5xl">{icon}</div>

            <div className="relative flex flex-col items-center gap-2 text-center">
                <p className="text-zinc-500 text-sm font-mono">ERROR {code}</p>
                <h1 className="text-4xl font-bold text-white">{title}</h1>
                <p className="text-zinc-400 text-sm mt-1">{description}</p>
            </div>

            <div className="relative flex gap-3">
                <button
                    onClick={() => navigate(-1)}
                    className="px-5 py-2.5 rounded-lg bg-zinc-800 text-zinc-300 text-sm font-medium
                               hover:bg-zinc-700 active:scale-95 transition-all cursor-pointer"
                >
                    ← Назад
                </button>
                <button
                    onClick={() => navigate('/')}
                    className="px-5 py-2.5 rounded-lg bg-pink-600 text-white text-sm font-medium
                               hover:bg-pink-700 active:scale-95 transition-all cursor-pointer"
                >
                    На главную
                </button>
            </div>
        </div>
    )
}

export default ErrorPage