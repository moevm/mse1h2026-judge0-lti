import {Panel, PanelGroup, PanelResizeHandle} from "react-resizable-panels";
import CodeEditor from "../../components/CodeEditor/CodeEditor";
import styles from "./IDEPage.module.scss";
import TasksSection from "../../components/TasksSection/TasksSection.tsx";
import ConsoleSection from "../../components/ConsoleSection/ConsoleSection.tsx";

interface IDEPageProps {
  language: string;
}

const IDEPage = ({ language }: IDEPageProps) => {
    return (
        <div>
            <PanelGroup direction="horizontal">
                <Panel defaultSize={30} minSize={20} maxSize={90} className={styles.editorPanel}>
                    <CodeEditor language={language} />
                </Panel>

                <PanelResizeHandle className={styles.gutterHorizontal}/>

                <Panel defaultSize={30} minSize={10} maxSize={80}>
                    <PanelGroup direction="vertical">
                        <Panel defaultSize={60} minSize={20} maxSize={80}>
                            <div className={styles.rightTop}>
                                <TasksSection/>
                            </div>
                        </Panel>
                        <PanelResizeHandle className={styles.gutterVertical}/>
                        <Panel defaultSize={40} minSize={20} maxSize={80}>
                            <div className={styles.rightBottom}>
                                <ConsoleSection/>
                            </div>
                        </Panel>
                    </PanelGroup>
                </Panel>
            </PanelGroup>
        </div>
    );
};

export default IDEPage;