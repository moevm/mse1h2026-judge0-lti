import {useEffect} from "react";
import styles from "./TasksSection.module.scss";
import {useModuleTasks} from "../../hooks/queries/useModuleTasks";
import ErrorState from "../../UI/ErrorState/ErrorState";
import TasksLoading from "../../UI/TasksLoading/TasksLoading.tsx";
import type {Task} from "../../api/modules.api.ts";

interface Props {
    moduleId: number;
    activeTaskId: number | null;
    setActiveTaskId: (id: number) => void;
    onTaskChange?: (task: Task | null) => void;
}

const TasksSection = ({moduleId, activeTaskId, setActiveTaskId, onTaskChange}: Props) => {
    const {data: tasks, isLoading, isError, refetch} = useModuleTasks(moduleId);

    useEffect(() => {
        if (tasks?.length && activeTaskId === null) {
            setActiveTaskId(tasks[0].id);
        }
    }, [tasks, activeTaskId, setActiveTaskId]);

    const activeTask =
        tasks?.find((task) => task.id === activeTaskId) ?? tasks?.[0];
    useEffect(() => {
        if (activeTask && onTaskChange) {
            onTaskChange(activeTask);
        } else if (!activeTask && onTaskChange) {
            onTaskChange(null);
        }
    }, [activeTask, onTaskChange]);
    if (isLoading) {
        return <TasksLoading/>;
    }

    if (isError) {
        return (
            <ErrorState
                message="Не удалось загрузить задачи"
                onRetry={refetch}
            />
        );
    }

    if (!tasks?.length) {
        return <div className={styles.tasksSection}>Нет задач</div>;
    }

    return (
        <div className={styles.tasksSection}>
            <div className={styles.tabs}>
                {tasks.map((task, index) => (
                    <button
                        key={task.id}
                        className={`${styles.tab} ${
                            activeTaskId === task.id ? styles.active : ""
                        }`}
                        onClick={() => setActiveTaskId(task.id)}
                    >
                        Задача {index + 1}
                    </button>
                ))}
            </div>

            <div className={styles.tabContent}>
                <h5 className={`${styles.taskStatementText} ${styles.tabContentText}`}>
                    Формулировка задания
                </h5>
                <p>{activeTask?.description}</p>
            </div>
        </div>
    );
};

export default TasksSection;