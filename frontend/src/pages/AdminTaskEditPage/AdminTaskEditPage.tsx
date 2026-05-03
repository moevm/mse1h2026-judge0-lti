import {useState, useEffect} from 'react'
import {useParams, useNavigate} from 'react-router-dom'
import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'
import {toast} from 'sonner'
import {tasksApi, type TaskPayload} from '../../api/modules.api'
import {useLanguages} from '../../hooks/queries/useLanguages'
import {taskKeys} from '../../lib/query-keys'
import Spinner from '../../UI/Spinner/Spinner'
import styles from './AdminTaskEditPage.module.scss'
import ImportTestsModal from "../../UI/ImportTestsModal/ImportTestsModal.tsx";

interface TabType {
    id: 'task' | 'tests'
    label: string
}

const tabs: TabType[] = [
    {id: 'task', label: 'Задание'},
    {id: 'tests', label: 'Тесты'},
]

const AdminTaskEditPage = () => {
    const {taskId} = useParams()
    const handleBack = () => {
    if (window.history.length > 1) {
        navigate(-1)
    } else {
        navigate('/admin/tasks')
    }
}
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const isNewTask = taskId === 'new' || !taskId || taskId === 'undefined'
    const id = isNewTask ? null : Number(taskId)

    const [activeTab, setActiveTab] = useState<'task' | 'tests'>('task')
    const [title, setTitle] = useState('')
    const [description, setDescription] = useState('')
    const [timeout, setTimeout] = useState<number>(2)
    const [languages, setLanguages] = useState<string[]>([])
    const [selectedLanguage, setSelectedLanguage] = useState('')
    const [availableLanguages, setAvailableLanguages] = useState<string[]>([])
    const [tests, setTests] = useState<Array<{ title: string; stdin: string; stdout: string }>>([])
    const {data: task, isLoading: isLoadingTask} = useQuery({
        queryKey: taskKeys.detail(id!),
        queryFn: () => tasksApi.getTask(id!),
        enabled: !isNewTask && id !== null && !isNaN(id!),
        retry: false,
    })

    const {data: allLanguages = [], isLoading: isLoadingLanguages} = useLanguages()

    useEffect(() => {
        if (task && !isNewTask) {
            setTitle(task.title)
            setDescription(task.description)
            setTimeout(task.timeout)
            setLanguages(task.languages)
            setTests(task.tests.map(t => ({
                title: t.title,
                stdin: t.stdin || '',
                stdout: t.stdout,
            })))
        }
    }, [task, isNewTask])

    useEffect(() => {
        const available = allLanguages
            .map(lang => lang.language)
            .filter(lang => !languages.includes(lang))
        setAvailableLanguages(available)
        if (available.length > 0 && !selectedLanguage) {
            setSelectedLanguage(available[0])
        }
    }, [allLanguages, languages])

    const addLanguage = () => {
        if (selectedLanguage && !languages.includes(selectedLanguage)) {
            setLanguages(prev => [...prev, selectedLanguage])
            const newAvailable = availableLanguages.filter(l => l !== selectedLanguage)
            setAvailableLanguages(newAvailable)
            if (newAvailable.length > 0) {
                setSelectedLanguage(newAvailable[0])
            } else {
                setSelectedLanguage('')
            }
        }
    }

    const removeLanguage = (lang: string) => {
        setLanguages(prev => prev.filter(l => l !== lang))
        setAvailableLanguages(prev => [...prev, lang].sort())
    }

    const addTest = () => {
        setTests(prev => [...prev, {title: '', stdin: '', stdout: ''}])
    }

    const updateTest = (index: number, field: keyof typeof tests[0], value: string) => {
        setTests(prev => prev.map((test, i) =>
            i === index ? {...test, [field]: value} : test
        ))
    }

    const removeTest = (index: number) => {
        setTests(prev => prev.filter((_, i) => i !== index))
    }

    const [isImportModalOpen, setIsImportModalOpen] = useState(false)

    const handleImportTests = (importedTests: Array<{ title: string; stdin: string; stdout: string }>) => {
        setTests(prev => [...prev, ...importedTests])
    }

    const saveMutation = useMutation({
        mutationFn: async () => {
            const payload: TaskPayload = {
                title: title.trim(),
                description: description.trim(),
                timeout,
                languages,
                tests: tests.filter(t => t.title.trim() && t.stdout.trim()),
            }

            if (isNewTask) {
                return tasksApi.createTask(payload)
            } else {
                return tasksApi.updateTask(id!, payload)
            }
        },
        onSuccess: (savedTask) => {
            queryClient.invalidateQueries({queryKey: taskKeys.all})

            queryClient.setQueryData(taskKeys.detail(savedTask.id), savedTask)

            toast.success(isNewTask ? 'Задача создана' : 'Задача обновлена')

            if (isNewTask) {
                navigate(`/admin/tasks/${savedTask.id}`, {replace: true})
            }
        },
        onError: (error: any) => {
            const message = error?.response?.data?.detail || 'Не удалось сохранить задачу'
            toast.error(message)
        },
    })

    const isLoading = isLoadingTask || isLoadingLanguages

    if (isLoading) {
        return (
            <div className={styles.loading}>
                <Spinner/>
            </div>
        )
    }

    return (<>
            <div className="page">
                <button className="backLink" onClick={handleBack}>
                    <md-icon>arrow_back</md-icon>
                    <span>Вернуться</span>
                </button>

                <div className={styles.header}>
                    <input
                        type="text"
                        className={styles.titleInput}
                        value={title}
                        onChange={e => setTitle(e.target.value)}
                        placeholder="Название задачи"
                    />
                </div>

                <div className={styles.languagesSection}>
                    <div className={styles.languagesHeader}>
                        <span className={styles.languagesLabel}>Языки:</span>
                        <div className={styles.languagesList}>
                            {languages.map(lang => (
                                <span key={lang} className={styles.languageTag}>
                                {lang}
                                    <button
                                        type="button"
                                        className={styles.removeLanguage}
                                        onClick={() => removeLanguage(lang)}
                                    >
                                    <md-icon>close</md-icon>
                                </button>
                            </span>
                            ))}
                        </div>

                        {availableLanguages.length > 0 && (
                            <div className={styles.addLanguage}>
                                <select
                                    value={selectedLanguage}
                                    onChange={e => setSelectedLanguage(e.target.value)}
                                    className={styles.languageSelect}
                                >
                                    {availableLanguages.map(lang => (
                                        <option key={lang} value={lang}>{lang}</option>
                                    ))}
                                </select>
                                <button
                                    type="button"
                                    className={styles.addLanguageButton}
                                    onClick={addLanguage}
                                >
                                    <md-icon>add</md-icon>
                                    Добавить язык
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <div className={styles.tabs}>
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className={styles.tabContent}>
                    {activeTab === 'task' && (
                        <div className={styles.taskTab}>
                            <label className={styles.descriptionLabel}>
                                <span>Описание</span>
                                <textarea
                                    className={styles.descriptionTextarea}
                                    value={description}
                                    onChange={e => setDescription(e.target.value)}
                                    placeholder="Введите описание задачи..."
                                    rows={10}
                                />
                            </label>

                            <label className={styles.timeoutLabel}>
                                <span>Лимит времени (секунды)</span>
                                <input
                                    type="number"
                                    className={styles.timeoutInput}
                                    value={timeout}
                                    onChange={e => setTimeout(Number(e.target.value))}
                                    min={1}
                                    step={1}
                                />
                            </label>
                        </div>
                    )}

                    {activeTab === 'tests' && (
                        <div className={styles.testsTab}>
                            <div className={styles.testsHeader}>
                                <button
                                    type="button"
                                    className={styles.addTestButton}
                                    onClick={addTest}
                                >
                                    <md-icon>add</md-icon>
                                    Добавить тест
                                </button>
                                <button
                                    type="button"
                                    className={styles.importButton}
                                    onClick={() => setIsImportModalOpen(true)}
                                >
                                    <md-icon>upload_file</md-icon>
                                    Загрузить JSON
                                </button>
                            </div>

                            {tests.length === 0 && (
                                <div className={styles.noTests}>
                                    <md-icon>science</md-icon>
                                    <span>Нет тестов. Добавьте первый тест</span>
                                </div>
                            )}

                            {tests.map((test, index) => (
                                <div key={index} className={styles.testCard}>
                                    <div className={styles.testHeader}>
                                        <input
                                            type="text"
                                            className={styles.testTitle}
                                            value={test.title}
                                            onChange={e => updateTest(index, 'title', e.target.value)}
                                            placeholder={`Тест ${index + 1}`}
                                        />
                                        <button
                                            type="button"
                                            className={styles.removeTest}
                                            onClick={() => removeTest(index)}
                                        >
                                            <md-icon>delete</md-icon>
                                        </button>
                                    </div>

                                    <div className={styles.testFields}>
                                        <label>
                                            <span>Входные данные (stdin)</span>
                                            <textarea
                                                className={styles.testStdin}
                                                value={test.stdin}
                                                onChange={e => updateTest(index, 'stdin', e.target.value)}
                                                placeholder="Входные данные..."
                                                rows={3}
                                            />
                                        </label>

                                        <label>
                                            <span>Ожидаемый вывод (stdout)</span>
                                            <textarea
                                                className={styles.testStdout}
                                                value={test.stdout}
                                                onChange={e => updateTest(index, 'stdout', e.target.value)}
                                                placeholder="Ожидаемый вывод..."
                                                rows={3}
                                            />
                                        </label>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className={styles.footer}>
                    <button
                        type="button"
                        className={styles.cancelButton}
                        onClick={() => navigate('/admin/tasks')}
                    >
                        Отмена
                    </button>
                    <button
                        type="button"
                        className={styles.saveButton}
                        onClick={() => saveMutation.mutate()}
                        disabled={!title.trim() || languages.length === 0 || saveMutation.isPending}
                    >
                        {saveMutation.isPending ? 'Сохранение...' : 'Сохранить'}
                    </button>
                </div>
            </div>
            <ImportTestsModal
                isOpen={isImportModalOpen}
                onClose={() => setIsImportModalOpen(false)}
                onImport={handleImportTests}
            />
        </>
    )
}

export default AdminTaskEditPage