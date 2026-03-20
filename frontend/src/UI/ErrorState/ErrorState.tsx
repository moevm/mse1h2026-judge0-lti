import type { AxiosError } from 'axios'
import errorIcon from '../../assets/icons/error_circle.svg'

interface ErrorStateProps {
    message?: string
    error?: AxiosError<{ detail?: string }>
    onRetry?: () => void
}

const ErrorState = ({
                        message = 'Что-то пошло не так',
                        error,
                        onRetry,
                    }: ErrorStateProps) => {
    const status = error?.response?.status
    const detail = error?.response?.data?.detail

    return (
        <div className="
            flex flex-col items-center gap-3 p-6 text-center
            rounded-xl
            bg-zinc-800/60
            border border-zinc-700/40
            border-t-zinc-600/70
            shadow-[0_1px_2px_rgba(0,0,0,0.2),0_4px_20px_rgba(0,0,0,0.35)]
        ">
            {/* Иконка + код ошибки в одну строку */}
            <div className="flex items-center gap-2">
                <img src={errorIcon} width={20} height={20} alt="" />
                {status && (
                    <span className="text-sm font-mono font-medium text-[#f87171]">
                        HTTP {status}
                    </span>
                )}
            </div>

            {/* Основное сообщение */}
            <p className="text-sm text-zinc-400 leading-relaxed">{message}</p>

            {/* Detail с бэкенда */}
            {detail && detail !== message && (
                <div className="
                    w-full text-left px-3 py-2
                    rounded-lg
                    bg-zinc-900/60
                    border border-zinc-700/40
                    shadow-[inset_0_1px_4px_rgba(0,0,0,0.4)]
                ">
                    <p className="text-xs text-zinc-500 mb-1">detail</p>
                    <p className="text-sm text-zinc-400">{detail}</p>
                </div>
            )}

            {onRetry && (
                <button
                    onClick={onRetry}
                    className="
                        mt-1 px-4 py-1.5 text-sm text-zinc-300
                        rounded-md
                        border border-zinc-600/50
                        hover:bg-zinc-700/50 hover:text-white
                        active:scale-95 transition-all cursor-pointer
                    "
                >
                    Попробовать снова
                </button>
            )}
        </div>
    )
}

export default ErrorState