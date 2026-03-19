interface ErrorStateProps {
    message?: string
    onRetry?: () => void
}

const ErrorState = ({ message = 'Что-то пошло не так', onRetry }: ErrorStateProps) => (
    <div className="
        flex flex-col items-center gap-3 p-6 text-center
        rounded-xl
        bg-zinc-800/60
        border border-zinc-700/40
        border-t-zinc-600/70
        shadow-[0_1px_2px_rgba(0,0,0,0.2),0_4px_20px_rgba(0,0,0,0.35)]
    ">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="#f87171" strokeWidth="1.5"/>
            <line x1="12" y1="7" x2="12" y2="13" stroke="#f87171" strokeWidth="1.5" strokeLinecap="round"/>
            <circle cx="12" cy="16.5" r="0.75" fill="#f87171"/>
        </svg>

        <p className="text-sm text-zinc-400 leading-relaxed">{message}</p>

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

export default ErrorState