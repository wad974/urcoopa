/*
function tableTbody(numero , facture, index) {
    
    // on creer une ligne
    const row = document.createElement('tr');
    row.setAttribute('href', '#');
    row.setAttribute('class', 'ligneRow');
    row.setAttribute('style', 'cursor:pointer');
    row.setAttribute('data-index', index);

    // on creer des  lignes 4
    const cell0 = document.createElement('td');
    //const cellText0 = document.createTextNode(` ${value.Numero_Facture} `);
    const cellText0 = document.createTextNode(` ${numero} `);
    cell0.appendChild(cellText0);
    row.appendChild(cell0);

    console.log(facture)
    facture.forEach((value)=>{
    // on creer des  lignes 1 
    const cell1 = document.createElement('td');
    const cellText1 = document.createTextNode(` ${value.Code_Client} `);
    cell1.appendChild(cellText1);
    row.appendChild(cell1);

    // on creer des  lignes 1.1 
    const cell1_1 = document.createElement('td');
    const cellText1_1 = document.createTextNode(` ${value.Code_Produit} `);
    cell1_1.appendChild(cellText1_1);
    row.appendChild(cell1_1);

    // on creer des  lignes 1.2 
    const cell1_2 = document.createElement('td');
    const cellText1_2 = document.createTextNode(` ${value.Libelle_Produit} `);
    cell1_2.appendChild(cellText1_2);
    row.appendChild(cell1_2);

    // on creer des  lignes 2
    const cell2 = document.createElement('td');
    const cellText2 = document.createTextNode(` ${value.Date_Facture} `);
    cell2.appendChild(cellText2);
    row.appendChild(cell2);

    // on creer des  lignes 3
    const cell21 = document.createElement('td');
    const cellText21 = document.createTextNode(` ${value.Date_Echeance} `);
    cell21.appendChild(cellText21);
    row.appendChild(cell21);

    // on creer des  lignes 4
    const cell22 = document.createElement('td');
    const cellText22 = document.createTextNode(` ${value.Nom_Client} `);
    cell22.appendChild(cellText22);
    row.appendChild(cell22);

    // on creer des  lignes 5
    const cell3 = document.createElement('td');
    const cellText3 = document.createTextNode(` ${Number.parseFloat(value.Montant_HT).toFixed(2)} €`);
    cell3.appendChild(cellText3);
    row.appendChild(cell3);

    // on creer des  lignes 6
    const cell4 = document.createElement('td');
    const cellText4 = document.createTextNode(` ${Number.parseFloat(value.Montant_TTC).toFixed(2)} €`);
    cell4.appendChild(cellText4);
    row.appendChild(cell4);
        });
    // add tableau
    tbody.appendChild(row);
}*/

//const { StrictMode } = require("react");

function formaterMontant(montant) {
    return montant.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Fonction pour calculer et mettre à jour les totaux
function calculerTotaux() {
    const rows = document.querySelectorAll('#myTable tbody tr:not([style*="display: none"])');
    let totalHT = 0;
    let totalTTC = 0;
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            // Extraire le montant TTC de la dernière colonne (enlever le symbole €)
            const montantTTC = parseFloat(cells[5].textContent.replace('€', '').trim());
            if (!isNaN(montantTTC)) {
                totalTTC += montantTTC;
                // Calculer le HT approximatif (en supposant 20% de TVA)
                // Calculer le HT approximatif (en supposant 2.10% de TVA)
                totalHT += montantTTC / 1.021;
            }
        }
    });
    
    // Mettre à jour les totaux dans le footer
    document.getElementById('htFooter').textContent = formaterMontant(totalHT) + ' €';
    document.getElementById('ttcFooter').textContent = formaterMontant(totalTTC) + ' €';
    
    return { totalHT, totalTTC };
}

