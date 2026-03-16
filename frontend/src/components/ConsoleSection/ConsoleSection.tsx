import {useState} from "react";
import styles from "./ConsoleSection.module.scss";

const ConsoleSection = () => {
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
                                activeTab === "input"
                                    ? "translateX(0%)"
                                    : "translateX(100%)"
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
                        Программа ещё не запускалась
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConsoleSection;