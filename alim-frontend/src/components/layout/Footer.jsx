export default function Footer() {
  return (
    <footer className="bg-secondary text-white py-8 mt-16">
      <div className="max-w-7xl mx-auto px-4 text-sm text-center">
        © {new Date().getFullYear()} ALIMMA — Tous droits réservés.
      </div>
    </footer>
  );
}