// Fonction pour valider toutes les factures visibles
function validerToutesFactures() {
    const confirmation = confirm(
        `⚠️ Êtes-vous sûr de vouloir valider TOUTES les factures affichées ?\n\n` +
        `📊 ${numerosFactures.length} factures validées\n` +
        `💰 Total HT validé : ${totaux.formaterMontant(totalHT)} €\n` +
        `💰 Total TTC validé : ${totaux.formaterMontant(totalTTC)} €`);
    
    if (!confirmation) return;
    
    showLoader(); // Afficher le loader
    
    // Récupérer toutes les lignes visibles (non masquées par les filtres)
    const rows = document.querySelectorAll('#myTable tbody tr:not([style*="display: none"])');
    const numerosFactures = [];
    
    rows.forEach(row => {
        const numeroFacture = row.querySelector('td:first-child').textContent.trim();
        if (numeroFacture) {
            numerosFactures.push(numeroFacture);
        }
    });
    
    if (numerosFactures.length === 0) {
        alert("❌ Aucune facture à valider !");
        hideLoader();
        return;
    }
    
    // Calculer le total avant validation
    const totaux = calculerTotaux();
    
    // Appel AJAX pour valider toutes les factures
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        hideLoader();
        
        if (this.status === 200) {
            const response = JSON.parse(this.responseText);
            
            // Afficher un message de succès avec les totaux
            alert(`✅ Validation réussie !\n\n` +
                `📊 ${numerosFactures.length} factures validées\n` +
                `💰 Total HT validé : ${totaux.formaterMontant(totalHT) } €\n` +
                `💰 Total TTC validé : ${totaux.formaterMontant(totalTTC) } €`);
            
            // Actualiser la page ou mettre à jour l'affichage
            location.reload();
        } else {
            const errorResponse = JSON.parse(this.responseText);
            alert(`❌ Erreur lors de la validation : ${errorResponse.message}`);
        }
    };
    
    xhttp.onerror = function() {
        hideLoader();
        alert("❌ Erreur de connexion lors de la validation !");
    };
    
    // Envoyer les données au backend
    xhttp.open("POST", "/valider-toutes-factures", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify({
        factures: numerosFactures,
        totalHT: totaux.totalHT,
        totalTTC: totaux.totalTTC
    }));
}

// Fonction pour mettre à jour les totaux en temps réel lors des filtres
function mettreAJourTotauxApresFiltre() {
    // Attendre un peu que le DOM soit mis à jour
    setTimeout(() => {
        calculerTotaux();
    }, 100);
}



function tableTbody(lignes, index, etat) {
    const facture = lignes[0]; // la première ligne représente les infos globales

    const row = document.createElement('tr');
    row.setAttribute('class', 'ligneRow');
    row.setAttribute('style', 'cursor:pointer');
    row.setAttribute('data-index', index);
    row.setAttribute('data-numero', facture.Numero_Facture); // utile pour le clic

    const cell0 = document.createElement('td');
    cell0.textContent = facture.Numero_Facture;
    row.appendChild(cell0);

    const cell1 = document.createElement('td');
    cell1.textContent = facture.Code_Client;
    row.appendChild(cell1);

    const cell2 = document.createElement('td');
    cell2.textContent = facture.Date_Facture;
    row.appendChild(cell2);

    const cell3 = document.createElement('td');
    cell3.textContent = facture.Date_Echeance;
    row.appendChild(cell3);

    const cell4 = document.createElement('td');
    cell4.textContent = facture.Nom_Client;;
    row.appendChild(cell4);
    /*
    const cell4 = document.createElement('td');
    cell4.textContent = Number.parseFloat(facture.Montant_HT).toFixed(2) + ' €';
    row.appendChild(cell4);
    */

    const cell5 = document.createElement('td');
    cell5.textContent = Number.parseFloat(facture.Montant_TTC).toFixed(2) + ' €';
    row.appendChild(cell5);

    tbody.appendChild(row);

    // Événement au clic : envoyer toutes les lignes de la facture
    console.log('ETAT BOUTON DANS TBODY', etat)
    row.addEventListener('click', () => {
        loadPageValidation(lignes, etat); // toutes les lignes de la facture
    });
}

