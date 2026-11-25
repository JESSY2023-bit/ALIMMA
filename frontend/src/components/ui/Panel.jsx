import { cx } from "./utils";

/** Panneau blanc. anchor : coin « ancre » signature (20/20/20/4). */
export function Panel({ as: Tag = "section", anchor = false, className, children, ...rest }) {
  return (
    <Tag className={cx("panel", anchor && "panel--anchor", className)} {...rest}>
      {children}
    </Tag>
  );
}
