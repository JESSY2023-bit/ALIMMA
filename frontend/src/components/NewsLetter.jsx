// components/NewsletterForm.jsx
export default function NewsletterForm() {
  return (
    <div className="w-full max-w-2xl flex flex-col items-center text-center">
      <h3 className="font-bold text-gray-900 text-sm uppercase mb-4 tracking-wide">
        Abonnez-vous et bénéficiez de 10 % de réduction sur votre première commande.
      </h3>
      <form 
        className="w-full flex flex-col sm:flex-row items-center border-b border-gray-300 pb-2 gap-2 sm:gap-0" 
        onSubmit={(e) => e.preventDefault()}
      >
        <input
          type="email"
          placeholder="Saisissez votre adresse e-mail"
          className="flex-1 w-full bg-transparent outline-none text-sm placeholder-gray-500 text-gray-800 text-center sm:text-left px-2"
          required
        />
        <button 
          type="submit" 
          className="font-bold text-sm uppercase text-[#2B4C7E] hover:text-[#1a3154] transition-colors whitespace-nowrap sm:ml-4"
        >
          S'abonner
        </button>
      </form>
      <p className="text-xs text-gray-500 mt-2">
        En vous abonnant, vous acceptez notre{' '}
        <a href="#" className="underline hover:text-gray-700">
          politique
        </a>
      </p>
    </div>
  );
}