/*FUNCTION TABLEAU BODY TOUS LES FACTURES*/
function tableauAdherent(facturesParNumero, etat) {
    //console.log('VALUE : ', facturesParNumero);
    let compteur = 0
    //boucle sur factures
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {

        let factureValider = null
        let typeFacture = null

        value.forEach((ligne) => {
            //console.log(ligne.facture_valider)

            factureValider = ligne.facture_valider
            typeFacture = ligne.Type_Facture
        });

        if (factureValider == etat && typeFacture == 'F' || factureValider == null) {
            //console.log(value)
            compteur++
            tableTbody( value, index, etat);
        }
    })

    //Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

    
}


/*FUNCTION TABLEAU AVOIR*/
function tableauAdherentAvoirs(facturesParNumero, etat) {
    //boucle sur factures
    let compteur = 0
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {

        let factureValider = null
        let typeFacture = null

        value.forEach((ligne ) => {
            //console.log(ligne.facture_valider)

            factureValider = ligne.facture_valider
            typeFacture = ligne.Type_Facture
        });

        if (factureValider == etat && typeFacture == 'A' ) {
            //console.log(value)
            compteur++
            tableTbody( value, index, etat);
        } else if (typeFacture == 'A' && factureValider == null) {
            //console.log(value)
            compteur++
            tableTbody( value, index, etat);
        }

    })

    //Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

}

function tableauAdherentFactureValider(facturesParNumero, etat) {
    //console.log('VALUE : ', facturesParNumero);
    let compteur = 0
    //boucle sur factures
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {

        let factureValider = null
        let typeFacture = null

        value.forEach((ligne) => {
            //console.log(ligne.facture_valider)

            factureValider = ligne.facture_valider
            typeFacture = ligne.Type_Facture
        });

        if (factureValider == etat) {
            //console.log(value)
            compteur++
            tableTbody( value, index, etat);
        }
    })

    //Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

}

//CLIENT NON ADHERENT
function tableauClientNonAdherent(facturesParNumero, etat) {
    //console.log('VALUE : ', facturesParNumero);
    let compteur = 0

    //boucle sur factures
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {
        console.log('Value', value)
        let typeClientAdherent = String()
        let idClientAdherent = String()

        value.forEach((ligne) => {
            console.log('ligne',ligne.Code_Client_ODOO)
            typeClientAdherent = ligne.Code_Client_ODOO
            idClientAdherent = ligne.ID_Client_ODOO
            //typeClientAdherent = ligne.facture_valider
            //typeFacture = ligne.Type_Facture
        });

        if (typeClientAdherent.includes('NON ADHERENT')) {
            compteur++; // on ajoute une facture traitée
            tableTbody(value, index, etat);
        }
    })

    // Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

}

// CLIENT ADHERENT
function tableauClientAdherent(facturesParNumero, etat) {
    //console.log('VALUE : ', facturesParNumero);
    let compteur = 0

    //boucle sur factures
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {

        let typeClientAdherent = null
        let idClientAdherent = null

        value.forEach((ligne) => {
            //console.log(ligne.facture_valider)
            typeClientAdherent = ligne.Code_Client_ODOO
            idClientAdherent = ligne.ID_Client_ODOO
            //typeClientAdherent = ligne.facture_valider
            //typeFacture = ligne.Type_Facture
        });

        if (typeClientAdherent.includes('CLIENT')) {
            compteur++; // on ajoute une facture traitée
            tableTbody(value, index, etat);
        }
    })

    // Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

}

//INCONNU
function tableauClientAdherentInconnu(facturesParNumero, etat) {
    //console.log('VALUE : ', facturesParNumero);
    let compteur = 0

    //boucle sur factures
    Object.entries(facturesParNumero).forEach(([numero,value], index) => {

        let typeClientAdherent = null
        let idClientAdherent = null

        value.forEach((ligne) => {
            //console.log(ligne.facture_valider)
            typeClientAdherent = ligne.Code_Client_ODOO
            idClientAdherent = ligne.ID_Client_ODOO
            //typeClientAdherent = ligne.facture_valider
            //typeFacture = ligne.Type_Facture
        });

        if (idClientAdherent == 0) {
            compteur++; // on ajoute une facture traitée
            tableTbody(value, index, etat);
        }
    })

    // Affichage du total
    document.getElementById('nombreFacture').textContent = `📦 ${compteur} factures trouvées`;

}

