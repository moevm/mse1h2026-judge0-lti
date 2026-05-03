import { useState } from 'react'
import styles from './AdminToolbar.module.scss'
import FilterDialog, { type FilterGroup } from '../FilterDialog/FilterDialog'

export type FilterValues = Record<string, string | number | undefined>

interface AdminToolbarProps {
    search: string
    onSearchChange: (value: string) => void

    filterGroups: FilterGroup[]
    filterValues: FilterValues
    onFilterChange: (fieldId: string, value: string | number | undefined) => void

    action?: React.ReactNode
    placeholder?: string
    variant?: 'page' | 'compact'
    showFilters?: boolean
}

const AdminToolbar = ({
    search,
    onSearchChange,
    filterGroups,
    filterValues,
    onFilterChange,
    action,
    placeholder = 'Поиск...',
    variant = 'page',
    showFilters = true,
}: AdminToolbarProps) => {
    const [filtersOpen, setFiltersOpen] = useState(false)

    return (
        <>
            <div className={`${styles.toolbar} ${styles[variant]}`}>
                <div className={styles.search}>
                    <md-icon>search</md-icon>
                    <input
                        value={search}
                        onChange={e => onSearchChange(e.target.value)}
                        placeholder={placeholder}
                    />
                </div>

                {showFilters && filterGroups.length > 0 && (
                    <md-filled-tonal-button onClick={() => setFiltersOpen(true)}>
                        фильтры
                        <md-icon slot="icon">tune</md-icon>
                    </md-filled-tonal-button>
                )}

                {action && <div className={styles.action}>{action}</div>}
            </div>

            <FilterDialog
                isOpen={filtersOpen}
                onClose={() => setFiltersOpen(false)}
                groups={filterGroups}
                values={filterValues}
                onChange={onFilterChange}
            />
        </>
    )
}

export default AdminToolbar