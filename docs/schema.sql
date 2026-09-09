-- =====================================================================
-- ALIMMA — Marketplace électronique du Cameroun
-- Schéma de base de données PostgreSQL
-- Version 1.0 — Septembre 2026
-- =====================================================================
-- Conventions :
--   - Clés primaires : BIGSERIAL / UUID selon la table
--   - Toutes les tables ont created_at / updated_at (audit minimal)
--   - Suppression logique via colonne "statut" plutôt que DELETE physique
--     pour les entités métier sensibles (annonces, utilisateurs, commandes)
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";        -- requêtes spatiales (recherche par carte)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- recherche floue sur titres/descriptions

-- =====================================================================
-- 1. TYPES ÉNUMÉRÉS
-- =====================================================================

CREATE TYPE role_utilisateur AS ENUM (
    'utilisateur', 'vendeur_pro', 'moderateur', 'livreur', 'administrateur'
);

CREATE TYPE type_vente AS ENUM ('fixe', 'enchere');

CREATE TYPE etat_produit AS ENUM ('neuf', 'occasion');

CREATE TYPE statut_annonce AS ENUM (
    'en_attente_moderation', 'active', 'en_pause', 'rejetee', 'vendue', 'expiree'
);

CREATE TYPE statut_commande AS ENUM (
    'attente_paiement', 'confirmee', 'payee', 'preparee',
    'en_transit', 'livree', 'annulee', 'litige'
);

CREATE TYPE mode_paiement AS ENUM ('mobile_money', 'cod');

CREATE TYPE operateur_mobile_money AS ENUM ('mtn', 'orange');

CREATE TYPE statut_paiement AS ENUM ('en_attente', 'paye', 'echoue', 'rembourse');

CREATE TYPE statut_livraison AS ENUM ('preparee', 'en_transit', 'livree', 'echec');

CREATE TYPE statut_commentaire AS ENUM ('visible', 'masque', 'supprime');

CREATE TYPE type_signalement AS ENUM ('annonce', 'utilisateur', 'commentaire');

CREATE TYPE statut_signalement AS ENUM ('ouvert', 'en_cours', 'traite', 'rejete');

CREATE TYPE type_promo AS ENUM ('globale', 'boutique');


-- =====================================================================
-- 2. UTILISATEURS ET RÔLES
-- =====================================================================

