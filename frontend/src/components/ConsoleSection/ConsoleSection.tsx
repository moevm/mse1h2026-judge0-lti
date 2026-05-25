import styles from "./ConsoleSection.module.scss";
import Spinner from '../../UI/Spinner/Spinner.tsx'

export interface ConsoleOutput {
    success?: boolean;
    error?: string;
    comment?: string;
    passed?: string;
    score?: number | null;
}

interface ConsoleSectionProps {
    activeTab: "input" | "output";
    onTabChange?: (tab: "input" | "output") => void;
    output: ConsoleOutput | null;
    inputValue?: string | null;
    onInputValueChange?: (value: string | null) => void;
    isLoading?: boolean;
}

const getScore = (output: ConsoleOutput | null) => {
    if (!output) return null;
    if (typeof output.score === 'number') return output.score;

    const match = output.passed?.match(/(\d+)\s*\/\s*(\d+)/);
    if (!match) return null;

    const passed = Number(match[1]);
    const total = Number(match[2]);

    if (!Number.isFinite(passed) || !Number.isFinite(total) || total <= 0) return null;

    return Math.floor((passed * 100) / total);
};

const getPassedText = (output: ConsoleOutput | null) => {
    const value = output?.passed?.trim();
    if (!value) return null;

    const match = value.match(/(\d+)\s*\/\s*(\d+)/);
    return match ? `${match[1]}/${match[2]}` : value;
};

const ConsoleSection = ({output, activeTab, onTabChange, inputValue="", onInputValueChange, isLoading = false}: ConsoleSectionProps) => {
    const score = getScore(output);
    const passedText = getPassedText(output);

    return (
        <div className={styles.consoleSection}>
            <div className={styles.consoleHeader}>
                <div className={styles.tabs}>
                    <button
                        className={`${styles.tab} ${activeTab === "input" ? styles.active : ""}`}
                        onClick={() => onTabChange?.("input")}
                    >
                        Input
                    </button>

                    <button
                        className={`${styles.tab} ${activeTab === "output" ? styles.active : ""}`}
                        onClick={() => onTabChange?.("output")}
                    >
                        Output
                    </button>

                    <div
                        className={styles.indicator}
                        style={{
                            transform: activeTab === "input" ? "translateX(0%)" : "translateX(100%)"
                        }}
                    />
                </div>
            </div>

            <div className={styles.consoleBody}>
                {activeTab === "input" && (
                    <textarea 
                        className={styles.consoleInput}
                        value={inputValue || ""}
                        onChange={(e) => onInputValueChange?.(e.target.value)}
                        placeholder="Введите тестовые данные..."    
                    />
                )}

                {activeTab === "output" && (
                    <div className={styles.consoleOutput}>
                        {isLoading ? (
                            <div className={styles.loaderContainer}>
                                <Spinner showLabel={false} />
                            </div>
                        ) : !output ? (
                            <div className={styles.messageInfo}>Нет вывода</div>
                        ) : (
                            <div className={styles.outputContainer}>
                                <div className={output.success ? styles.messageSuccess : styles.messageError}>
                                    {output.success ? "Passed" : "Failed"}
                                </div>

                                {(score !== null || passedText) && (
                                    <div className={styles.resultMetrics}>
                                        {score !== null && (
                                            <div className={styles.resultMetric}>
                                                <span>Баллы</span>
                                                <strong>{score}</strong>
                                            </div>
                                        )}
                                        {passedText && (
                                            <div className={styles.resultMetric}>
                                                <span>Тестов пройдено</span>
                                                <strong>{passedText}</strong>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {output.comment && (
                                    <div className={styles.messageComment}>
                                        <strong>Комментарий:</strong> {output.comment}
                                    </div>
                                )}

                                {output.error && (
                                    <div className={styles.messageError}>
                                        <strong>Error:</strong>
                                        <pre>{output.error}</pre>
                                    </div>
                                )}

                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConsoleSection;
