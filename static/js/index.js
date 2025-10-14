
function recuperationFacture(factures) {
    if (factures) {

        const facturesParNumero = {}; // clé = Numero_Facture

        factures.forEach(f => {
            const numero = f.Numero_Facture;
            if (!facturesParNumero[numero]) {
                facturesParNumero[numero] = [];
            }
            facturesParNumero[numero].push(f);
        });

        // boucle sur factures
        tableauAdherent(facturesParNumero, etat_facture_valider)

        /*let bouton_row = document.querySelectorAll('.ligneRow')
        //console.log(bouton_row)
        if (bouton_row) {
            bouton_row.forEach(row => {
                row.addEventListener('click', (event) => {
                    const index = row.dataset.index;
                    const facture = factures[index];
                    console.log('FACTURE CLIQUÉE:', facture);
    
                    loadPageValidation(facture);
                });
            });
        }*/

        // bouton facture a traiter
        if (bouton_Factures_A_Traiter) {
            bouton_Factures_A_Traiter.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                if (tcaption) {
                    tcaption.innerHTML = 'A traiter'
                }
                etat_facture_valider = 0;
                tbody.innerHTML = '';
                tableauAdherent(facturesParNumero, etat_facture_valider);
            });
        }

        // je vais ecouter lors des clics 
        if (bouton_avoirs) {
            bouton_avoirs.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                if (tcaption) {
                    tcaption.innerHTML = 'Tous les avoirs'
                }
                etat_facture_valider = 0
                loadPageFactureAvoir(facturesParNumero, etat_facture_valider); // Passer toutes les factures
            });
        }

        // traitement des information recuperer
        if (bouton_Factures_Valider) {
            bouton_Factures_Valider.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                if (tcaption) {
                    tcaption.innerHTML = 'Déjà validées'
                }
                //console.log('ETAT 1')
                etat_facture_valider = 1;
                loadPageFactureValider(facturesParNumero, etat_facture_valider);
            });
        }

        // Traitement client adherent
        if (bouton_Factures_Client_Adherent) {
            bouton_Factures_Client_Adherent.addEventListener('click', (event) => {
                event.preventDefault();
                event.preventDefault();
                if (tcaption) {
                    tcaption.innerHTML = 'Les clients adhérents'
                }
                etat_facture_valider = 0;
                loadPageFactureClientAdherent(facturesParNumero, etat_facture_valider)
            });
        }

        // Traitement bouton_Factures_Client_Non_Adherent 
        if (bouton_Factures_Client_Non_Adherent) {
            bouton_Factures_Client_Non_Adherent.addEventListener('click', (event) => {
                event.preventDefault();
                event.preventDefault();
                if (tcaption) {
                    tcaption.innerHTML = 'Les clients non adhérents'
                }
                etat_facture_valider = 0;
                loadPageFactureClientNonAdherent(facturesParNumero, etat_facture_valider)
            });
        }

        // Traitement bouton_Factures_Client_Inconnu
        if (bouton_Factures_Client_Inconnu) {
            bouton_Factures_Client_Inconnu.addEventListener('click', (event) => {
                event.preventDefault();
                event.preventDefault();
                if (tcaption) {
                    tcaption.innerHTML = 'Les clients inconnu'
                }
                etat_facture_valider = 0;
                loadPageFactureClientInconnu(facturesParNumero, etat_facture_valider)
            });
        }

        // traitement facture par date
        // filtre par dates
        const dateFiltre = document.getElementById('dateInput');
        const moisSet = new Set();

        // extraire les mois
        factures.forEach(f => {
            //console.log('TESTE FACTURE -> ',f)
            const dateFacturation = new Date(f.Date_Facture);
            //console.log('TESTE DATE -> ',dateFacturation) 
            const moisAnnee = `${dateFacturation.getFullYear()}-${(dateFacturation.getMonth() + 1).toString().padStart(2, '0')}`;
            //console.log('TESTE mois Années -> ', moisAnnee)
            moisSet.add(moisAnnee);
        });

        //console.log('moisSet -> ', moisSet)

        // trier les mois récents en premier
        const moisList = Array.from(moisSet).sort().reverse();

        // ajouter dans le select
        moisList.forEach(mois => {
            const option = document.createElement('option');
            option.value = mois;
            option.textContent = `📅 ${mois}`;
            dateFiltre.appendChild(option);
        });


        dateFiltre.addEventListener('change', (event) => {
            const valeurMois = event.target.value;

            tbody.innerHTML = '';

            const facturesFiltrées = {};
            for (let numero in facturesParNumero) {
                const lignes = facturesParNumero[numero];
                const dateFacturation = new Date(lignes[0].Date_Facture);
                const moisAnnee = `${dateFacturation.getFullYear()}-${(dateFacturation.getMonth() + 1).toString().padStart(2, '0')}`;

                //console.log('lignes -> ', lignes )
                //console.log('dateFacturation -> ', dateFacturation )
                //console.log('mmoisAnnée -> ', moisAnnee )
                //console.log('valuer mois -> ' ,valeurMois)

                if (valeurMois === "" || moisAnnee === valeurMois) {
                    facturesFiltrées[numero] = lignes;
                }
            }

            //console.log('factures filtrés -> ', facturesFiltrées) 
            tableauAdherent(facturesFiltrées, etat_facture_valider);

        });

    }

}
// je recupere mes boutons
let bouton_facture = document.querySelector('#touslesfactures');
let bouton_avoirs = document.querySelector('#touslesavoirs');
let bouton_Factures_Valider = document.querySelector('#aValider');
let bouton_Factures_A_Traiter = document.querySelector('#aTraiter');
let bouton_Factures_Client_Adherent = document.querySelector('#clientAdherent');
let bouton_Factures_Client_Non_Adherent = document.querySelector('#clientNonAdherent');
let bouton_Factures_Client_Inconnu = document.querySelector('#clientInconnu');
let bouton_donnees_inconnu = document.querySelector('#documentInconnu');
let bouton_dashboard = document.querySelector('#dashboard');

