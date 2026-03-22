import { useEffect } from "react";
import Editor, { loader } from '@monaco-editor/react';
import styles from "../../pages/IDEPage/IDEPage.module.scss";

interface CodeEditorProps {
    language: string;
    value: string;
    onChange: (value: string | undefined) => void;
}

const CodeEditor = ({ language, value, onChange }: CodeEditorProps) => {
    const theme = 'myCustomTheme';

    useEffect(() => {
        loader.init().then((monaco) => {
            monaco.editor.defineTheme('myCustomTheme', {
                base: 'vs-dark',
                inherit: true,
                rules: [],
                colors: {
                    'editor.background': '#0D1117',
                },
            });
        });
    }, []);

    return (
        <div className={styles.ideContainer}>
            <Editor
                height="100%"
                language={language}
                value={value}
                onChange={onChange}
                theme={theme}
                options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: "on",
                    automaticLayout: true
                }}
            />
        </div>
    );
};

export default CodeEditor;