import type { CSSProperties } from 'react'

const palettes = [
    ['#f2e7fe', '#6750a4', '#ffb4ab', '#cac4d0'],
    ['#e7f4ff', '#006a6a', '#7dd8d0', '#b8c9d9'],
    ['#fff0d6', '#7d5260', '#ffd8e4', '#d0bcff'],
    ['#eaf7df', '#386a20', '#b8e986', '#c4c7c5'],
    ['#f7e5ee', '#984061', '#ffb1c8', '#d6c3cd'],
    ['#e8def8', '#4a4458', '#f4bf4f', '#b9c6ff'],
    ['#dff5ef', '#146c5f', '#f7c8a3', '#9ad5ca'],
    ['#f0f2ff', '#4658a9', '#a8c7fa', '#ffd6a5'],
]

export const getGeneratedArtworkStyle = (seed: string | number) => {
    const value = String(seed)
    const hash = [...value].reduce((total, char, index) => total + char.charCodeAt(0) * (index + 3), 0)
    const palette = palettes[hash % palettes.length]

    return {
        '--art-bg': palette[0],
        '--art-primary': palette[1],
        '--art-secondary': palette[2],
        '--art-muted': palette[3],
        '--art-variant': `variant-${hash % 4}`,
        '--art-rotate-a': `${(hash % 40) - 20}deg`,
        '--art-rotate-b': `${((hash >> 2) % 52) - 26}deg`,
        '--art-x-a': `${20 + (hash % 44)}%`,
        '--art-y-a': `${10 + ((hash >> 1) % 28)}%`,
        '--art-x-b': `${14 + ((hash >> 3) % 48)}%`,
        '--art-y-b': `${48 + ((hash >> 4) % 26)}%`,
        '--art-x-c': `${46 + ((hash >> 5) % 28)}%`,
        '--art-y-c': `${36 + ((hash >> 6) % 34)}%`,
        '--art-size-a': `${18 + ((hash >> 1) % 20)}%`,
        '--art-size-b': `${16 + ((hash >> 3) % 18)}%`,
        '--art-size-c': `${18 + ((hash >> 5) % 22)}%`,
        '--art-scale-a': `${0.68 + (hash % 13) / 18}`,
        '--art-scale-b': `${0.7 + ((hash >> 2) % 12) / 18}`,
        '--art-scale-c': `${0.68 + ((hash >> 4) % 13) / 18}`,
        '--art-orbit-size': `${42 + ((hash >> 3) % 24)}%`,
        '--art-orbit-x': `${-18 + ((hash >> 5) % 20)}%`,
        '--art-orbit-y': `${-22 + ((hash >> 7) % 18)}%`,
        '--art-radius-a': `${8 + (hash % 22)}px`,
        '--art-radius-b': `${4 + ((hash >> 3) % 18)}px`,
        '--art-opacity-a': `${0.72 + (hash % 4) / 10}`,
        '--art-opacity-b': `${0.54 + ((hash >> 4) % 4) / 10}`,
    } as CSSProperties
}
