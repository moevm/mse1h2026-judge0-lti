import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAttempt } from '../../hooks/queries/useUsers'
import styles from './AdminStudentAttemptPage.module.scss'
import Spinner from '../../UI/Spinner/Spinner'

interface TestDetail {
    id: number
    title: string
    status: 'passed' | 'failed' | 'error'
    input?: string
    expected?: string
    output?: string
    error?: string
}

const AdminStudentAttemptPage = () => {
    const { attemptId } = useParams<{ attemptId: string }>()
    const navigate = useNavigate()
    const aid = Number(attemptId)
    const [expandedTests, setExpandedTests] = useState<Set<number>>(new Set())

    const { data: attempt, isLoading, isError } = useAttempt(aid)

    const toggleTest = (testId: number) => {
        setExpandedTests(prev => {
            const newSet = new Set(prev)
            if (newSet.has(testId)) {
                newSet.delete(testId)
            } else {
                newSet.add(testId)
            }
            return newSet
        })
    }

    const formatDate = (value: string) =>
        new Intl.DateTimeFormat('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }).format(new Date(value))

    // Парсим тесты из message или создаем фейковые для демо
    const formatScore = (score: number | null | undefined) => (
        typeof score === 'number' ? `${score} баллов` : null
    )

    const tests: TestDetail[] = [
        { id: 1, title: 'Test #1', status: 'failed', input: '[2, 4, 8, 16]', expected: '32', output: 'NaN' },
        { id: 2, title: 'Test #2', status: 'failed', input: '[1, 2, 3]', expected: '6', output: '3' },
    ]

    if (isLoading) return <div className={styles.state}><Spinner /></div>
    if (isError || !attempt) return <div className={styles.state}>Попытка не найдена</div>

    return (
        <div className={styles.layout}>
            {/* Левая колонка - тесты */}
            <div className={styles.left}>
                <div className={styles.date}>{formatDate(attempt.created_at)}</div>

                <div className={attempt.is_solved ? styles.statusSuccess : styles.statusFail}>
                    {attempt.is_solved ? 'Все тесты пройдены' : 'Пройдены не все тесты'}
                </div>

                {formatScore(attempt.score) ? (
                    <div className={styles.scoreBadge}>{formatScore(attempt.score)}</div>
                ) : null}

                <div className={styles.section}>
                    <div className={styles.sectionTitle}>Тесты</div>
                    {tests.map(test => (
                        <div
                            key={test.id}
                            className={`${styles.testItem} ${expandedTests.has(test.id) ? styles.expanded : ''}`}
                        >
                            <div className={styles.testHeader} onClick={() => toggleTest(test.id)}>
                                <md-icon className={test.status === 'passed' ? styles.iconSuccess : styles.iconError}>
                                    {test.status === 'passed' ? 'check_circle' : 'cancel'}
                                </md-icon>
                                <span>{test.title}</span>
                                <md-icon className={styles.arrow}>
                                    {expandedTests.has(test.id) ? 'expand_less' : 'expand_more'}
                                </md-icon>
                            </div>

                            {expandedTests.has(test.id) && (
                                <div className={styles.testDetail}>
                                    {test.status === 'failed' && (
                                        <>
                                            <div className={styles.verdict}>Wrong Answer</div>
                                            <div className={styles.detailLine}>
                                                <span className={styles.detailLabel}>Input:</span>
                                                <span className={styles.detailValue}>{test.input}</span>
                                            </div>
                                            <div className={styles.detailLine}>
                                                <span className={styles.detailLabel}>Expected:</span>
                                                <span className={styles.detailValue}>{test.expected}</span>
                                            </div>
                                            <div className={styles.detailLine}>
                                                <span className={styles.detailLabel}>Output:</span>
                                                <span className={styles.detailValue}>{test.output}</span>
                                            </div>
                                        </>
                                    )}
                                    {test.status === 'error' && (
                                        <>
                                            <div className={styles.verdict}>Runtime Error</div>
                                            <div className={styles.errorMessage}>{test.error}</div>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Правая колонка - код */}
            <div className={styles.right}>
                <div className={styles.rightHeader}>
                    <button className={styles.backBtn} onClick={() => navigate(-1)}>
                        <md-icon>arrow_back</md-icon>
                    </button>
                    <h1 className={styles.title}>Попытка #{attempt.id}</h1>
                </div>

                <div className={styles.codeWrapper}>
                    <div className={styles.codeHeader}>
                        <span className={styles.codeLang}>{attempt.language || 'code'}</span>
                    </div>
                    <pre className={styles.codeBlock}>
                        <code>{attempt.source_code || '// Код недоступен'}</code>
                    </pre>
                </div>
            </div>
        </div>
    )
}

export default AdminStudentAttemptPage
