import {useState} from "react";
import styles from "./Header.module.scss";
import runIcon from '../../assets/icons/run_icon.svg';
import submitIcon from '../../assets/icons/submit_icon.svg';
import attemptIcon from '../../assets/icons/attempt_icon.svg';
import timeIcon from '../../assets/icons/time_icon.svg';
import themeIcon from '../../assets/icons/theme_icon.svg';
import profileIcon from '../../assets/icons/profile_icon.svg';
import logoutIcon from '../../assets/icons/logout_icon.svg';
import IconButton from "../../UI/IconButton/IconButton.tsx"

const Header = () => {
    const [language, setLanguage] = useState("javascript");

    return (
        <div className={styles.header}>
            <div className={styles.logoContainer}>
                <img src="/logo.png" alt=""/>
                <h1 className={styles.logoTitle}>CodeIDE</h1>
                <div className={styles.controls}>
                    <div className={styles.languageSelector}>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                        >
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="cpp">C++</option>
                        </select>
                        <span className={styles.arrow}> › </span>
                    </div>
                </div>
            </div>
            <div className={styles.actionPanel}>
                <IconButton icon={runIcon} label="Запустить" type="run" />
                <IconButton icon={submitIcon} label="Проверить" type="submit" />
                <div className={styles.infoBadge}>
                    <img src={attemptIcon} alt="attempts"/>
                    <span className={styles.attemptText}>3/5 попыток</span>
                </div>
                <div className={styles.infoBadge}>
                    <img src={timeIcon} alt="time"/>
                    <span className={styles.timeText}>45:32</span>
                </div>
            </div>
            <div className={styles.profile}>
                <button className={`${styles.infoBadge} ${styles.themeBlock}`}>
                    <img src={themeIcon} alt="theme"/>
                </button>
                <div className={styles.infoBadge}>
                    <img src={profileIcon} alt="profile"/>
                    <span className={styles.profileText}>username</span>
                </div>
                <button className={`${styles.infoBadge} ${styles.logoutBlock}`}>
                    <img src={logoutIcon} alt="logout"/>
                </button>
            </div>

        </div>
    );
};

export default Header;