CREATE TABLE utilisateurs (
    id                  BIGSERIAL PRIMARY KEY,
    nom                 VARCHAR(150) NOT NULL,
    email               VARCHAR(255) UNIQUE,
    telephone           VARCHAR(20) UNIQUE NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    role                role_utilisateur NOT NULL DEFAULT 'utilisateur',
    photo_url           TEXT,
    note_moyenne        NUMERIC(2,1) DEFAULT 0.0 CHECK (note_moyenne BETWEEN 0 AND 5),
    nb_avis             INTEGER DEFAULT 0,
    points_parrainage   INTEGER DEFAULT 0,
    code_parrainage     VARCHAR(12) UNIQUE NOT NULL,
    parraine_par_id     BIGINT REFERENCES utilisateurs(id),
    deux_fa_active      BOOLEAN DEFAULT FALSE,
    est_actif           BOOLEAN DEFAULT TRUE,
    derniere_connexion  TIMESTAMPTZ,
    date_inscription    TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_utilisateurs_role ON utilisateurs(role);
CREATE INDEX idx_utilisateurs_telephone ON utilisateurs(telephone);

-- Codes OTP pour la double authentification (2FA)
CREATE TABLE otp_codes (
    id              BIGSERIAL PRIMARY KEY,
    utilisateur_id  BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    code            VARCHAR(6) NOT NULL,
    expire_at       TIMESTAMPTZ NOT NULL,
    utilise         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_otp_utilisateur ON otp_codes(utilisateur_id, utilise);

-- Extension de profil pour les vendeurs Premium / Pro (1-1 avec utilisateurs)
CREATE TABLE profils_vendeur_pro (
    utilisateur_id      BIGINT PRIMARY KEY REFERENCES utilisateurs(id) ON DELETE CASCADE,
    siret_niu           VARCHAR(50),
    nom_boutique        VARCHAR(150) NOT NULL,
    logo_url            TEXT,
    banniere_url        TEXT,
    description_boutique TEXT,
    nb_ventes_total      INTEGER DEFAULT 0,
    est_certifie         BOOLEAN DEFAULT FALSE,
    date_activation       TIMESTAMPTZ DEFAULT now()
);

-- Extension de profil pour les livreurs (1-1 avec utilisateurs)
CREATE TABLE profils_livreur (
    utilisateur_id       BIGINT PRIMARY KEY REFERENCES utilisateurs(id) ON DELETE CASCADE,
    vehicule_info        VARCHAR(100),
    zone_geographique     VARCHAR(150),
    statut_disponibilite  VARCHAR(20) DEFAULT 'disponible'
        CHECK (statut_disponibilite IN ('disponible', 'en_tournee', 'hors_ligne'))
);


-- =====================================================================
-- 3. CATALOGUE : CATÉGORIES, ANNONCES, IMAGES
-- =====================================================================

CREATE TABLE categories (
    id              BIGSERIAL PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL,
    slug            VARCHAR(120) UNIQUE NOT NULL,
    parent_id       BIGINT REFERENCES categories(id),
    icone_url       TEXT,
    ordre_affichage INTEGER DEFAULT 0
);
CREATE INDEX idx_categories_parent ON categories(parent_id);

CREATE TABLE annonces (
    id                  BIGSERIAL PRIMARY KEY,
    vendeur_id          BIGINT NOT NULL REFERENCES utilisateurs(id),
    categorie_id        BIGINT NOT NULL REFERENCES categories(id),
    titre               VARCHAR(200) NOT NULL,
    description          TEXT NOT NULL,
    prix                NUMERIC(12,2) NOT NULL CHECK (prix >= 0),
    type_vente          type_vente NOT NULL DEFAULT 'fixe',
    etat                etat_produit NOT NULL DEFAULT 'occasion',
    ville               VARCHAR(100) NOT NULL,
    quartier            VARCHAR(100),
    localisation        GEOGRAPHY(POINT, 4326),   -- pour la recherche par carte (PostGIS)
    statut              statut_annonce NOT NULL DEFAULT 'en_attente_moderation',
    nb_vues             INTEGER DEFAULT 0,
    date_publication    TIMESTAMPTZ,
    date_expiration     TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_annonces_vendeur ON annonces(vendeur_id);
CREATE INDEX idx_annonces_categorie ON annonces(categorie_id);
CREATE INDEX idx_annonces_statut ON annonces(statut);
CREATE INDEX idx_annonces_localisation ON annonces USING GIST(localisation);
CREATE INDEX idx_annonces_titre_trgm ON annonces USING GIN (titre gin_trgm_ops);

CREATE TABLE annonce_images (
    id          BIGSERIAL PRIMARY KEY,
    annonce_id  BIGINT NOT NULL REFERENCES annonces(id) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    ordre       SMALLINT DEFAULT 0
);
CREATE INDEX idx_annonce_images_annonce ON annonce_images(annonce_id);

-- Enchères (extension 1-1 optionnelle d'une annonce de type "enchere")
CREATE TABLE encheres (
    id                BIGSERIAL PRIMARY KEY,
    annonce_id        BIGINT NOT NULL UNIQUE REFERENCES annonces(id) ON DELETE CASCADE,
    prix_depart       NUMERIC(12,2) NOT NULL,
    montant_actuel    NUMERIC(12,2) NOT NULL,
    pas_enchere       NUMERIC(12,2) NOT NULL DEFAULT 500,
    date_limite       TIMESTAMPTZ NOT NULL,
    gagnant_id        BIGINT REFERENCES utilisateurs(id),
    est_terminee      BOOLEAN DEFAULT FALSE
);

CREATE TABLE enchere_offres (
    id          BIGSERIAL PRIMARY KEY,
    enchere_id  BIGINT NOT NULL REFERENCES encheres(id) ON DELETE CASCADE,
    utilisateur_id BIGINT NOT NULL REFERENCES utilisateurs(id),
    montant     NUMERIC(12,2) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_enchere_offres_enchere ON enchere_offres(enchere_id);


-- =====================================================================
-- 4. COMMANDES, PAIEMENTS, LIVRAISONS
-- =====================================================================

CREATE TABLE commandes (
    id                  BIGSERIAL PRIMARY KEY,
    acheteur_id         BIGINT NOT NULL REFERENCES utilisateurs(id),
    annonce_id          BIGINT NOT NULL REFERENCES annonces(id),
    vendeur_id          BIGINT NOT NULL REFERENCES utilisateurs(id),
    quantite            INTEGER NOT NULL DEFAULT 1,
    montant_produit     NUMERIC(12,2) NOT NULL,
    frais_livraison     NUMERIC(12,2) NOT NULL DEFAULT 0,
    montant_total       NUMERIC(12,2) NOT NULL,
    mode_paiement       mode_paiement NOT NULL,
    statut              statut_commande NOT NULL DEFAULT 'attente_paiement',
    adresse_livraison   TEXT NOT NULL,
    ville_livraison     VARCHAR(100) NOT NULL,
    code_parrainage_utilise VARCHAR(12),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_commandes_acheteur ON commandes(acheteur_id);
CREATE INDEX idx_commandes_vendeur ON commandes(vendeur_id);
CREATE INDEX idx_commandes_statut ON commandes(statut);

CREATE TABLE paiements (
    id                  BIGSERIAL PRIMARY KEY,
    commande_id         BIGINT NOT NULL UNIQUE REFERENCES commandes(id) ON DELETE CASCADE,
    methode             mode_paiement NOT NULL,
    operateur           operateur_mobile_money,
    reference_transaction VARCHAR(100),
    montant             NUMERIC(12,2) NOT NULL,
    statut              statut_paiement NOT NULL DEFAULT 'en_attente',
    paye_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE livraisons (
    id                  BIGSERIAL PRIMARY KEY,
    commande_id         BIGINT NOT NULL UNIQUE REFERENCES commandes(id) ON DELETE CASCADE,
    livreur_id          BIGINT REFERENCES utilisateurs(id),
    statut              statut_livraison NOT NULL DEFAULT 'preparee',
    qr_code             VARCHAR(64) UNIQUE,
    date_prise_en_charge TIMESTAMPTZ,
    date_livraison      TIMESTAMPTZ,
    paiement_cod_confirme BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_livraisons_livreur ON livraisons(livreur_id);
CREATE INDEX idx_livraisons_statut ON livraisons(statut);


-- =====================================================================
-- 5. RÉPUTATION, ENGAGEMENT COMMUNAUTAIRE
-- =====================================================================

CREATE TABLE avis (
    id              BIGSERIAL PRIMARY KEY,
    commande_id     BIGINT NOT NULL REFERENCES commandes(id),
    auteur_id       BIGINT NOT NULL REFERENCES utilisateurs(id),
    vendeur_id      BIGINT NOT NULL REFERENCES utilisateurs(id),
    note            SMALLINT NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (commande_id, auteur_id)
);
CREATE INDEX idx_avis_vendeur ON avis(vendeur_id);

CREATE TABLE follows (
    follower_id     BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    vendeur_id      BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (follower_id, vendeur_id)
);

CREATE TABLE favoris (
    utilisateur_id  BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    annonce_id      BIGINT NOT NULL REFERENCES annonces(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (utilisateur_id, annonce_id)
);

CREATE TABLE commentaires (
    id              BIGSERIAL PRIMARY KEY,
    annonce_id      BIGINT NOT NULL REFERENCES annonces(id) ON DELETE CASCADE,
    utilisateur_id  BIGINT NOT NULL REFERENCES utilisateurs(id),
    contenu         TEXT NOT NULL,
    reponse_vendeur TEXT,
    statut          statut_commentaire NOT NULL DEFAULT 'visible',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_commentaires_annonce ON commentaires(annonce_id);

CREATE TABLE messages (
    id              BIGSERIAL PRIMARY KEY,
    expediteur_id   BIGINT NOT NULL REFERENCES utilisateurs(id),
    destinataire_id BIGINT NOT NULL REFERENCES utilisateurs(id),
    annonce_id      BIGINT REFERENCES annonces(id),
    contenu         TEXT,
    piece_jointe_url TEXT,
    lu              BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_conversation ON messages(expediteur_id, destinataire_id);

CREATE TABLE badges (
    id              BIGSERIAL PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL,
    description_condition TEXT,
    icone_url       TEXT
);

CREATE TABLE utilisateur_badges (
    utilisateur_id  BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    badge_id        BIGINT NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    obtenu_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (utilisateur_id, badge_id)
);

CREATE TABLE parrainages (
    id                      BIGSERIAL PRIMARY KEY,
    parrain_id              BIGINT NOT NULL REFERENCES utilisateurs(id),
    filleul_id              BIGINT NOT NULL UNIQUE REFERENCES utilisateurs(id),
    recompense_utilisee     BOOLEAN DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE alertes_recherche (
    id              BIGSERIAL PRIMARY KEY,
    utilisateur_id  BIGINT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    mots_cles       VARCHAR(200),
    categorie_id    BIGINT REFERENCES categories(id),
    ville           VARCHAR(100),
    prix_max        NUMERIC(12,2),
    est_actif       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_alertes_utilisateur ON alertes_recherche(utilisateur_id);

CREATE TABLE newsletters (
    id          BIGSERIAL PRIMARY KEY,
    sujet       VARCHAR(200) NOT NULL,
    contenu     TEXT NOT NULL,
    envoye_at   TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE newsletter_abonnements (
    utilisateur_id  BIGINT PRIMARY KEY REFERENCES utilisateurs(id) ON DELETE CASCADE,
    abonne          BOOLEAN DEFAULT TRUE,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- =====================================================================
-- 6. STATISTIQUES VENDEUR (matérialisées, recalculées périodiquement)
-- =====================================================================

CREATE TABLE statistiques_vendeur (
    vendeur_id      BIGINT PRIMARY KEY REFERENCES utilisateurs(id) ON DELETE CASCADE,
    nb_vues_total   INTEGER DEFAULT 0,
    nb_ventes_mois  INTEGER DEFAULT 0,
    ca_mois         NUMERIC(14,2) DEFAULT 0,
    taux_conversion NUMERIC(5,2) DEFAULT 0,
    derniere_maj    TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- =====================================================================
-- 7. PROMOTIONS
-- =====================================================================

CREATE TABLE codes_promo (
    id              BIGSERIAL PRIMARY KEY,
    code            VARCHAR(30) UNIQUE NOT NULL,
    type            type_promo NOT NULL,
    vendeur_id      BIGINT REFERENCES utilisateurs(id),   -- NULL si promo globale (admin)
    reduction_pct   NUMERIC(5,2),
    reduction_montant NUMERIC(12,2),
    date_debut      TIMESTAMPTZ NOT NULL,
    date_fin        TIMESTAMPTZ NOT NULL,
    usage_max       INTEGER,
    usage_actuel    INTEGER DEFAULT 0,
    est_actif       BOOLEAN DEFAULT TRUE
);
CREATE INDEX idx_codes_promo_vendeur ON codes_promo(vendeur_id);


-- =====================================================================
-- 8. MODÉRATION & ADMINISTRATION
-- =====================================================================

CREATE TABLE signalements (
    id              BIGSERIAL PRIMARY KEY,
    type            type_signalement NOT NULL,
    cible_id        BIGINT NOT NULL,          -- id de l'annonce / utilisateur / commentaire visé
    signale_par_id  BIGINT NOT NULL REFERENCES utilisateurs(id),
    motif           VARCHAR(150) NOT NULL,
    description     TEXT,
    statut          statut_signalement NOT NULL DEFAULT 'ouvert',
    traite_par_id   BIGINT REFERENCES utilisateurs(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    traite_at       TIMESTAMPTZ
);
CREATE INDEX idx_signalements_statut ON signalements(statut);

CREATE TABLE journal_moderation (
    id              BIGSERIAL PRIMARY KEY,
    moderateur_id   BIGINT NOT NULL REFERENCES utilisateurs(id),
    action          VARCHAR(100) NOT NULL,     -- ex: 'annonce_rejetee', 'commentaire_masque'
    cible_type      VARCHAR(50) NOT NULL,
    cible_id        BIGINT NOT NULL,
    details         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE parametres_site (
    cle             VARCHAR(100) PRIMARY KEY,
    valeur          TEXT NOT NULL,
    description     TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Exemples : 'frais_livraison_defaut', 'cgu_url', 'mentions_legales_url'

-- =====================================================================
-- FIN DU SCRIPT
-- =====================================================================