// impression
function impression() {
    window.print();
}


// Placeholder actions
function validerFacture(numeroFacture) {
    const confirmation = confirm("Êtes-vous sûr de vouloir valider cette facture ?");

    if (confirmation) {
        // Étape 1 : appel backend pour mise à jour
        const xhttp = new XMLHttpRequest();
        xhttp.onload = function () {
            document.getElementById("validationPage").style.display = 'block';
            document.getElementById("validationPage").innerHTML = this.responseText;
        }
        // Appel pour mise à jour facture
        xhttp.open("POST", `/valider-facture/${encodeURIComponent(numeroFacture)}`, true);
        xhttp.send();

    }

}

// Placeholder actions
function envoyerOdoo(facture) {
    const confirmation = confirm("📝 Êtes-vous sûr de vouloir envoyer cette facture dans Odoo ?");

    if (!confirmation) return;
    showLoader(); // ⏳ Affiche le loader
    // Étape 1 : charger la page de confirmation
    const xhtml = new XMLHttpRequest();
    xhtml.onload = function () {
        document.getElementById("validationPage").style.display = 'block';
        document.getElementById("validationPage").innerHTML = this.responseText;

        // Étape 2 : envoyer la facture vers le backend
        const xdata = new XMLHttpRequest();
        xdata.onload = function () {
            
            response = JSON.parse(this.responseText)
            console.info(response)
            if (this.status == 500){
                document.getElementById("message").innerHTML = '🛑<strong> Erreur : </strong> '+response.message+' <a href="mailto:support.sdpma@sicalait.fr">📧 Contactez le support informatique</a>';
                console.log("Articles non reconnu.");

            }else if (this.status == 200){
                document.getElementById("message").innerHTML = '✅<strong>Succès !</strong> '+response.message;
                console.log("✅ Facture envoyée dans Odoo.");
            }else if (this.status == 511)
            {
                document.getElementById("message").innerHTML = '🛑<strong> Erreur : </strong> '+response.message+' <a href="https://staging-erp.groupe-sicalait.fr/web#cids=19&menu_id=127&action=286&model=res.partner&view_type=form">ℹ️ Créer le client dans Odoo</a>';
                console.error("Client à créer.");
            }
            
            hideLoader(); // ✅ Cache le loader quand terminé
            
        };
        xdata.open("POST", "/create_facture_adherent_odoo", true);
        xdata.setRequestHeader('Content-Type', 'application/json');
        xdata.send(JSON.stringify(facture));
    };

    xhtml.open("GET", "/static/html/adherent_odoo.html", true);
    xhtml.send();
}

