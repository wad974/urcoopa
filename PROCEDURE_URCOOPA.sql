CREATE DEFINER=`root`@`%` PROCEDURE `exportodoo`.`URCOOPA_PREPA_FACTURES`()
BEGIN
	
#Mise à jour ligne 900, ajoute l'article de service URCOOPA correspondant
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_product p
  on fu. Numero_Ligne_Facture =900
  and SUBSTRING_INDEX(p.name,'-',-1)= fu.Libelle_Produit
  and p.`type` ='service'
  set fu.ID_Produit_ODOO=p.id, fu.code_produit_ODOO=p.default_code, fu.ID_Produit_tmpl_ODOO = p.product_tmpl_id;

#Maj ID_CLIENT pour les magasin Sicalait
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.sic_depot d
    on fu.code_client = d.code_urcoopa
    and Type_Client='MAG. SICALAIT'
    set ID_Client_ODOO= d.company_id, Code_Client_ODOO=concat(d.code, ', ', d.lib);

#Maj ID_CLIENT pour les magasin SDPMA
#attention code a revoir    
update exportodoo.sic_urcoopa_facture fu
    set fu.ID_Client_ODOO= 56, Code_Client_ODOO='Sicalait aliment !'
    where fu.Type_Client='MAG. SDPMA';

#init ID_CLIENT pour les ADHERENT
update exportodoo.sic_urcoopa_facture fu
   set ID_Client_ODOO= 0, Code_Client_ODOO=''
   where fu.Type_Client='ADHERENT';
  
#maj des vrai ADHERENT
update exportodoo.sic_urcoopa_facture fu
  join exportodoo_prod.res_partner p
    on fu.nom_client = p.name
    and fu.Type_Client='ADHERENT'
  join exportodoo_prod.res_partner_category cat
    on p.category_id  = cat.id
    and cat.name='ADHERENT'
    set ID_Client_ODOO= p.id, Code_Client_ODOO=concat('CLIENT : ', p.`ref`);

#Maj des faux ADHERENT
update exportodoo.sic_urcoopa_facture fu
  join exportodoo_prod.res_partner p
    on fu.nom_client = p.name
    and fu.Type_Client='ADHERENT'
  join exportodoo_prod.res_partner_category cat
    on p.category_id  = cat.id
    and cat.name<>'ADHERENT'
    set ID_Client_ODOO= p.id, Code_Client_ODOO=concat('NON ADHERENT : ', p.`ref`);

#Maj des clients INCONNU    
update exportodoo.sic_urcoopa_facture fu
   set Code_Client_ODOO='INCONNU !'
   where fu.Type_Client='ADHERENT'
     and ID_Client_ODOO= 0;
    
#Maj ID_Produit_tmpl_ODOO depuis le catalogue
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_supplierinfo c
  on fu.Code_Produit = c.product_code
  and c.partner_id =  5081
  set fu.ID_Produit_tmpl_ODOO=c.product_tmpl_id
  where fu.ID_Produit_tmpl_ODOO is null;

#Maj ID_Produit_ODOO grace à ID_Produit_tmpl_ODOO
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_product p
  on fu.ID_Produit_tmpl_ODOO = p.product_tmpl_id
  set fu.ID_Produit_ODOO=p.id, fu.code_produit_ODOO=p.default_code
  where fu.ID_Produit_ODOO is null;
  
#Recup poids au Kilo dans base_unit_count
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_product p
  on fu.ID_Produit_ODOO = p.id
  and p.base_unit_name='Kilo'
  set fu.poid_unit_odoo= p.base_unit_count;
  
#Recup les quntité pour les articles à 'Unité(s)'
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_product p
  on fu.ID_Produit_ODOO = p.id
  and p.base_unit_name='Unité(s)'
  and p.base_unit_count<>0
  set fu.poid_unit_odoo= p.base_unit_count;
  
#maj poid_unit_odoo à 1 si =0
update exportodoo.sic_urcoopa_facture fu
  join exportodoo.product_product p
  on fu.ID_Produit_ODOO = p.id
  and p.base_unit_name='Unité(s)'
  and p.base_unit_count=0
  set fu.poid_unit_odoo= 1;

#Conversion poids vers quantité si géré à l'Unité
update exportodoo.sic_urcoopa_facture
   set Qte_Fact_Conv=round(Quantite_Facturee/poid_unit_odoo,4)
   where Unite_Facturee='UN';
  
#Conversion poids vers quantité si géré à la TONNE
update exportodoo.sic_urcoopa_facture
   set Qte_Fact_Conv=round((Quantite_Facturee*1000)/poid_unit_odoo,4)
   where Unite_Facturee='TO';
  	
SELECT 'OK' as result;

END