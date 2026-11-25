import { useId } from "react";

/** Generate accessible ids and described-by values for a field. */
export function useFieldA11y({ id, hint, error, success }) {
  const auto = useId();
  const base = id ?? auto;
  const msgId = `${base}-msg`;
  return { id: base, msgId, describedBy: error || success || hint ? msgId : undefined };
}
