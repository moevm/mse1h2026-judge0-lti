import {Panel, PanelGroup, PanelResizeHandle} from "react-resizable-panels";
import CodeEditor from "../../components/CodeEditor/CodeEditor";
import styles from "./IDEPage.module.scss";
import TasksSection from "../../components/TasksSection/TasksSection.tsx";
import ConsoleSection, {type ConsoleOutput} from "../../components/ConsoleSection/ConsoleSection.tsx";

import Header from "../../components/Header/Header";
import {useCheckSolution} from "../../hooks/queries/useCheckSolution.ts";
import {useState} from "react";

interface IDEPageProps {
    language: string;
    setLanguage: (lang: string) => void;
}

const STORAGE_KEY = "ide-task-codes";

const IDEPage = ({language, setLanguage}: IDEPageProps) => {
    const {mutate: checkSolution} = useCheckSolution();

    const [codes, setCodes] = useState<Record<number, string>>(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    });

    const [activeTaskId, setActiveTaskId] = useState<number | null>(null);
    const [consoleOutput, setConsoleOutput] = useState<ConsoleOutput | null>(null);

    const currentCode = activeTaskId ? codes[activeTaskId] ?? "" : "";

    const handleCodeChange = (value: string) => {
        if (!activeTaskId) return;

        setCodes(prev => {
            const newCodes = {
                ...prev,
                [activeTaskId]: value
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(newCodes));
            return newCodes;
        });
    };

    const handleCheck = () => {
        if (!activeTaskId) return;

        const submitted_at = new Date().toISOString();

        checkSolution(
            {
                taskId: activeTaskId,
                code: currentCode,
                language,
                submitted_at
            },
            {
                onSuccess: (data) => {
                    setConsoleOutput(data);
                },
            }
        );
    };

    return (
        <div>
            <Header language={language} setLanguage={setLanguage} onCheck={handleCheck}/>

            <PanelGroup direction="horizontal">
                <Panel defaultSize={30} minSize={20} maxSize={90} className={styles.editorPanel}>
                    <CodeEditor
                        language={language}
                        value={currentCode}
                        onChange={(value) => handleCodeChange(value || "")}
                    />
                </Panel>

                <PanelResizeHandle className={styles.gutterHorizontal}/>

                <Panel defaultSize={30} minSize={10} maxSize={80}>
                    <PanelGroup direction="vertical">
                        <Panel defaultSize={60} minSize={20} maxSize={80}>
                            <div className={styles.rightTop}>
                                <TasksSection
                                    moduleId={1}
                                    activeTaskId={activeTaskId}
                                    setActiveTaskId={setActiveTaskId}
                                />
                            </div>
                        </Panel>

                        <PanelResizeHandle className={styles.gutterVertical}/>

                        <Panel defaultSize={40} minSize={20} maxSize={80}>
                            <div className={styles.rightBottom}>
                                <ConsoleSection output={consoleOutput}/>
                            </div>
                        </Panel>
                    </PanelGroup>
                </Panel>
            </PanelGroup>
        </div>
    );
};

export default IDEPage;