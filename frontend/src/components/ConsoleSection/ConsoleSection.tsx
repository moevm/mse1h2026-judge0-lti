import {useState} from "react";
import styles from "./ConsoleSection.module.scss";

export interface ConsoleOutput {
    success?: boolean;
    error?: string;
    comment?: string;
    passed?: string;
}


interface ConsoleSectionProps {
    output: ConsoleOutput | null;
}

const ConsoleSection = ({output}: ConsoleSectionProps) => {
    const [activeTab, setActiveTab] = useState<"input" | "output">("output");

    return (
        <div className={styles.consoleSection}>
            <div className={styles.consoleHeader}>
                <div className={styles.tabs}>
                    <button
                        className={`${styles.tab} ${activeTab === "input" ? styles.active : ""}`}
                        onClick={() => setActiveTab("input")}
                    >
                        Input
                    </button>

                    <button
                        className={`${styles.tab} ${activeTab === "output" ? styles.active : ""}`}
                        onClick={() => setActiveTab("output")}
                    >
                        Output
                    </button>

                    <div
                        className={styles.indicator}
                        style={{
                            transform:
                                activeTab === "input" ? "translateX(0%)" : "translateX(100%)"
                        }}
                    />
                </div>
            </div>

            <div className={styles.consoleBody}>
                {activeTab === "input" && (
                    <textarea
                        className={styles.consoleInput}
                    />
                )}

                {activeTab === "output" && (
                    <div className={styles.consoleOutput}>
                        {!output ? (
                            <div className={styles.messageInfo}>Программа ещё не запускалась</div>
                        ) : (
                            <div className={styles.outputContainer}>
                                <div
                                    className={
                                        output.success ? styles.messageSuccess : styles.messageError
                                    }
                                >
                                    {output.success ? "Passed" : "Failed"}
                                </div>

                                {output.error && (
                                    <div className={styles.messageError}>
                                        <strong>Error:</strong> {output.error}
                                    </div>
                                )}

                                {output.comment && (
                                    <div className={styles.messageComment}>
                                        <strong>Comment:</strong> {output.comment}
                                    </div>
                                )}

                                {output.passed !== undefined && (
                                    <div className={styles.messageInfo}>
                                        {output.passed}
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