import { cn } from '../../lib/utils.ts'

interface SkeletonProps {
    className?: string
}

const Skeleton = ({ className }: SkeletonProps) => (
    <div
        className={cn(
            'animate-pulse rounded-md bg-zinc-700/60',
            className
        )}
    />
)

export default Skeleton