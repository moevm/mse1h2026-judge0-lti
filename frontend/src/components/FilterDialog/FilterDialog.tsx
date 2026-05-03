import styles from './FilterDialog.module.scss'

export interface FilterField {
    id: string
    label: string
    type: 'text' | 'date' | 'datetime-local' | 'number' | 'select'
    placeholder?: string
    options?: { value: string; label: string }[]
    min?: number
    max?: number
}

export interface FilterGroup {
    id: string
    title: string
    fields: FilterField[]
}

interface FilterDialogProps {
    isOpen: boolean
    onClose: () => void
    groups: FilterGroup[]
    values: Record<string, string | number | undefined>
    onChange: (fieldId: string, value: string | number | undefined) => void
    onReset?: () => void
}

const FilterDialog = ({
    isOpen,
    onClose,
    groups,
    values,
    onChange,
    onReset,
}: FilterDialogProps) => {
    if (!isOpen) return null

    const handleReset = () => {
        groups.forEach(group => {
            group.fields.forEach(field => {
                onChange(field.id, undefined)
            })
        })
        onReset?.()
    }

    const renderField = (field: FilterField) => {
        const value = values[field.id] ?? ''

        switch (field.type) {
            case 'text':
                return (
                    <input
                        type="text"
                        className={styles.input}
                        placeholder={field.placeholder}
                        value={value}
                        onChange={e =>
                            onChange(field.id, e.target.value || undefined)
                        }
                    />
                )

            case 'date':
                return (
                    <input
                        type="date"
                        className={styles.input}
                        value={value}
                        onChange={e =>
                            onChange(field.id, e.target.value || undefined)
                        }
                    />
                )

            case 'datetime-local':
                return (
                    <input
                        type="datetime-local"
                        className={styles.input}
                        value={value}
                        onChange={e =>
                            onChange(field.id, e.target.value || undefined)
                        }
                    />
                )

            case 'number':
                return (
                    <input
                        type="number"
                        className={styles.input}
                        placeholder={field.placeholder}
                        min={field.min}
                        max={field.max}
                        value={value}
                        onChange={e =>
                            onChange(
                                field.id,
                                e.target.value ? Number(e.target.value) : undefined
                            )
                        }
                    />
                )

            case 'select':
                return (
                    <select
                        className={styles.select}
                        value={value}
                        onChange={e =>
                            onChange(field.id, e.target.value || undefined)
                        }
                    >
                        <option value="">Не выбрано</option>
                        {field.options?.map(opt => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>
                )

            default:
                return null
        }
    }

    return (
        <div className={styles.overlay} onMouseDown={onClose}>
            <div
                className={styles.dialog}
                onMouseDown={e => e.stopPropagation()}
            >
                <div className={styles.header}>
                    <h2>Фильтры</h2>
                    <button className={styles.iconButton} onClick={onClose}>
                        <md-icon>close</md-icon>
                    </button>
                </div>

                <div className={styles.content}>
                    {groups.map(group => (
                        <div className={styles.group} key={group.id}>
                            <h3 className={styles.groupTitle}>
                                {group.title}
                            </h3>

                            <div className={styles.fields}>
                                {group.fields.map(field => (
                                    <div
                                        className={styles.field}
                                        key={field.id}
                                    >
                                        <label className={styles.label}>
                                            {field.label}
                                        </label>
                                        {renderField(field)}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className={styles.footer}>
                    <button className={styles.resetButton} onClick={handleReset}>
                        Сбросить всё
                    </button>
                    <div className={styles.actions}>
                        <button className={styles.cancelButton} onClick={onClose}>
                            Отмена
                        </button>
                        <button className={styles.applyButton} onClick={onClose}>
                            Применить
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default FilterDialog