/*AJAX PAGE */
function loadPageValidation(lignes, etat) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //console.log('dans lignes' ,lignes)
        let facture = lignes[0];

        //affiche page 
        document.getElementById("validationPage").style.display = 'block';
        document.getElementById("validationPage").innerHTML = this.responseText;

        // header
        document.getElementById("societeFacture").textContent = facture.Societe_Facture;
        document.getElementById("numeroFacture").textContent = facture.Numero_Facture;
        document.getElementById("nomClient").textContent = facture.Nom_Client;
        document.getElementById("codeClient").textContent = facture.Code_Client;

        //details factures
        document.getElementById("typeFacture").textContent = facture.Type_Facture;
        document.getElementById("dateFacture").textContent = facture.Date_Facture;
        document.getElementById("dateEcheance").textContent = facture.Date_Echeance;
        document.getElementById("typeClient").textContent = facture.Type_Client;
        document.getElementById("depotBL").textContent = facture.Depot_BL;
        document.getElementById("blLigne").textContent = `${facture.Numero_BL}`;

        // ARTICLES
        // On cible le tbody du tableau produits (assure-toi qu’il existe dans ton template)
        const tbody = document.querySelector(".product-table tbody");
        tbody.innerHTML = ""; // reset si plusieurs clics
        // Boucle sur toutes les lignes de produit
        lignes.forEach(l => {
            const tr = document.createElement("tr");
            if (l.Qte_Fact_Conv == null)
            {

                tr.innerHTML = `
                <td><span>${l.Code_Produit} - ${l.Libelle_Produit}</span><br> </td>
                <td>${l.Quantite_Facturee} ${l.Unite_Facturee}</td>
                <td>${parseFloat(l.Prix_Unitaire).toFixed(2)} €</td>
                <td>${parseFloat(l.Montant_HT_Ligne).toFixed(2)} €</td>
            `;
            } else {
            tr.innerHTML = `
                <td><span>${l.Code_Produit} - ${l.Libelle_Produit}</span><br> </td>
                <td>${l.Qte_Fact_Conv} </td>
                <td>${parseFloat(l.Prix_Unitaire).toFixed(2)} €</td>
                <td>${parseFloat(l.Montant_HT_Ligne).toFixed(2)} €</td>
            `;}

            tbody.appendChild(tr);
        });


        //MONTANT
        document.getElementById("tauxTVA").textContent = parseFloat(facture.Taux_TVA).toFixed(2);
        document.getElementById("montantHT").textContent = parseFloat(facture.Montant_HT).toFixed(2);
        document.getElementById("montantTTC").textContent = parseFloat(facture.Montant_TTC).toFixed(2);
        document.getElementById("commentaires").textContent = facture.Commentaires || "—";

        // Activation bouton Valider avec la bonne facture
        console.log('VOICI ETAT DE LA FACTURE DANS LOADPAGEVALIDATION', etat)
        if (etat === 1) {
            document.getElementById("boutonValiderFacture").style.display = 'none'
            document.getElementById("boutonEnvoyerOdoo").style.display = 'none'
            console.log('BOUTON VALIDATION NONE')
        }
        document.getElementById("boutonValiderFacture")
            .setAttribute('onclick', `validerFacture(${facture.Numero_Facture})`);
        // Activation bouton Valider avec la bonne facture
        document.getElementById("boutonEnvoyerOdoo").onclick = () => {
        envoyerOdoo(lignes);};

        // fermeture close
        document.getElementById('close').addEventListener('click', (event)=>{
            event.preventDefault()
            event.stopPropagation()
            document.getElementById('validationPage').style.display = 'none';
        });
    };

    //xhttp.open("GET", "/static/html/validation_copy.html", true);
    xhttp.open("GET", "/static/html/validation_copy_copy.html", true);
    xhttp.send();
}


// loadPageFactureValider
function loadPageFactureValider(factures, etat_facture_valider) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //TABLEAU 
        const tbody = document.getElementById('TableauValeur');
        tbody.innerHTML = this.responseText;
        tableauAdherentFactureValider(factures, etat_facture_valider)
        //document.getElementById("demo").innerHTML = this.responseText;
        //boutonRow(bouton_row)
    }
    xhttp.open("GET", "/static/html/tableauBody.html", true);
    xhttp.send();
}

//loadPageFactureAvoir
function loadPageFactureAvoir(facturesParNumero, etat_facture_valider) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //TABLEAU 
        //const tbody = document.getElementById('TableauValeur');
        tbody.innerHTML = this.responseText;
        tableauAdherentAvoirs(facturesParNumero, etat_facture_valider);
        /*
        let bouton_row = document.querySelectorAll('.ligneRow')
        console.log('ici', bouton_row)
        boutonRowBody(bouton_row, factures)*/
        //document.getElementById("demo").innerHTML = this.responseText;
    }
    xhttp.open("GET", "/static/html/tableauBody.html", true);
    xhttp.send();
}

