import { useState, type CSSProperties, type ReactNode } from 'react'
import styles from './AdminToolbar.module.scss'

export interface FilterOption {
    value: string
    label: string
}

export interface FilterGroup {
    id: string
    title: string
    options: FilterOption[]
}

interface AdminToolbarProps {
    search: string
    onSearchChange: (value: string) => void
    filterGroups: FilterGroup[]
    selectedFilters: Record<string, string | undefined>
    onFilterChange: (groupId: string, value: string | null) => void
    action?: ReactNode
    placeholder?: string
    variant?: 'page' | 'compact'
}

const AdminToolbar = ({
    search,
    onSearchChange,
    filterGroups,
    selectedFilters,
    onFilterChange,
    action,
    placeholder = 'Поиск',
    variant = 'page',
}: AdminToolbarProps) => {
    const [filtersOpen, setFiltersOpen] = useState(false)
    const dialogStyle = { '--filter-columns': filterGroups.length } as CSSProperties

    return (
        <>
            <div className={`${styles.toolbar} ${styles[variant]}`}>
                <label className={styles.search}>
                    <input
                        value={search}
                        onChange={event => onSearchChange(event.target.value)}
                        placeholder={placeholder}
                    />
                    <md-icon>search</md-icon>
                </label>

                <md-filled-tonal-button type="button" onClick={() => setFiltersOpen(true)}>
                    фильтры
                    <md-icon slot="icon">format_color_fill</md-icon>
                </md-filled-tonal-button>

                {action ? <div className={styles.action}>{action}</div> : null}
            </div>

            {filtersOpen ? (
                <div className={styles.overlay} role="presentation" onMouseDown={() => setFiltersOpen(false)}>
                    <section
                        className={styles.filtersDialog}
                        role="dialog"
                        aria-modal="true"
                        onMouseDown={event => event.stopPropagation()}
                    >
                        <header className={styles.filtersHeader}>
                            <h2>Фильтры поиска</h2>
                            <md-icon-button type="button" onClick={() => setFiltersOpen(false)} aria-label="Закрыть фильтры">
                                <md-icon>close</md-icon>
                            </md-icon-button>
                        </header>
                        <div className={styles.filterColumns} style={dialogStyle}>
                            {filterGroups.map(group => (
                                <div className={styles.filterColumn} key={group.id}>
                                    <h3>{group.title}</h3>
                                    {group.options.map(filter => {
                                        const selected = selectedFilters[group.id] === filter.value

                                        return (
                                            <button
                                                key={filter.value}
                                                type="button"
                                                className={selected ? `${styles.menuItem} ${styles.selected}` : styles.menuItem}
                                                onClick={() => onFilterChange(group.id, selected ? null : filter.value)}
                                            >
                                                <span>{filter.label}</span>
                                                {selected ? <md-icon>close</md-icon> : null}
                                            </button>
                                        )
                                    })}
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            ) : null}
        </>
    )
}

export default AdminToolbar
