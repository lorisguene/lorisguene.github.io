setwd("C:/Users/lguene01/OneDrive - Université de Poitiers/SAE/SAE régression")
setwd("C:/Users/loris/OneDrive - Université de Poitiers/SAE/SAE régression")
install.packages("dplyr")
library(dplyr)
rm(list = ls())

data3 <- read.csv2("test.csv")
df <- read.csv2("./ouai/fichier_resultat_filtré.csv")
test <- colnames(data3)
test
df <- df[, c("Commune","Date.mutation","Nature.mutation","Code.postal","Code.departement","Type.local","Surface.reelle.bati","Nombre.pieces.principales","Surface.terrain","Valeur.fonciere")]
df$Surface.terrain[is.na(df$Surface.terrain)] <- 0
df$Surface.terrain[df$Surface.terrain == ""] <- 0


df_2023 <- data3[grepl("2023$", data3$Date.mutation), ]
#df_2024 <- data3[grepl("2024$", data3$Date.mutation), ]

cols_communes <- intersect(colnames(df), colnames(data3))
data3 <- data3[, cols_communes]

#df[] <- lapply(df, function(x) gsub('"', '', x))  # Enlever les guillemets doubles
#df[] <- lapply(df, function(x) gsub("'", '', x))

cols_communes <- c("Valeur.fonciere","Code.departement","Surface.reelle.bati","Nombre.pieces.principales","Surface.terrain","Code.postal")


clean_numeric <- function(x) {
  x <- gsub('"', '', x)    # Enlever les guillemets
  x <- gsub(",", ".", x)   # Remplacer la virgule par un point
  as.numeric(x)            # Conversion en numérique
}

# Appliquer cette fonction aux colonnes concernées dans df et data3
df[cols_communes] <- lapply(df[cols_communes], clean_numeric)
data3[cols_communes] <- lapply(data3[cols_communes], clean_numeric)

valeurs_df <- df$Valeur.fonciere
valeurs_data3 <- data3$Valeur.fonciere

# Supprimer la colonne Valeur.fonciere des deux dataframes
#df <- df[, !(names(df) %in% "Valeur.fonciere")]
#data3 <- data3[, !(names(data3) %in% "Valeur.fonciere")]

df_common <- merge(df, data3, by = c("Date.mutation","Nature.mutation","Commune", "Code.postal", "Code.departement", "Type.local", "Surface.reelle.bati", "Nombre.pieces.principales", "Surface.terrain"))
#df_common2 <- merge( df_2023,df_common, by = c("Date.mutation","Nature.mutation","Commune", "Code.postal", "Code.departement", "Type.local", "Surface.reelle.bati", "Nombre.pieces.principales", "Surface.terrain"))

df_common <- df_common[!duplicated(df_common), ]
#df_common2<- df_common2[, 1:9]








# Lecture des fichiers
data_2024 <- read.csv2("test.csv")
df_2024_raw <- read.csv2("./ouai/fichier_resultat_filtré2.csv")

# Garde les colonnes nécessaires
df_2024 <- df_2024_raw[, c("Commune","Date.mutation","Nature.mutation","Code.postal",
                           "Code.departement","Type.local","Surface.reelle.bati",
                           "Nombre.pieces.principales","Surface.terrain","Valeur.fonciere")]

# Remplacement des vides/NA dans Surface.terrain
df_2024$Surface.terrain[is.na(df_2024$Surface.terrain)] <- 0
df_2024$Surface.terrain[df_2024$Surface.terrain == ""] <- 0

# Filtrer les mutations de 2024
data_2024 <- data_2024[grepl("2024$", data_2024$Date.mutation), ]

# Filtrer sur les ventes et les biens "Maison" ou "Appartement"
data_2024 <- data_2024[
  data_2024$Nature.mutation == "Vente" &
    data_2024$Type.local %in% c("Maison", "Appartement"),
]

# Colonnes communes
cols_communes <- intersect(colnames(df_2024), colnames(data_2024))
data_2024 <- data_2024[, cols_communes]

# Colonnes numériques à nettoyer
cols_numeric <- c("Valeur.fonciere","Code.departement","Surface.reelle.bati",
                  "Nombre.pieces.principales","Surface.terrain","Code.postal")

clean_numeric <- function(x) {
  x <- gsub('"', '', x)
  x <- gsub(",", ".", x)
  as.numeric(x)
}

# Nettoyage
df_2024[cols_numeric] <- lapply(df_2024[cols_numeric], clean_numeric)
data_2024[cols_numeric] <- lapply(data_2024[cols_numeric], clean_numeric)

# Sauvegarde temporaire de Valeur.fonciere
valeurs_df_2024 <- df_2024$Valeur.fonciere
valeurs_data_2024 <- data_2024$Valeur.fonciere

# Suppression temporaire
#df_2024 <- df_2024[, !(names(df_2024) %in% "Valeur.fonciere")]
#data_2024 <- data_2024[, !(names(data_2024) %in% "Valeur.fonciere")]

# Réinsertion
df_2024$Valeur.fonciere <- as.numeric(valeurs_df_2024)
data_2024$Valeur.fonciere <- as.numeric(valeurs_data_2024)

# Fusion des 2 sources (colonnes identiques)
df_2024_common <- merge(df_2024, data_2024, by = c("Date.mutation","Nature.mutation","Commune", 
                                                   "Code.postal", "Code.departement", "Type.local", 
                                                   "Surface.reelle.bati", "Nombre.pieces.principales", 
                                                   "Surface.terrain"))

# Résultat final sans doublons
df_2024_clean <- df_2024_common[!duplicated(df_2024_common), ]
#df_2024_clean <- df_2024_clean[, 1:9]  # Garder colonnes principales



df_total <- rbind(df_common, df_2024_clean)
colnames(df_total)[colnames(df_total) == "Valeur.fonciere.y"] <- "Valeur.fonciere"

test <- merge(df_total, data3, by = c("Date.mutation","Nature.mutation","Commune", 
                                 "Code.postal", "Code.departement", "Type.local", 
                                 "Surface.reelle.bati", "Nombre.pieces.principales", 
                                 "Surface.terrain","Valeur.fonciere"))
sum(duplicated(test[c("Valeur.fonciere","Date.mutation")]))
# Supprimer les doublons sur plusieurs colonnes
test <- test[!duplicated(test[c("Valeur.fonciere", "Date.mutation")]), ]
test$res <- test$Valeur.fonciere.x - test$Valeur.fonciere
test$Valeur.fonciere.x[is.na(test$Valeur.fonciere.x)] <- 0
sum(is.na(test$res))
min(test$res)
scr <- sum(test$res^2)
scr
sct <- sum(( test$Valeur.fonciere.x- mean(test$Valeur.fonciere.x))^2)
1 - scr/sct

test <- subset(test, select = -res)
write.csv2(test, "mon_fichier.csv", row.names = FALSE)
