import { DEMO_LISTINGS, DEMO_REVIEWS } from "../mocks/sellerDemo";

// ⏸️ Les endpoints « annonces du vendeur » et « avis du vendeur » ne sont pas encore dans la doc API.
// En attendant, ces hooks renvoient des listes vides (ou les données de démo avec ?demo=1 en dev).
// Quand l’API existera, remplacez le corps par un useQuery (voir hooks/usePublicProfile.js).

/** Retour attendu : { data: [{ id, title, price, image, createdAt, sold }], isLoading } */
export function useSellerListings(_sellerId, { demo = false } = {}) {
  return { data: demo ? DEMO_LISTINGS : [], isLoading: false };
}

/** Retour attendu : { data: { distribution: { 5: n, … }, items: [{ id, author, date, rating, text }] }, isLoading } */
export function useSellerReviews(_sellerId, { demo = false } = {}) {
  return { data: demo ? DEMO_REVIEWS : { distribution: null, items: [] }, isLoading: false };
}
