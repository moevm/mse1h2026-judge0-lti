import IconButton from '../../UI/IconButton/IconButton';
import styles from './LandingPage.module.scss';

import adminPanelIcon from '../../assets/icons/admin_panel_icon.svg'
import runIcon from '../../assets/icons/run_icon.svg';
import repeatIcon from '../../assets/icons/repeat_icon.svg';
import {useNavigate, useSearchParams} from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';
import { useModule } from '../../hooks/queries/useModule';
import { modulesApi } from '../../api/modules.api';
import { toast } from 'sonner';


const LandingPage = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { user, isAdmin } = useAuth();
    const moduleId = searchParams.get('module_id');
    const { data: module } = useModule(moduleId ? Number(moduleId) : null);
    if (!moduleId) {
        return <div>Ошибка: модуль не указан</div>;
    }
    const displayUsername = user?.username || user?.id.toString() || "Гость";

    const openIde = async () => {
        const numericModuleId = Number(moduleId);

        if (!Number.isFinite(numericModuleId)) {
            toast.error('Некорректный модуль');
            return;
        }

        try {
            await modulesApi.startModuleSession(numericModuleId);
            navigate(`/task?module_id=${moduleId}`);
        } catch {
            toast.error('Не удалось начать прохождение модуля');
        }
    };

    const handleStart = () => {
        void openIde();
    };

    const handleRetake = () => {
        void openIde();
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
