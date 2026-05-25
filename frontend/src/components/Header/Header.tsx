import styles from './Header.module.scss';
import runIcon from '../../assets/icons/run_icon.svg';
import submitIcon from '../../assets/icons/submit_icon.svg';
import attemptIcon from '../../assets/icons/attempt_icon.svg';
import timeIcon from '../../assets/icons/time_icon.svg';
import profileIcon from '../../assets/icons/profile_icon.svg';
import IconButton from '../../UI/IconButton/IconButton.tsx';
import { useEffect, useState } from 'react';
import type { User } from '../../hooks/queries/useAuth.ts';


interface HeaderProps {
    selectedLanguage: string | null;
    setSelectedLanguage: (language: string) => void;
    onRun: () => void;
    onCheck: () => void;
    languages: string[];
    timeRemaining: number | null;
    canExecute: boolean;
    onFinish: () => void;
    isFinishing?: boolean;
    user: User | null;
    attemptsUsed?: number;
    maxAttempts?: number | null;
}

const Header = ({
    selectedLanguage,
    setSelectedLanguage,
    onRun,
    onCheck,
    languages,
    timeRemaining,
    canExecute,
    onFinish,
    isFinishing = false,
    user,
    attemptsUsed = 0,
    maxAttempts = null
}: HeaderProps) => {

    const [formattedTime, setFormattedTime] = useState<string>('');

    useEffect(() => {
        if (timeRemaining === null) {
            setFormattedTime('∞');
            return;
        }
        
        const formatTime = (seconds: number): string => {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            if (hours > 0) {
                return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        };
        
        setFormattedTime(formatTime(timeRemaining));
    }, [timeRemaining]);

    const attemptsText = maxAttempts === null 
        ? `${attemptsUsed}/∞`
        : `${attemptsUsed}/${maxAttempts}`

    return (
        <div className={styles.header}>
            <div className={styles.logoContainer}>
                <img src="/logo.png" alt=""/>
                <h1 className={styles.logoTitle}>CodeIDE</h1>
                <div className={styles.controls}>
                    <div className={styles.languageSelector}>
                        <select
                            value={selectedLanguage ?? ''}
                            onChange={(e) => setSelectedLanguage(e.target.value)}
                            disabled={languages.length === 0}
                        >
                            <option value="" disabled>
                                Выберите язык
                            </option>
                            {languages.map((lang) => (
                                <option key={lang} value={lang}>
                                    {lang}
                                </option>
                            ))}
                        </select>
                        <span className={styles.arrow}> › </span>
                    </div>
                </div>
            </div>
            <div className={styles.actionPanel}>
                <IconButton 
                    icon={runIcon}
                    label="Запустить" 
                    type="run"
                    onClick={onRun}
                    disabled={!canExecute}
                />
                <IconButton
                    icon={submitIcon}
                    label="Проверить"
                    type="submit"
                    onClick={onCheck}
                    disabled={!canExecute}
                />
                <div className={styles.infoBadge}>
                    <img src={attemptIcon} alt="attempts"/>
                    <span className={styles.attemptText}>
                        {attemptsText} попыток
                    </span>
                </div>
                <div className={styles.infoBadge}>
                    <img src={timeIcon} alt="time"/>
                    <span className={styles.timeText}>{formattedTime}</span>
                </div>
            </div>
            <div className={styles.profile}>
                <div className={styles.infoBadge}>
                    <img src={profileIcon} alt="profile"/>
                    <span className={styles.profileText}>{user?.username ?? 'Гость'}</span>
                </div>
                <button
                    type="button"
                    className={styles.finishButton}
                    onClick={onFinish}
                    disabled={!canExecute || isFinishing}
                >
                    <md-icon>flag</md-icon>
                    <span>{isFinishing ? 'Завершение...' : 'Завершить'}</span>
                </button>
            </div>
        </div>
    );
};

export default Header;