function boutonRowBody(bouton_row, factures) {

    bouton_row.forEach(row => {
        row.addEventListener('click', (event) => {
            const index = row.dataset.index;
            const facture = factures[index];
            //console.log('FACTURE CLIQUÉE:', facture);

            loadPageValidation(facture);
        });
    });
}

// loadPageFactureClientAdherent
function loadPageFactureClientAdherent(factures, etat_facture_valider) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //TABLEAU 
        const tbody = document.getElementById('TableauValeur');
        tbody.innerHTML = this.responseText;
        tableauClientAdherent(factures, etat_facture_valider)
        //document.getElementById("demo").innerHTML = this.responseText;
        //boutonRow(bouton_row)
    }
    xhttp.open("GET", "/static/html/tableauBody.html", true);
    xhttp.send();
}

// loadPageFactureClientNonAdherent
function loadPageFactureClientNonAdherent(factures, etat_facture_valider) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //TABLEAU 
        const tbody = document.getElementById('TableauValeur');
        tbody.innerHTML = this.responseText;
        tableauClientNonAdherent(factures, etat_facture_valider)
        //document.getElementById("demo").innerHTML = this.responseText;
        //boutonRow(bouton_row)
    }
    xhttp.open("GET", "/static/html/tableauBody.html", true);
    xhttp.send();
}

// loadPageFactureClientNonAdherent
function loadPageFactureClientInconnu(factures, etat_facture_valider) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        //TABLEAU 
        const tbody = document.getElementById('TableauValeur');
        tbody.innerHTML = this.responseText;
        tableauClientAdherentInconnu(factures, etat_facture_valider)
        //document.getElementById("demo").innerHTML = this.responseText;
        //boutonRow(bouton_row)
    }
    xhttp.open("GET", "/static/html/tableauBody.html", true);
    xhttp.send();
}

// fucntion loader
function showLoader() {
    document.getElementById('loader').setAttribute('class', 'd-flex justify-content-center align-items-center chargement');
}

function hideLoader() {
        document.getElementById('loader').setAttribute('class', 'hideloader');
}


// Placeholder actions
async function ouverturePageInconnu() {
    
    console.log('OUVERTURE PAGE DONNES INCONNUS')
    // Étape 1 : appel backend pour mise à jour
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        document.querySelector('#bloc_principal').style.display = 'none';
        document.getElementById("data_inconnu").style.display = 'block';
        document.getElementById("data_inconnu").innerHTML = this.responseText;
    
        // Maintenant seulement on peut récupérer l'élément
        const filtreSelect = document.getElementById("filtreSelect");
        const btnExport = document.getElementById("btnExport")
        if (filtreSelect) {
            filtreSelect.addEventListener("change", function () {
                let value = this.value;

                document.getElementById("tableAll").style.display = (value === "all") ? "block" : "none";
                document.getElementById("tableClients").style.display = (value === "clients") ? "block" : "none";
                document.getElementById("tableArticles").style.display = (value === "articles") ? "block" : "none";
            });
        } else {
            console.warn("⚠️ #filtreSelect introuvable dans la réponse HTML !");
        }
    
        // import excel
        btnExport.addEventListener("click", async function () {
        // Récupère la valeur du select
        const filtre = filtreSelect.value;

        if (filtre) {
                const response = await fetch(`/export_inconnus/${filtre}`);
                if (!response.ok) throw new Error("Erreur lors de l'export Excel");

                // Fichier blob
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);

                // Téléchargement auto
                const a = document.createElement("a");
                a.href = url;
                a.download = `data_${filtre}.xlsx`;
                document.body.appendChild(a);
                a.click();

                // Nettoyage
                a.remove();
                window.URL.revokeObjectURL(url);
        } else{
                console.error("❌ Erreur export ");
                alert("Impossible d’exporter le fichier Excel.");
            }
        });
    
    
    }

    // Appel pour mise à jour facture
    xhttp.open("GET", `/les_inconnus`, true);
    xhttp.send();

}