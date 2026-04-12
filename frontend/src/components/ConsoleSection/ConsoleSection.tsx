import styles from "./ConsoleSection.module.scss";

export interface ConsoleOutput {
    success?: boolean;
    error?: string;
    comment?: string;
    passed?: string;
}

interface ConsoleSectionProps {
    activeTab: "input" | "output";
    onTabChange?: (tab: "input" | "output") => void;
    output: ConsoleOutput | null;
    inputValue?: string;
    onInputValueChange?: (value: string) => void;
}

const ConsoleSection = ({output, activeTab, onTabChange, inputValue="", onInputValueChange}: ConsoleSectionProps) => {
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
                        value={inputValue}
                        onChange={(e) => onInputValueChange?.(e.target.value)}
                        placeholder="Введите тестовые данные..."    
                    />
                )}

                {activeTab === "output" && (
                    <div className={styles.consoleOutput}>
                        {!output ? (
                            <div className={styles.messageInfo}>Нет вывода</div>
                        ) : (
                            <div className={styles.outputContainer}>
                                <div className={output.success ? styles.messageSuccess : styles.messageError}>
                                    {output.success ? "Passed" : "Failed"}
                                </div>

                                {output.comment && (
                                    <div className={styles.messageComment}>
                                        <strong>Комментарий:</strong> {output.comment}
                                    </div>
                                )}

                                {output.passed !== undefined && (
                                    <div className={styles.messageInfo}>
                                        {output.passed}
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