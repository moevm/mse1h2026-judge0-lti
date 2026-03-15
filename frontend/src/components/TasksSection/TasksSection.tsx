import {useState} from "react";
import styles from "./TasksSection.module.scss";

interface Task {
    id: number;
    title: string;
    content: string;
    examples: string[]; // просто текст
}

const tasks: Task[] = [
    {
        id: 1,
        title: "Сумма чисел",
        content: "Напишите программу, которая принимает два числа и выводит их сумму.",
        examples: [
            "Ввод:\n2 3\nВывод:\n5",
            "Ввод:\n10 15\nВывод:\n25",
        ],
    },
    {
        id: 2,
        title: "Проверка на четность",
        content: "Программа получает число и выводит 'YES', если оно чётное, и 'NO', если нечётное.",
        examples: [
            "Ввод:\n4\nВывод:\nYES",
            "Ввод:\n7\nВывод:\nNO",
        ],
    },
    {
        id: 3,
        title: "Обратная строка",
        content: "На вход подается строка, на выходе нужно вывести её в обратном порядке.",
        examples: [
            "Ввод:\nhello\nВывод:\nolleh",
            "Ввод:\nworld\nВывод:\ndlrow",
        ],
    },
];

const TasksSection = () => {
    const [activeTab, setActiveTab] = useState<number>(tasks[0].id);

    const activeTask = tasks.find((task) => task.id === activeTab);

    return (
        <div className={styles.tasksSection}>
            <div className={styles.tabs}>
                {tasks.map((task, index) => (
                    <button
                        key={task.id}
                        className={`${styles.tab} ${activeTab === task.id ? styles.active : ""}`}
                        onClick={() => setActiveTab(task.id)}
                    >
                        Задача {index + 1}
                    </button>
                ))}
            </div>


            <div className={styles.tabContent}>
                <h5 className={`${styles.taskStatementText} ${styles.tabContentText}`}>Формулировка задания</h5>
                <p>{activeTask?.content}</p>

                <h5 className={`${styles.taskExampleText} ${styles.tabContentText}`}>Примеры ввода/вывода</h5>
                <div className={styles.exampleBlock}>
                    {activeTask?.examples.map((ex, index) => (
                        <pre key={index} className={styles.example}>
                            {ex}
                        </pre>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TasksSection;