import type { DetailedHTMLProps, HTMLAttributes } from 'react'

type MaterialElementProps = DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
    type?: string
    disabled?: boolean
    checked?: boolean
    selected?: boolean
    value?: string
}

declare module 'react' {
    namespace JSX {
        interface IntrinsicElements {
            'md-icon': MaterialElementProps
            'md-icon-button': MaterialElementProps
            'md-filled-button': MaterialElementProps
            'md-filled-tonal-button': MaterialElementProps
            'md-text-button': MaterialElementProps
            'md-checkbox': MaterialElementProps
        }
    }
}
