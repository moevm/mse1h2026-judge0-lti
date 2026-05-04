import IconButton from '../../UI/IconButton/IconButton';
import styles from './LandingPage.module.scss';

import adminPanelIcon from '../../assets/icons/admin_panel_icon.svg'
import runIcon from '../../assets/icons/run_icon.svg';
import repeatIcon from '../../assets/icons/repeat_icon.svg';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';
import { useModule } from '../../hooks/queries/useModule';

// TODO: Для демонстрации
const MODULE_ID: number = 1;

const LandingPage = () => {
    const navigate = useNavigate();
    const { user, isAdmin } = useAuth();
    const { data: module } = useModule(MODULE_ID);

    const displayUsername = user?.username || user?.id.toString() || "Гость";

    const handleStart = () => {
        navigate("/task");
    };

    const handleRetake = () => {
        navigate("/task");
    };

    const handleAdminPanel = () => {
        navigate("/admin");
    };

    return (
        <div className={styles.landingPageContainer}>
            
            <div className={styles.header}>
                <div className={styles.username}>
                    {`Username: ${displayUsername}`}
                </div>
                {isAdmin && (
                    <IconButton
                        icon={adminPanelIcon}
                        label="Админ-панель"
                        type="adminPanelEntry"
                        onClick={handleAdminPanel}
                    />
                )}
            </div>

            <div className={styles.mainContainer}>
                <div className={styles.textGroup}>
                    <div className={styles.titleText}>
                        {`${module?.title}`}
                    </div>
                    <div className={styles.descriptionText}>
                        {`${module?.description}`}
                    </div>
                </div>

                <div className={styles.buttonGroup}>
                    <IconButton 
                        icon={runIcon}
                        label="Начать" 
                        type="run"
                        onClick={handleStart}    
                    />
                    <IconButton
                        icon={repeatIcon}
                        label="Перепройти"
                        type="submit"
                        onClick={handleRetake}
                    />
                </div>

            </div>
        </div>
    );
};

export default LandingPage;