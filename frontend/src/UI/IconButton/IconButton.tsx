import styles from "./IconButton.module.scss";

interface IconButtonProps {
  icon: string;
  label: string;
  type?: "run" | "submit";
  onClick?: () => void;
}

const IconButton = ({ icon, label, type = "run", onClick }: IconButtonProps) => (
  <button onClick={onClick} className={`${styles.iconButton} ${styles[type]}`}>
    <img src={icon} alt={label} />
    {label}
  </button>
);

export default IconButton;