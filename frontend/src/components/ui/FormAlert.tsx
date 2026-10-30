import { Button } from './Button'
import { Icon } from './Icon'

export interface FormAlertProps {
  message?: string
  onRetry?: () => void
  retrying?: boolean
}

/** Encart rouge en haut du formulaire pour les erreurs serveur (5xx) et réseau. */
export function FormAlert({
  message = 'Envoi impossible pour le moment. Vos saisies sont conservées : réessayez dans quelques instants.',
  onRetry,
  retrying,
}: FormAlertProps) {
  return (
    <div className="ui-alert" role="alert">
      <Icon name="error" filled />
      <p className="ui-alert__text">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} loading={retrying}>
          Réessayer
        </Button>
      )}
    </div>
  )
}
