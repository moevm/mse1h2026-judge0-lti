import Skeleton from "../Skeleton/Skeleton.tsx";
import styles from "./TasksLoading.module.scss";

const TasksLoading = () => {
    return (
        <div className="flex flex-col gap-4">

            <div className="flex gap-2">
                {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton
                        key={i}
                        className="h-8 w-24 rounded-lg"
                    />
                ))}
            </div>

            <div className={`flex flex-col gap-3 p-4 rounded-xl border border-zinc-700 ${styles.skeletonBlock}`}>

                <Skeleton className="h-6 w-3/4 rounded-md" />

                <div className="flex flex-col gap-1">
                    <Skeleton className="h-4 w-full rounded-md" />
                    <Skeleton className="h-4 w-5/6 rounded-md" />
                    <Skeleton className="h-4 w-2/3 rounded-md" />
                </div>


                <div className="flex flex-col gap-2 mt-2">
                    <Skeleton className="h-5 w-1/4 rounded-md" />

                    <div className="flex flex-col gap-2">
                        <Skeleton className="h-16 w-full rounded-md" />
                        <Skeleton className="h-16 w-full rounded-md" />
                    </div>
                </div>

            </div>

        </div>
    );
};

export default TasksLoading;