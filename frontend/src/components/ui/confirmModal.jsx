// src/components/ui/ConfirmModal.jsx
import { FaExclamationTriangle } from "react-icons/fa";

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmLabel = "Confirmer",
  cancelLabel = "Annuler",
  onConfirm,
  onCancel,
  isPending = false,
  variant = "danger",
}) {
  if (!isOpen) return null;

  const confirmClasses =
    variant === "danger"
      ? "bg-red-500 hover:bg-red-600 text-white"
      : "bg-primary hover:bg-primary-dark text-white";

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
      onClick={onCancel}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-center w-14 h-14 rounded-full bg-red-100 mx-auto mb-4">
          <FaExclamationTriangle className="text-red-500 text-2xl" />
        </div>

        <h3 className="text-xl font-bold text-gray-900 text-center mb-2">
          {title}
        </h3>

        <p className="text-sm text-gray-500 text-center mb-6">{message}</p>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={isPending}
            className="flex-1 px-4 py-2.5 rounded-lg border border-gray-200 text-gray-700 font-semibold text-sm hover:bg-gray-50 transition disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            disabled={isPending}
            className={`flex-1 px-4 py-2.5 rounded-lg font-semibold text-sm transition disabled:opacity-50 ${confirmClasses}`}
          >
            {isPending ? "..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}