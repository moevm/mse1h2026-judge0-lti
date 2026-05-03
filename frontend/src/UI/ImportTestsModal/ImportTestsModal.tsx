import { useRef, useState } from 'react'
import { toast } from 'sonner'
import styles from './ImportTestsModal.module.scss'

interface ImportTestsModalProps {
    isOpen: boolean
    onClose: () => void
    onImport: (tests: Array<{ title: string; stdin: string; stdout: string }>) => void
}

interface TestType {
    title: string
    stdin: string
    stdout: string
}

const ImportTestsModal = ({ isOpen, onClose, onImport }: ImportTestsModalProps) => {
    const [isImporting, setIsImporting] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const exampleFormat = {
        tests: [
            {
                title: "Проверка положительных чисел",
                stdin: "2 3",
                stdout: "5"
            },
            {
                title: "Проверка отрицательных чисел",
                stdin: "-5 -3",
                stdout: "-8"
            },
            {
                title: "Проверка с нулём",
                stdin: "0 7",
                stdout: "7"
            }
        ]
    }

    const clearFileInput = () => {
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        setIsImporting(true)
        const reader = new FileReader()

        reader.onload = (e) => {
            try {
                const content = e.target?.result as string
                const json = JSON.parse(content)

                if (!json.tests || !Array.isArray(json.tests)) {
                    toast.error('Неверный формат JSON. Ожидается { "tests": [...] }')
                    clearFileInput()
                    return
                }

                if (json.tests.length === 0) {
                    toast.error('Файл не содержит тестов')
                    clearFileInput()
                    return
                }

                const importedTests: TestType[] = json.tests.map((test: any, index: number) => ({
                    title: test.title || `Тест ${index + 1}`,
                    stdin: test.stdin || '',
                    stdout: test.stdout || '',
                }))

                const missingStdout = importedTests.filter((t: TestType) => !t.stdout)
                if (missingStdout.length > 0) {
                    toast.warning(`${missingStdout.length} тестов не имеют ожидаемого вывода`)
                }

                onImport(importedTests)
                toast.success(`Импортировано ${importedTests.length} тестов`)
                onClose()
            } catch {
                toast.error('Ошибка при разборе JSON файла. Проверьте синтаксис.')
            } finally {
                clearFileInput()
                setIsImporting(false)
            }
        }

        reader.onerror = () => {
            toast.error('Не удалось прочитать файл')
            clearFileInput()
            setIsImporting(false)
        }

        reader.readAsText(file)
    }

    const handleCopyExample = () => {
        navigator.clipboard.writeText(JSON.stringify(exampleFormat, null, 2))
        toast.success('Пример формата скопирован в буфер обмена')
    }

    const handleImportClick = () => {
        fileInputRef.current?.click()
    }

    if (!isOpen) return null

    const handleOverlayClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget && !isImporting) {
            onClose()
        }
    }

    return (
        <div className={styles.overlay} onClick={handleOverlayClick}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>Импорт тестов из JSON</h3>
                    <button
                        className={styles.closeButton}
                        onClick={onClose}
                        disabled={isImporting}
                    >
                        <md-icon>close</md-icon>
                    </button>
                </div>

                <div className={styles.content}>
                    <div className={styles.description}>
                        <md-icon>info</md-icon>
                        <p>Загрузите JSON файл с тестами в следующем формате:</p>
                    </div>

                    <div className={styles.exampleSection}>
                        <div className={styles.exampleHeader}>
                            <span>Пример формата</span>
                            <button
                                className={styles.copyButton}
                                onClick={handleCopyExample}
                            >
                                <md-icon>content_copy</md-icon>
                                Копировать
                            </button>
                        </div>
                        <pre className={styles.exampleCode}>
                            {JSON.stringify(exampleFormat, null, 2)}
                        </pre>
                    </div>

                    <div className={styles.uploadSection}>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".json"
                            onChange={handleFileUpload}
                            style={{ display: 'none' }}
                        />
                        <button
                            type="button"
                            className={styles.uploadButton}
                            onClick={handleImportClick}
                            disabled={isImporting}
                        >
                            <md-icon>cloud_upload</md-icon>
                            {isImporting ? 'Импорт...' : 'Выбрать JSON файл'}
                        </button>
                        <p className={styles.hint}>
                            Поддерживаются только файлы с расширением .json
                        </p>
                    </div>
                </div>

                <div className={styles.footer}>
                    <button
                        className={styles.cancelButton}
                        onClick={onClose}
                        disabled={isImporting}
                    >
                        Отмена
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ImportTestsModal