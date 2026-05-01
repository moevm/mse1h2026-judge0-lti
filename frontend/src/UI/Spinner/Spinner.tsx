import { LineWave } from 'react-loader-spinner'

interface SpinnerProps {
    showLabel?: boolean
    color?: string
}

const Spinner = ({ showLabel = false, color = '#8B5CF6' }: SpinnerProps) => (
    <div className="flex flex-col items-center gap-1">
        <LineWave color={color} height={80} width={80} visible={true} />
        {showLabel && (
            <span className="text-sm" style={{ color }}>
                Загрузка
            </span>
        )}
    </div>
)

export default Spinner