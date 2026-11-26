import { Icon, IconButton, Logo } from "../components/ui";

/**
 * Mise en page des parcours en étapes (code SMS, mot de passe oublié).
 *  steps : ["Numéro", "Code", …] (facultatif) · step : étape courante (1-based)
 *  onBack : flèche retour (mobile) · headerRight : contenu à droite de l’en-tête desktop
 *  icon / iconTone ("error") : pastille d’icône · centered : texte centré sur desktop
 * Les enfants fournissent leurs blocs `.flow__content` et `.flow__actions`
 * (dans un `<form className="flow__form">` si besoin).
 */
export default function FlowLayout({ steps, step = 1, onBack, headerRight, icon, iconTone, title, subtitle, centered, children }) {
  const showProgress = steps && step < steps.length;
  return (
    <div className="flow">
      <header className="flow__header">
        <div className="container flow__header-in">
          <Logo />
          {steps ? (
            <ol className="stepper" aria-label="Étapes">
              {steps.map((label, i) => {
                const n = i + 1;
                const state = n < step ? "done" : n === step ? "current" : "todo";
                return (
                  <li key={label} data-state={state} aria-current={state === "current" ? "step" : undefined}>
                    <span className="stepper__dot">{state === "done" ? <Icon name="check" /> : n}</span>
                    {label}
                  </li>
                );
              })}
            </ol>
          ) : (
            <span />
          )}
          {headerRight}
        </div>
      </header>

      <div className="flow__top">
        {onBack && <IconButton icon="arrow_back" variant="ghost" aria-label="Retour" onClick={onBack} />}
        {showProgress && (
          <div
            className="flow__progress"
            role="progressbar"
            aria-valuemin={1}
            aria-valuemax={steps.length}
            aria-valuenow={step}
            aria-label={`Étape ${step} sur ${steps.length}`}
          >
            <span style={{ width: `${(step / steps.length) * 100}%` }} />
          </div>
        )}
      </div>

      <main className="flow__body">
        <section className="flow__card" data-align={centered ? "center" : undefined}>
          {icon && (
            <span className="flow__tile" data-tone={iconTone}>
              <Icon name={icon} size={26} />
            </span>
          )}
          {title && <h1 className="flow__title">{title}</h1>}
          {subtitle && <p className="flow__sub">{subtitle}</p>}
          {children}
        </section>
      </main>
    </div>
  );
}
