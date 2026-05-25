import {Panel, PanelGroup, PanelResizeHandle} from 'react-resizable-panels';
import CodeEditor from '../../components/CodeEditor/CodeEditor';
import styles from './IDEPage.module.scss';
import TasksSection from '../../components/TasksSection/TasksSection.tsx';
import ConsoleSection, {
    type ConsoleOutput,
} from '../../components/ConsoleSection/ConsoleSection.tsx';

import Header from '../../components/Header/Header';
import {useCheckSolution} from '../../hooks/queries/useCheckSolution.ts';
import {useRunSolution} from '../../hooks/queries/useRunSolution.ts';
import {useEffect, useState} from 'react';
import {mapServerLangToMonaco} from '../../utils/languageMap.ts';
import type {Task} from '../../api/modules.api';
import {useSearchParams} from "react-router-dom";
import { useFinishModuleSession, useModuleSession } from '../../hooks/queries/useModuleSession.ts';
import { useAuth } from '../../hooks/queries/useAuth.ts';
import { useCheckAttempts } from '../../hooks/queries/useCheckAttempts.ts';

const STORAGE_KEY = 'ide-task-codes';

const IDEPage = () => {
    const [searchParams] = useSearchParams();
    const moduleId = Number(searchParams.get('module_id'));

    const { data: sessionData } = useModuleSession(moduleId);
    const { mutate: finishSession, isPending: isFinishingSession } = useFinishModuleSession();
    
    // Таймер
    const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
    const [isSessionExpired, setIsSessionExpired] = useState(false);
    const [sessionEndReason, setSessionEndReason] = useState<'manual' | 'expired' | null>(null);

    // Задачи
    const {mutate: checkSolution, isPending: isChecking} = useCheckSolution();
    const [activeTaskId, setActiveTaskId] = useState<number | null>(null);
    const [currentTask, setCurrentTask] = useState<Task | null>(null);

    // Попытки
    const { data: attemptsData, refetch: refetchAttempts } = useCheckAttempts(activeTaskId);

    // Запуск решения 
    const {mutate: runSolution, isPending: isRunning} = useRunSolution();

    // Консоль
    const [consoleOutputs, setConsoleOutputs] = useState<Record<number, ConsoleOutput | null>>({});
    const [consoleTab, setConsoleTab] = useState<'input' | 'output'>('output');

    // stdin
    const [stdinValue, setStdinValue] = useState<string | null>(null);

    // Языки
    const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
    const availableLanguages = currentTask?.languages || [];

    const handleTaskChange = (task: Task | null) => {
        setCurrentTask(task);
        if (task?.languages && task.languages.length > 0) {
            setSelectedLanguage(task.languages[0]);
        } else {
            setSelectedLanguage(null);
        }
    };

    useEffect(() => {
        if (activeTaskId) {
            refetchAttempts();
        }
    }, [activeTaskId, refetchAttempts]);

    const handleStdinChange = (value: string | null) => {
        setStdinValue(value);
    };

    // Код
    const [codes, setCodes] = useState<Record<number, string>>(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    });
    const currentCode = activeTaskId ? (codes[activeTaskId] ?? '') : '';

    const handleCodeChange = (value: string) => {
        if (!activeTaskId) return;
        setCodes((prev) => {
            const newCodes = {...prev, [activeTaskId]: value};
            localStorage.setItem(STORAGE_KEY, JSON.stringify(newCodes));
            return newCodes;
        });
    };

    // По нажатию "Запустить"
    const handleRun = () => {
        if (!activeTaskId || !currentTask) return;
        const submitted_at = new Date().toISOString();

        console.log(stdinValue ?? '');

        const langNameForServer = selectedLanguage ?? 'Plain Text';

        runSolution(
            {
                code: currentCode,
                stdin: stdinValue ?? '',
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
        )
    };

    // По нажатию "Проверить"
    const handleCheck = () => {
        if (!activeTaskId || !currentTask) return;
        const submitted_at = new Date().toISOString();

        const langNameForServer = selectedLanguage ?? 'Plain Text';

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
                    refetchAttempts();
                },
            }
        );
    };

    const handleFinish = () => {
        if (!moduleId || !sessionData?.session || sessionData.session.finished_at) return;
        setSessionEndReason('manual');
        finishSession(moduleId, {
            onSuccess: () => {
                setIsSessionExpired(false);
            },
        });
    };

    useEffect(() => {
        if (!sessionData?.session) {
            setTimeRemaining(null);
            setIsSessionExpired(false);
            return;
        }

        const session = sessionData.session;
        if (session.finished_at) {
            setTimeRemaining(null);
            setIsSessionExpired(false);
            return;
        }

        setSessionEndReason(null);
        const serverTime = new Date(sessionData.server_time_now);
        
        if (session.expires_at && new Date(session.expires_at) <= serverTime) {
            setSessionEndReason('expired');
            setIsSessionExpired(true);
            setTimeRemaining(0);
            return;
        }

        if (!session.expires_at) {
            setTimeRemaining(null);
            setIsSessionExpired(false);
            return;
        }

        const serverStartedAt = new Date(sessionData.server_time_now).getTime();
        const clientStartedAt = Date.now();
        const expiresAt = new Date(session.expires_at).getTime();

        const calculateTimeRemaining = () => {
            const estimatedServerNow = serverStartedAt + (Date.now() - clientStartedAt);
            const remaining = expiresAt - estimatedServerNow;

            return Math.max(0, Math.floor(remaining / 1000));
        };

        const updateTimer = () => {
            const remaining = calculateTimeRemaining();
            setTimeRemaining(remaining);
            
            if (remaining <= 0) {
                setSessionEndReason('expired');
                setIsSessionExpired(true);
                finishSession(moduleId);
                return true;
            }

            return false;
        };

        if (updateTimer()) return;

        const interval = setInterval(() => {
            if (updateTimer()) {
                clearInterval(interval);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [sessionData, finishSession, moduleId]);

    const canExecute = !!(!isSessionExpired && sessionData?.session && !sessionData.session.finished_at);
    const { user } = useAuth();
    const editorLanguage = mapServerLangToMonaco(selectedLanguage || undefined);

    if (!sessionData?.session || sessionData.session.finished_at || isSessionExpired) {
        const isTimeExpired = sessionEndReason === 'expired' || (isSessionExpired && sessionEndReason !== 'manual');

        return (
            <div className={styles.expiredSession}>
                <h2>{isTimeExpired ? 'Время вышло' : 'Прохождение завершено'}</h2>
                <p>
                    {isTimeExpired
                        ? 'Время прохождения модуля закончилось.'
                        : 'Вы завершили прохождение модуля.'}
                </p>
                <button onClick={() => window.location.href = `/?module_id=${moduleId}`}>
                    Вернуться к модулю
                </button>
            </div>
        );
    }

    return (
        <div>
            <Header
                selectedLanguage={selectedLanguage}
                setSelectedLanguage={setSelectedLanguage}
                onRun={handleRun}
                onCheck={handleCheck}
                languages={availableLanguages}
                timeRemaining={timeRemaining}
                canExecute={canExecute}
                onFinish={handleFinish}
                isFinishing={isFinishingSession}
                user={user}
                attemptsUsed={attemptsData?.attempts_used}
                maxAttempts={attemptsData?.max_attempts}
            />

            <PanelGroup direction="horizontal">
                <Panel defaultSize={30} minSize={20} maxSize={90} className={styles.editorPanel}>
                    <CodeEditor
                        language={editorLanguage}
                        value={currentCode}
                        onChange={(value) => handleCodeChange(value || '')}
                    />
                </Panel>

                <PanelResizeHandle className={styles.gutterHorizontal}/>

                <Panel defaultSize={30} minSize={10} maxSize={80}>
                    <PanelGroup direction="vertical">
                        <Panel defaultSize={60} minSize={20} maxSize={80}>
                            <div className={styles.rightTop}>
                                <TasksSection
                                    moduleId={moduleId}
                                    activeTaskId={activeTaskId}
                                    setActiveTaskId={setActiveTaskId}
                                    onTaskChange={handleTaskChange}
                                />
                            </div>
                        </Panel>

                        <PanelResizeHandle className={styles.gutterVertical}/>

                        <Panel defaultSize={40} minSize={20} maxSize={80}>
                            <div className={styles.rightBottom}>
                                <ConsoleSection
                                    output={
                                        activeTaskId ? (consoleOutputs[activeTaskId] ?? null) : null
                                    }
                                    activeTab={consoleTab}
                                    onTabChange={setConsoleTab}
                                    inputValue={stdinValue}
                                    onInputValueChange={handleStdinChange}
                                    isLoading={isChecking || isRunning}
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
