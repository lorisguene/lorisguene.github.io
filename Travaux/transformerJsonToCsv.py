# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 09:46:26 2024

@author: loris
"""
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime


def nettoyerTexte(texte):
    if isinstance(texte, str):  # Vérifie si le champ est une chaîne de caractères
    
        if len(texte)> 30000:
            texte = texte[:30000]
            
        return texte.replace("\n", " ")  # Remplace les \n par des espaces
    
    return texte


colonne  = ["id","url","title","lead_text","description","tags","date_start","date_end","address_name","address_street","address_zipcode","address_city","lat_lon","pmr","blind","deaf","transport","contact_phone","contact_mail","contact_url","access_type","price_detail","cover_url"]
entete = ["ID","URL","Titre","Chapeau","Description","Mots clés","Date de début","Heure de début","Date de fin","Heure de Fin","Nom du lieu","Adresse du lieu","Code Postal","Ville","Coordonnées géographiques","Accès PMR","Accès mal voyant","Accès mal entendant","Transport","Téléphone de contact","Email de contact","Url de contact","Type d’accès","Détail du prix","URL de l’image de couverture"]
try:
    
    fichier = open("que-faire-a-paris-.json","r", encoding  = "utf-8")
    
    tousLesDico = json.loads(fichier.read())
    try:
            
        fichierCSV = open("CSV.csv","w",encoding = "utf-8-sig", newline = '')
        ecritCSV = csv.writer(fichierCSV,delimiter  = ";")
        ecritCSV.writerow(entete)
        
        for j in range(len(tousLesDico)):
            ligne = []
            evenement = tousLesDico[j]
            
            if not isinstance(evenement, dict):
                print(f"L'élément à l'indice {j} n'est pas un dictionnaire.")
                continue
            
            for i in range(len(colonne)):
                dedans = False
                
                for cle, valeur in evenement.items():
                    
                    if cle == colonne[i]:
                        dedans = True
                        
                        if (cle == 'date_start' or cle == 'date_end'):
                            
                            if valeur == None or valeur == "":
                                ligne.append("")
                                ligne.append("")
                                
                            else:
                                
                                try:
                                    date = datetime.fromisoformat(valeur.split('T')[0])
                                    dateFr = date.strftime("%d/%m/%Y")
                                    heure = str(valeur[11:19])
                                    ligne.append(dateFr)
                                    ligne.append(heure)
                                    
                                except ValueError:
                                    ligne.append("")
                                    ligne.append("")
                                    
                        else:
                            
                            if valeur == None:
                                ligne.append("")
                                
                            else:
                                
                                if isinstance(valeur, str):
                                    soup = BeautifulSoup(valeur, "html.parser")
                                    valeur = soup.getText()
                                    
                                    if valeur and (valeur[0] == '0' or valeur[0] == '+'):
                                        valeur = f"'{valeur}"
                                        
                                ligne.append(nettoyerTexte(valeur))
                                
                if dedans == False:
                    
                    if i == 6  or i == 8:
                        ligne.append("")
                        
                    ligne.append("")
                    
            ecritCSV.writerow(ligne)
        
        fichierCSV.close()
        
    except PermissionError:
        print("Vous n'avez pas la permission")
        
    except OSError:
        print("Erreur du système de fichiers")
        
    fichier.close()
    
except FileNotFoundError:
    print('Fichier "que-faire-a-paris-.json" introuvable')
    
except json.JSONDecodeError:
    print("Erreur de décodage JSON, le fichier n'est pas correctement formaté.")
