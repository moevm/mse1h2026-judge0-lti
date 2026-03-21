
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import styles from './IDEPage.module.scss';
import TasksSection from '../../components/TasksSection/TasksSection.tsx';
import ConsoleSection, {
    type ConsoleOutput,
} from '../../components/ConsoleSection/ConsoleSection.tsx';

import Header from '../../components/Header/Header';
import { useCheckSolution } from '../../hooks/queries/useCheckSolution.ts';
import { useState } from 'react';
import { useLanguages } from '../../hooks/queries/useLanguages.ts';
import { mapServerLangToMonaco } from '../../utils/languageMap.ts';

const STORAGE_KEY = 'ide-task-codes';

const IDEPage = () => {
    // Задачи
    const { mutate: checkSolution } = useCheckSolution();
    const [activeTaskId, setActiveTaskId] = useState<number | null>(null);

    // Консоль
    const [consoleOutputs, setConsoleOutputs] = useState<Record<number, ConsoleOutput | null>>({});
    const [consoleTab, setConsoleTab] = useState<'input' | 'output'>('output');

    // Языки
    const { data: languages = [] } = useLanguages();
    const [selectedLanguageId, setSelectedLanguageId] = useState<number | null>(
        languages[0]?.id ?? null
    );

    // Код
    const [codes, setCodes] = useState<Record<number, string>>(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    });
    const currentCode = activeTaskId ? (codes[activeTaskId] ?? '') : '';


    const handleCodeChange = (value: string) => {
        if (!activeTaskId) return;
        setCodes((prev) => {
            const newCodes = { ...prev, [activeTaskId]: value };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(newCodes));
            return newCodes;
        });
    };

    const handleCheck = () => {
        if (!activeTaskId) return;
        const submitted_at = new Date().toISOString();

        const selectedLanguage = languages.find((l) => l.id === selectedLanguageId);
        const langNameForServer = selectedLanguage?.language ?? 'Plain Text';

        checkSolution(
            {
                taskId: activeTaskId,
                code: currentCode,
                language: langNameForServer,
                submitted_at,
            },
            {
                onSuccess: (data) => {
                    setConsoleOutputs((prev) => ({
                        ...prev,
                        [activeTaskId]: data,
                    }));
                    setConsoleTab('output');
                },
            }
        );
    };

    const editorLanguage = mapServerLangToMonaco(
        languages.find((l) => l.id === selectedLanguageId)?.language
    );

    return (
        <div>
            <Header
                selectedLanguageId={selectedLanguageId ?? 0}
                setSelectedLanguageId={setSelectedLanguageId}
                onCheck={handleCheck}
                languages={languages}
            />

            <PanelGroup direction="horizontal">
                <Panel defaultSize={30} minSize={20} maxSize={90} className={styles.editorPanel}>
                    <CodeEditor
                        language={editorLanguage}
                        value={currentCode}
                        onChange={(value) => handleCodeChange(value || '')}
                    />
                </Panel>

                <PanelResizeHandle className={styles.gutterHorizontal} />

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

                        <PanelResizeHandle className={styles.gutterVertical} />

                        <Panel defaultSize={40} minSize={20} maxSize={80}>
                            <div className={styles.rightBottom}>
                                <ConsoleSection
                                    output={
                                        activeTaskId ? (consoleOutputs[activeTaskId] ?? null) : null
                                    }
                                    activeTab={consoleTab}
                                    onTabChange={setConsoleTab}
                                />
                            </div>
                        </Panel>
                    </PanelGroup>
                </Panel>
            </PanelGroup>
        </div>
    );
};

export default IDEPage;

