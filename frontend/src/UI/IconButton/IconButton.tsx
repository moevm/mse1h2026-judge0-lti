import styles from "./IconButton.module.scss";

interface IconButtonProps {
    icon: string;
    label: string;
    type?: "run" | "submit";
    onClick?: () => void;
    className?: string;
    disabled?: boolean;
}

const IconButton = ({icon, label, type = "run", onClick, className = "", disabled = false}: IconButtonProps) => (
    <button
        onClick={onClick}
        className={`${styles.iconButton} ${styles[type]} ${className}`}
        disabled={disabled}
    >
        <img src={icon} alt={label}/>
        {label}
    </button>
);

export default IconButton;