import { Icon } from "./Icon";
import { cx } from "./utils";
import { getInitials } from "../../utils/format";

/**
 * Avatar rond : photo ou initiales.
 * size : "s" (32) | "m" (44) | "l" (64) | "xl" (96) | "xxl" (112) · verified : point d’or « vérifié »
 */
export function Avatar({ name = "", src, size = "m", verified = false, className }) {
  const initials = getInitials(name);
  return (
    <span className={cx("ui-avatar", `ui-avatar--${size}`, verified && "ui-avatar--verified", className)}>
      {src ? <img src={src} alt="" /> : initials || <Icon name="person" />}
    </span>
  );
}
