import IconButton from '../../UI/IconButton/IconButton';
import styles from './LandingPage.module.scss';

import adminPanelIcon from '../../assets/icons/admin_panel_icon.svg';
import runIcon from '../../assets/icons/run_icon.svg';
import repeatIcon from '../../assets/icons/repeat_icon.svg';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../hooks/queries/useAuth';
import { useModule } from '../../hooks/queries/useModule';
import { useFinishModuleSession, useModuleSession, useStartModuleSession } from '../../hooks/queries/useModuleSession';

const LandingPage = () => {
    const { user, isAdmin, isTeacher } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const moduleId = searchParams.get('module_id');

    const { data: module } = useModule(moduleId ? Number(moduleId) : null);
    const { data: sessionData, isLoading: isSessionLoading, refetch: refetchSession } = useModuleSession(moduleId ? Number(moduleId) : null);
    const { mutate: startSession, isPending: isStarting } = useStartModuleSession();
    const { mutate: finishSession, isPending: isFinishing } = useFinishModuleSession();

    if (!moduleId) {
        return <div>Ошибка: модуль не указан</div>;
    }

    const displayUsername = user?.username || user?.id.toString() || "Гость";

    const isSessionActive = Boolean(sessionData?.session && !sessionData.session.finished_at &&
        (!sessionData.session.expires_at || new Date(sessionData.session.expires_at) > new Date(sessionData.server_time_now)));

    const getStartButtonText = () => {
        if (isStarting) return "Запуск...";
        if (isSessionActive) return "Продолжить";
        return "Начать";
    };

    const getRetakeButtonText = () => {
        if (isFinishing) return "Перезапуск...";
        return "Перепройти";
    };

    const handleStart = () => {
        if (isSessionActive) {
            navigate(`/task?module_id=${moduleId}`);
        } else {
            startSession(Number(moduleId), {
                onSuccess: () => {
                    navigate(`/task?module_id=${moduleId}`);
                },
            });
        }
    };

    const handleRetake = () => {
        const moduleIdNumber = Number(moduleId);

        if (sessionData?.session && !sessionData.session.finished_at) {
            finishSession(moduleIdNumber, {
                onSuccess: () => {
                    startSession(moduleIdNumber, {
                        onSuccess: () => {
                            refetchSession();
                            navigate(`/task?module_id=${moduleId}`);
                        },
                    });
                },
            });
        } else {
            startSession(moduleIdNumber, {
                onSuccess: () => {
                    navigate(`/task?module_id=${moduleId}`);
                },
            });
        }
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
                {(isAdmin || isTeacher) && (
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
                        {module?.title ?? ''}
                    </div>
                    <div className={styles.descriptionText}>
                        {module?.description ?? ''}
                    </div>
                </div>

                <div className={styles.buttonGroup}>
                    {!isSessionLoading && (
                        <IconButton
                            icon={runIcon}
                            label={getStartButtonText()}
                            type="run"
                            onClick={handleStart}
                            disabled={isStarting}
                        />
                    )}
                    <IconButton
                        icon={repeatIcon}
                        label={getRetakeButtonText()}
                        type="submit"
                        onClick={handleRetake}
                        disabled={isFinishing || isStarting}
                    />
                </div>
            </div>
        </div>
    );
};

export default LandingPage;