let etat_facture_valider = 0

/****/
//document.querySelector('#TTC').innerHTML = ' TTC : ' + montant_total_ttc;
//document.querySelector('#HT').innerHTML = ' HT : ' + montant_total_ht;

//TABLEAU 
const tbody = document.getElementById('TableauValeur');
const tcaption = document.getElementById('tableCaption');


// function recherche tableau
function myFunction() {
    const input = document.getElementById("myInput");
    const filter = input.value.toUpperCase();
    const table = document.getElementById("myTable");
    const tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        // i = 1 pour ignorer l'en-tête
        const tds = tr[i].getElementsByTagName("td");
        let rowMatches = false;

        for (let j = 0; j < tds.length; j++) {
            const td = tds[j];
            if (td) {
                const txtValue = td.textContent || td.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    rowMatches = true;
                    break;
                }
            }
        }

        tr[i].style.display = rowMatches ? "" : "none";
    }
}

// Ajouter l'événement au bouton "Valider tout"
document.addEventListener('DOMContentLoaded', function () {

    const boutonValiderTout = document.getElementById('ValiderTotal');
    if (boutonValiderTout) {
        boutonValiderTout.addEventListener('click', validerToutesFactures);
    }

    // Calculer les totaux au chargement initial
    calculerTotaux();

    // Mettre à jour les totaux après chaque filtrage
    const originalMyFunction = window.myFunction;
    window.myFunction = function () {
        originalMyFunction();
        mettreAJourTotauxApresFiltre();
    };

    // Mettre à jour les totaux après les filtres par boutons
    document.querySelectorAll('[id^="aTraiter"], [id^="aValider"], [id^="client"]').forEach(btn => {
        btn.addEventListener('click', mettreAJourTotauxApresFiltre);
    });

    // Mettre à jour les totaux après le filtre par date
    const dateInput = document.getElementById('dateInput');
    if (dateInput) {
        dateInput.addEventListener('change', mettreAJourTotauxApresFiltre);
    }

    const buttons = document.querySelectorAll('.btn-outline-warning, .btn-outline-success, .btn-outline-primary, .btn-outline-secondary, .btn-outline-danger');

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            // Retirer active de tous les boutons
            buttons.forEach(btn => btn.classList.remove('active'));

            // Ajouter active au bouton cliqué
            this.classList.add('active');

            // Votre logique de filtrage ici
            console.log('Bouton cliqué:', this.id);
        });
    });
});

bouton_donnees_inconnu.addEventListener('click', (event) => {

    //alert('BOUTON FACTURES CLICKER')
    console.log('Bouton cliqué')
    event.preventDefault();
    event.stopPropagation();

    showLoader();
    ouverturePageInconnu();
    hideLoader()

});

bouton_dashboard.addEventListener('click', (event) => {

    //alert('BOUTON FACTURES CLICKER')
    console.log('Bouton cliqué')
    event.preventDefault();
    event.stopPropagation();

    showLoader();
    ouverturePageDashboard();
    hideLoader()

});


