// Variables pour les données comptables
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1;

// Fonction pour formater les montants
function formatMontant(montant) {
    return new Intl.NumberFormat('fr-FR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(montant);
}

// Fonction pour générer le tableau comptable avec les données
function genererTableauComptable(data) {
    donnees = data.data
    mois = data.periode
    const tbody = document.querySelector('.document-table tbody');

    //console.log('TESTE TBODY => ',tbody)
    if (!tbody) return;

    console.log('Données reçues:', donnees);
    //console.log('TVA', donnees[0].total_TVA)

    // Vider le tableau existant
    tbody.innerHTML = '';

    if (!donnees || donnees.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Aucune donnée disponible pour cette période</td></tr>';
        return;
    }

    // Traiter les données de la requête SQL et les convertir en écritures comptables
    const ecritures = [];

    donnees.forEach(row => {
        const typeFacture = row.Type_Facture;
        const estIntr = row.est_intr === 'INTR';
        const total_HT = parseFloat(row.total_HT);
        const total_TVA = parseFloat(row.total_TVA);
        const moisSelection = row.mois_facture

        if (mois === moisSelection){
            if (typeFacture === 'F') { // Factures
                
                if (estIntr) {
                    ecritures.push({
                        compte: '7075000',
                        libelle: 'VENTES VRAC (INTR)',
                        debit: 0,
                        credit: total_HT,
                        classe: ''
                    });
                } else {
                    ecritures.unshift({
                        compte: '44573',
                        libelle: 'TVA VRAC URCOOPA',
                        debit: 0,
                        credit: total_TVA,
                        classe: ''
                    }),
                    ecritures.push({
                        compte: '7075000',
                        libelle: 'VENTES VRAC',
                        debit: 0,
                        credit: total_HT,
                        classe: ''
                    });
                }
            } else if (typeFacture === 'A') { // Avoirs
                if (estIntr) {
                    ecritures.push({
                        compte: '6075000',
                        libelle: 'ACHATS VRAC (INTR)',
                        debit: total_HT,
                        credit: 0,
                        classe: ''
                    });
                } else {
                    ecritures.unshift({
                        compte: '44563',
                        libelle: 'TVA VRAC URCOOPA',
                        debit: total_TVA,
                        credit: 0,
                        classe: ''
                    }),
                    ecritures.push({
                        compte: '6075000',
                        libelle: 'ACHATS VRAC',
                        debit: total_HT,
                        credit: 0,
                        classe: ''
                    });
                }
            }
        }
        
        
    });

    
    // Calculer la TVA sur les ventes normales (non INTR)
    //const totalVentes = donnees
    //    .filter(row => row.Type_Facture === 'F' && row.est_intr !== 'INTR')
    //    .reduce((sum, row) => sum + parseFloat(row.total_HT), 0);

    // Calculer HT et TVA sur les ventes normales (non INTR)

    //console.log('HT total => ', totalVentes);
    //console.log('TVA totale => ', totalTVA);
    //console.log('TTC total => ', tva);
    //console.log('Voir totalVente => ', totalVentes)
    //const tva = totalVentes * 0.021; // 2.1%
    
    // Ajouter les écritures TVA au début
    /*
    if (donnees[0].total_TVA > 0) {
        ecritures.unshift(
            {
                compte: '44573',
                libelle: 'TVA VRAC URCOOPA',
                debit: 0,
                credit: donnees[0].total_TVA ,
                classe: 'tva-row'
            },
            {
                compte: '44563',
                libelle: 'TVA VRAC URCOOPA',
                debit: donnees[0].total_TVA,
                credit: 0,
                classe: 'tva-row'
            }
        );
    }
    */
    // Générer les lignes du tableau
    ecritures.forEach(ecriture => {
        const row = document.createElement('tr');
        row.className = ecriture.classe;
        console.log('DEBIT -> ',ecriture.debit)
        row.innerHTML = `
            <td></td>
            <td class="center-cell fw-bold">${ecriture.compte}</td>
            <td>${ecriture.libelle}</td>
            <td class="number-cell ${ecriture.debit < 0 ? 'fw-bold text-danger' : ''}">${ecriture.debit < 0 ? formatMontant(ecriture.debit) : ''}</td>
            <td class="number-cell ${ecriture.credit > 0 ? 'fw-bold text-success' : ''}">${ecriture.credit > 0 ? formatMontant(ecriture.credit) : ''}</td>
            <td class="center-cell">EUR</td>
        `;
        
        tbody.appendChild(row);
    });
}

// Fonction pour charger les données d'un mois spécifique
async function chargerDonneesMois(annee, mois) {
    try {
        console.log(`Chargement des données pour ${annee}-${mois}`);

        const response = await fetch(`/api/donnees-comptables/${annee}/${mois}`);
        const data = await response.json();

        console.log('Réponse API:', data);

        if (data.success) {
            console.info('Data.success ok !')
            genererTableauComptable(data);

            // Vérifier que data.data existe et n'est pas vide avant d'accéder aux propriétés
            if (data.data && data.data.length > 0) {
                const moisFacture = data.data[0].mois_facture;
                const totalTVA = data.data[0].total_TVA;
                
                console.log('Mois:', moisFacture);
                console.log('Total TVA:', totalTVA);
            } else {
                console.log('Aucune donnée disponible pour cette période');
            }

            const dateNow = new Date();
            const dateOperation = document.querySelector('.dateOperation');
            const dateEcheance = document.querySelector('.dateEcheance');
            const modalTitle = document.querySelector('#documentComptableModal .modal-title');
            
            if (modalTitle) {
                modalTitle.textContent = `📊 Document Comptable - TVA COLLECTEE 2.1% (${data.periode})`;
            }
        } else {
            console.error('Erreur lors du chargement des données:', data.error);
            alert('Erreur lors du chargement des données: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        alert('Erreur de connexion: ' + error.message);
    }
}

// Fonction pour ajouter le sélecteur de mois 
function ajouterSelecteurMois() {
    const modalHeader = document.querySelector('#documentComptableModal .modal-header');
    console.log('Modal header trouvé:', modalHeader);

    if (modalHeader && !document.getElementById('selecteurMoisComptable')) {
        const selecteurContainer = document.createElement('div');
        selecteurContainer.className = 'd-flex align-items-center gap-2 ms-auto';
        selecteurContainer.innerHTML = `
            <label class="small mb-0 text-muted">Période:</label>
            <select id="selecteurMoisComptable" class="form-select form-select-sm" style="width: 150px;">
                <option value="">Sélectionner un mois</option>
            </select>
        `;

        // Générer les options des 12 derniers mois
        const maintenant = new Date();
        for (let i = 0; i < 12; i++) {
            const date = new Date(maintenant.getFullYear(), maintenant.getMonth() - i, 1);
            //console.log('date apres selection', date)
            const annee = date.getFullYear();
            const mois = date.getMonth() + 1;
            const option = document.createElement('option');
            option.value = `${annee}-${mois}`;
            option.textContent = `${annee}-${mois.toString().padStart(2, '0')}`;
            if (i === 0) option.selected = true; // Sélectionner le mois actuel
            selecteurContainer.querySelector('select').appendChild(option);
        }

        // Insérer avant le bouton de fermeture
        const closeButton = modalHeader.querySelector('#closeDocumentModal');
        modalHeader.insertBefore(selecteurContainer, closeButton);

        // Événement de changement
        document.getElementById('selecteurMoisComptable').addEventListener('change', (event) => {
            const [annee, mois] = event.target.value.split('-');
            console.log('Changement de mois:', annee, mois);
            if (annee && mois) {
                chargerDonneesMois(parseInt(annee), parseInt(mois));
            }
        });

        console.log('Sélecteur de mois ajouté avec succès');
    }
}

// GESTION DU MODAL DOCUMENT COMPTABLE
let bouton_document_comptable = document.querySelector('#documentComptable');

if (bouton_document_comptable) {
    bouton_document_comptable.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();

        console.log('Ouverture du modal comptable');
        console.log('Données comptables disponibles:', donneesComptables);

        // Afficher le modal
        const modal = document.getElementById('documentComptableModal');
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';

            // Ajouter le sélecteur de mois
            ajouterSelecteurMois();

            // Générer le tableau avec les données actuelles ou charger le mois actuel
            if (donneesComptables && donneesComptables.length > 0) {
                genererTableauComptable(donneesComptables);
            } else {
                // Charger les données du mois actuel
                const maintenant = new Date();
                chargerDonneesMois(maintenant.getFullYear(), maintenant.getMonth() + 1);
            }
        }
    });
}

