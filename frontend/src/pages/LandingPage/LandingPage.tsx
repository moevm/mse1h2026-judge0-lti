import IconButton from '../../UI/IconButton/IconButton';
import styles from './LandingPage.module.scss';

import adminPanelIcon from '../../assets/icons/admin_panel_icon.svg'
import runIcon from '../../assets/icons/run_icon.svg';
import repeatIcon from '../../assets/icons/repeat_icon.svg';

const LandingPage = () => {
    const username: string = "User";
    const title: string = "Задачи на Python (Easy)";
    const description: string = `
        В рамках данного практического блока Вам предстоит выполнить контрольное задание, состоящее из трех задач по программированию на языке Python. Предложенные задачи относятся к легкому уровню сложности и направлены на проверку освоения базовых конструкций языка и алгоритмического мышления.
        Обратите внимание на следующие организационные требования:
        На решение всех трех задач отводится 60 минут. Время исчисляется с момента начала тестирования.
        Для каждой задачи предусмотрено не более трех попыток отправки кода на проверку.
    `

    const handleStart = () => {
        console.log('Начать тестирование');
    };

    const handleRetake = () => {
        console.log('Перепройти тестирование');
    };

    const handleAdminPanel = () => {
        console.log('Открыть админ панель');
    };

    return (
        <div className={styles.landingPageContainer}>
            
            <div className={styles.header}>
                <div className={styles.username}>
                    {`Username: ${username}`}
                </div>
                <IconButton
                    icon={adminPanelIcon}
                    label="Админ-панель"
                    type="adminPanelEntry"
                    onClick={handleAdminPanel}
                />
            </div>

            <div className={styles.mainContainer}>
                <div className={styles.textGroup}>
                    <div className={styles.titleText}>
                        {`${title}`}
                    </div>
                    <div className={styles.descriptionText}>
                        {`${description}`}
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