import { useEffect } from 'react'
import styles from './ConfirmModal.module.scss'

interface ConfirmModalProps {
    isOpen: boolean
    title: string
    message: string
    confirmText?: string
    cancelText?: string
    confirmVariant?: 'danger' | 'primary' | 'secondary'
    isLoading?: boolean
    onConfirm: () => void
    onCancel: () => void
}

const ConfirmModal = ({
    isOpen,
    title,
    message,
    confirmText = 'Удалить',
    cancelText = 'Отмена',
    confirmVariant = 'danger',
    isLoading = false,
    onConfirm,
    onCancel,
}: ConfirmModalProps) => {
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isOpen && !isLoading) {
                onCancel()
            }
        }

        if (isOpen) {
            document.addEventListener('keydown', handleEscape)
            document.body.style.overflow = 'hidden'
        }

        return () => {
            document.removeEventListener('keydown', handleEscape)
            document.body.style.overflow = 'unset'
        }
    }, [isOpen, onCancel, isLoading])
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden'
        } else {
            document.body.style.overflow = ''
        }

        return () => {
            document.body.style.overflow = ''
        }
    }, [isOpen])

    if (!isOpen) return null

    const handleOverlayClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget && !isLoading) {
            onCancel()
        }
    }


    const getConfirmButtonClass = () => {
        switch (confirmVariant) {
            case 'danger':
                return styles.confirmDanger
            case 'primary':
                return styles.confirmPrimary
            case 'secondary':
                return styles.confirmSecondary
            default:
                return styles.confirmDanger
        }
    }

    const getConfirmButtonText = () => {
        if (isLoading) {
            return confirmVariant === 'danger' ? 'Удаление...' : 'Сохранение...'
        }
        return confirmText
    }

    return (
        <div className={styles.overlay} onClick={handleOverlayClick}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>{title}</h3>
                    <button
                        className={styles.closeButton}
                        onClick={onCancel}
                        disabled={isLoading}
                    >
                        <md-icon>close</md-icon>
                    </button>
                </div>

                <div className={styles.content}>
                    <p>{message}</p>
                </div>

                <div className={styles.footer}>
                    <button
                        className={styles.cancelButton}
                        onClick={onCancel}
                        disabled={isLoading}
                    >
                        {cancelText}
                    </button>
                    <button
                        className={getConfirmButtonClass()}
                        onClick={onConfirm}
                        disabled={isLoading}
                    >
                        {getConfirmButtonText()}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ConfirmModal