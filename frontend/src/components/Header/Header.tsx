import styles from "./Header.module.scss";
import runIcon from '../../assets/icons/run_icon.svg';
import submitIcon from '../../assets/icons/submit_icon.svg';
import attemptIcon from '../../assets/icons/attempt_icon.svg';
import timeIcon from '../../assets/icons/time_icon.svg';
import themeIcon from '../../assets/icons/theme_icon.svg';
import profileIcon from '../../assets/icons/profile_icon.svg';
import logoutIcon from '../../assets/icons/logout_icon.svg';
import IconButton from "../../UI/IconButton/IconButton.tsx"
import type { Language } from "../../api/languages.api.ts";

interface HeaderProps {
    selectedLanguageId: number | null;
    setSelectedLanguageId: (id: number) => void;
    onCheck: () => void;
    languages: Language[];
}

const Header = ({ selectedLanguageId, setSelectedLanguageId, onCheck, languages }: HeaderProps) => {
    return (
        <div className={styles.header}>
            <div className={styles.logoContainer}>
                <img src="/logo.png" alt="" />
                <h1 className={styles.logoTitle}>CodeIDE</h1>
                <div className={styles.controls}>
                    <div className={styles.languageSelector}>
                        <select
                            value={selectedLanguageId ?? ""}
                            onChange={(e) => setSelectedLanguageId(Number(e.target.value))}
                            disabled={languages.length === 0}
                        >
                            <option value="" disabled>Выберите язык</option>
                            {languages.map(lang => (
                                <option key={lang.id} value={lang.id}>{lang.language}</option>
                            ))}
                        </select>
                        <span className={styles.arrow}> › </span>
                    </div>
                </div>
            </div>
            <div className={styles.actionPanel}>
                <IconButton icon={runIcon} label="Запустить" type="run" />
                <IconButton icon={submitIcon} label="Проверить" type="submit" onClick={onCheck} />
                <div className={styles.infoBadge}>
                    <img src={attemptIcon} alt="attempts" />
                    <span className={styles.attemptText}>3/5 попыток</span>
                </div>
                <div className={styles.infoBadge}>
                    <img src={timeIcon} alt="time" />
                    <span className={styles.timeText}>45:32</span>
                </div>
            </div>
            <div className={styles.profile}>
                <button className={`${styles.infoBadge} ${styles.themeBlock}`}>
                    <img src={themeIcon} alt="theme" />
                </button>
                <div className={styles.infoBadge}>
                    <img src={profileIcon} alt="profile" />
                    <span className={styles.profileText}>username</span>
                </div>
                <button className={`${styles.infoBadge} ${styles.logoutBlock}`}>
                    <img src={logoutIcon} alt="logout" />
                </button>
            </div>
        </div>
    );
};

export default Header;