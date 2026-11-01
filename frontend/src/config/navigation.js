/** Navigation du site : une seule source pour la barre de catégories, le menu mobile, la recherche et le pied de page. */

export const CATEGORIES = [
  { slug: "telephones", label: "Téléphones", icon: "smartphone" },
  { slug: "informatique", label: "Informatique", icon: "laptop_mac" },
  { slug: "mode-beaute", label: "Mode & beauté", icon: "checkroom" },
  { slug: "maison", label: "Maison", icon: "chair" },
  { slug: "electromenager", label: "Électroménager", icon: "kitchen" },
  { slug: "vehicules", label: "Véhicules", icon: "directions_car" },
];

export const categoryPath = (slug) => `/categorie/${slug}`;

export const HIGHLIGHTS = [
  { label: "Ventes flash", to: "/ventes-flash", icon: "bolt", tone: "flash" },
  { label: "Enchères", to: "/encheres", icon: "gavel" },
];

export const TOPBAR_LINKS = [
  { label: "Vendre sur ALIMMA", to: "/publier" },
  { label: "Suivre ma commande", to: "/suivi-commande" },
  { label: "Aide", to: "/aide" },
];

export const FOOTER_COLUMNS = [
  {
    title: "Acheter",
    links: [
      { label: "Toutes les catégories", to: "/categories" },
      { label: "Ventes flash", to: "/ventes-flash" },
      { label: "Enchères", to: "/encheres" },
      { label: "Recherche sur la carte", to: "/carte" },
    ],
  },
  {
    title: "Vendre",
    links: [
      { label: "Publier une annonce", to: "/publier" },
      { label: "Devenir vendeur Pro", to: "/vendeur-pro" },
      { label: "Parrainage", to: "/parrainage" },
    ],
  },
  {
    title: "Aide & légal",
    links: [
      { label: "Suivre ma commande", to: "/suivi-commande" },
      { label: "Conditions générales (CGU)", to: "/cgu" },
      { label: "Mentions légales", to: "/mentions-legales" },
      { label: "Politique de confidentialité", to: "/confidentialite" },
    ],
  },
];

export const formatFcfa = (amount = 0) => `${new Intl.NumberFormat("fr-FR").format(amount)} FCFA`;
