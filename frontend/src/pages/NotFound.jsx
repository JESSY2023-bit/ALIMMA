
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="max-w-2xl mx-auto px-4 py-24 text-center">
      <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
      <p className="text-secondary-light mb-8">
        Oups, cette page n'existe pas.
      </p>
      <Link to="/" className="btn-primary">
        Retour à l'accueil
      </Link>
    </section>
  );
}