// Fermeture du modal avec le bouton X
const closeDocumentModal = document.getElementById('closeDocumentModal');
if (closeDocumentModal) {
    closeDocumentModal.addEventListener('click', () => {
        fermerModalDocumentComptable();
    });
}

// Fermeture du modal avec le bouton Fermer du footer
const closeDocumentModalFooter = document.getElementById('closeDocumentModalFooter');
if (closeDocumentModalFooter) {
    closeDocumentModalFooter.addEventListener('click', () => {
        fermerModalDocumentComptable();
    });
}

// Fermeture du modal en cliquant à l'extérieur
const documentComptableModal = document.getElementById('documentComptableModal');
if (documentComptableModal) {
    documentComptableModal.addEventListener('click', (event) => {
        if (event.target === documentComptableModal) {
            fermerModalDocumentComptable();
        }
    });
}

// Fermeture avec la touche Échap
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const modal = document.getElementById('documentComptableModal');
        if (modal && modal.style.display === 'block') {
            fermerModalDocumentComptable();
        }
    }
});

// Fonction pour fermer le modal
function fermerModalDocumentComptable() {
    const modal = document.getElementById('documentComptableModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';

        // Supprimer le sélecteur de mois pour éviter les doublons
        const selecteur = document.getElementById('selecteurMoisComptable');
        if (selecteur && selecteur.parentElement) {
            selecteur.parentElement.remove();
        }
    }
}
