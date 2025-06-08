
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import mysql.connector
import os
from datetime import datetime

# Configuration de connexion
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "selmarin_tda"
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface Selmarin")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")

        self.dark_mode = False
        self.init_styles()
        self.conn = self.connect_to_db()
        self.cursor = self.conn.cursor()

        self.create_widgets()

    def init_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.set_theme("light")

    def set_theme(self, mode):
        if mode == "dark":
            self.configure(bg="#2e2e2e")
            self.style.configure(".", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
            self.style.configure("TEntry", fieldbackground="#3c3c3c", foreground="white")
            self.style.map("TButton", background=[("active", "#444")])
        else:
            self.configure(bg="#f0f0f0")
            self.style.configure(".", background="#f0f0f0", foreground="black", fieldbackground="white")
            self.style.configure("TEntry", fieldbackground="white", foreground="black")
            self.style.map("TButton", background=[("active", "#ddd")])

        self.style.configure("TLabel", font=("Segoe UI", 11))
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("TCombobox", font=("Segoe UI", 11))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

    
    def afficher_erreur(self, err):
        err_msg = str(err)
        if "foreign key constraint fails" in err_msg:
            messagebox.showerror("Erreur de contrainte", "Échec : la clé étrangère fait référence à une valeur inexistante.")
        elif "Duplicate entry" in err_msg:
            messagebox.showerror("Doublon", "Échec : la clé primaire existe déjà.")
        elif "Incorrect datetime value" in err_msg:
            messagebox.showerror("Erreur de date", "Le format de la date est invalide. Attendu : AAAA-MM-JJ.")
        elif "Data truncated" in err_msg or "Incorrect" in err_msg:
            messagebox.showerror("Erreur de données", "Échec : une donnée est mal formatée ou trop longue.")
        else:
            messagebox.showerror("Erreur SQL", err_msg)

    def toggle_theme(self):
            self.dark_mode = not self.dark_mode
            self.set_theme("dark" if self.dark_mode else "light")

    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(**db_config)
            print("Connexion réussie.")
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur de connexion", str(err))
            self.destroy()

    def create_widgets(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        theme_menu = tk.Menu(menu, tearoff=0)
        theme_menu.add_command(label="Basculer thème clair/sombre", command=self.toggle_theme)
        menu.add_cascade(label="Apparence", menu=theme_menu)

        tabControl = ttk.Notebook(self)

        self.tab_tables = ttk.Frame(tabControl)
        self.tab_import = ttk.Frame(tabControl)
        self.tab_sql = ttk.Frame(tabControl)
        self.tab_guide = ttk.Frame(tabControl)
        tabControl.add(self.tab_tables, text="📊 Visualiser Tables")
        tabControl.add(self.tab_import, text="📥 Importer CSV")
        tabControl.add(self.tab_sql, text="💬 Requêtes SQL")
        tabControl.add(self.tab_guide, text="📘 Guide d'utilisation")

        tabControl.pack(expand=1, fill="both")

        self.build_tables_tab()
        self.build_import_tab()
        self.build_sql_tab()
        self.build_guide_tab()


    def build_tables_tab(self):
        self.tables_listbox = tk.Listbox(self.tab_tables, font=("Segoe UI", 10), width=30)
        self.tables_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.tables_listbox.bind("<<ListboxSelect>>", self.load_table_data)

        self.table_view = ttk.Treeview(self.tab_tables)
        self.table_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_insert = ttk.Button(self.tab_tables, text="➕ Ajouter une ligne", command=self.show_insert_form)
        btn_insert.pack(pady=5)
        btn_update = ttk.Button(self.tab_tables, text="✏️ Modifier la ligne sélectionnée", command=self.show_update_form)
        btn_update.pack(pady=5)
        btn_delete = ttk.Button(self.tab_tables, text="🗑️ Supprimer la ligne sélectionnée", command=self.delete_selected_row)
        btn_delete.pack(pady=5)

        self.refresh_tables_list()

    def refresh_tables_list(self):
        self.tables_listbox.delete(0, tk.END)
        self.cursor.execute("SHOW TABLES")
        for (table_name,) in self.cursor.fetchall():
            self.tables_listbox.insert(tk.END, table_name)

    
    def show_insert_form(self):
        selection = self.tables_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionne une table.")
            return

        table = self.tables_listbox.get(selection[0])

        # Récupérer les colonnes
        self.cursor.execute(f"DESCRIBE {table}")
        columns = [col[0] for col in self.cursor.fetchall()]

        form = tk.Toplevel(self)
        form.title(f"Ajouter une ligne à {table}")
        form.geometry("400x400")

        entries = {}

        for idx, col in enumerate(columns):
            ttk.Label(form, text=col).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(form, width=30)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[col] = entry

        def insert_row():
            values = [entries[col].get() for col in columns]
            placeholders = ", ".join(["%s"] * len(values))
            colnames = ", ".join(columns)
            try:
                self.cursor.execute(f"INSERT INTO {table} ({colnames}) VALUES ({placeholders})", values)
                self.conn.commit()
                messagebox.showinfo("Succès", "Ligne insérée avec succès.")
                form.destroy()
                self.load_table_data(None)
            except Exception as e:
                self.afficher_erreur(e)

        ttk.Button(form, text="Valider", command=insert_row).grid(row=len(columns), column=0, columnspan=2, pady=15)


    def show_update_form(self):
        selection = self.tables_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionne une table.")
            return

        table = self.tables_listbox.get(selection[0])
        selected_item = self.table_view.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Sélectionne une ligne dans le tableau.")
            return

        values = self.table_view.item(selected_item)["values"]
        self.cursor.execute(f"DESCRIBE {table}")
        columns = [col[0] for col in self.cursor.fetchall()]
        primary_key = columns[0]

        form = tk.Toplevel(self)
        form.title(f"Modifier une ligne de {table}")
        form.geometry("400x400")

        entries = {}

        for idx, (col, val) in enumerate(zip(columns, values)):
            ttk.Label(form, text=col).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(form, width=30)
            entry.insert(0, val)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[col] = entry

        def update_row():
            updated_values = [entries[col].get() for col in columns]
            set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])
            try:
                self.cursor.execute(
                    f"UPDATE {table} SET {set_clause} WHERE {primary_key} = %s",
                    updated_values[1:] + [updated_values[0]]
                )
                self.conn.commit()
                messagebox.showinfo("Succès", "Ligne mise à jour.")
                form.destroy()
                self.load_table_data(None)
            except Exception as e:
                self.afficher_erreur(e)

        ttk.Button(form, text="Mettre à jour", command=update_row).grid(row=len(columns), column=0, columnspan=2, pady=15)

    def delete_selected_row(self):
        selection = self.tables_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionne une table.")
            return

        table = self.tables_listbox.get(selection[0])
        selected_item = self.table_view.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Sélectionne une ligne à supprimer.")
            return

        values = self.table_view.item(selected_item)["values"]
        self.cursor.execute(f"DESCRIBE {table}")
        columns = [col[0] for col in self.cursor.fetchall()]
        primary_key = columns[0]

        confirm = messagebox.askyesno("Confirmation", f"Supprimer la ligne avec {primary_key} = {values[0]} ?")
        if confirm:
            try:
                self.cursor.execute(f"DELETE FROM {table} WHERE {primary_key} = %s", (values[0],))
                self.conn.commit()
                messagebox.showinfo("Succès", "Ligne supprimée.")
                self.load_table_data(None)
            except Exception as e:
                self.afficher_erreur(e)
    
    def load_table_data(self, event):
            selection = self.tables_listbox.curselection()
            if not selection:
                return
            table = self.tables_listbox.get(selection[0])
            self.cursor.execute(f"SELECT * FROM {table}")
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
    
            self.table_view.delete(*self.table_view.get_children())
            self.table_view["columns"] = columns
            self.table_view["show"] = "headings"
    
            for col in columns:
                self.table_view.heading(col, text=col)
    
            for row in rows:
                self.table_view.insert("", "end", values=row)

    def build_import_tab(self):
        ttk.Label(self.tab_import, text="Choisir un fichier CSV à importer :").pack(pady=10)

        self.csv_choice = tk.StringVar()
        csv_options = ["client.csv", "saunier.csv", "entree.csv", "sortie.csv"]
        self.csv_dropdown = ttk.Combobox(self.tab_import, textvariable=self.csv_choice, values=csv_options, state="readonly")
        self.csv_dropdown.pack(pady=5)

        btn = ttk.Button(self.tab_import, text="Importer", command=self.import_specific_csv)
        btn.pack(pady=10)
    def build_guide_tab(self):
            texte = """\
        Bienvenue dans l'application Selmarin !
        
        🧭 Onglet \"Visualiser Tables\" :
        - Sélectionne une table à gauche
        - Clique sur une ligne pour la modifier ou la supprimer
        - Utilise le bouton \"Ajouter\" pour insérer une nouvelle ligne
        
        📥 Onglet \"Importer CSV\" :
        - Choisis un fichier CSV parmi les 4 proposés
        - Les données seront insérées dans les tables correspondantes
        - Les dates sont automatiquement converties
        
        💬 Onglet \"Requêtes SQL\" :
        - Choisis une requête prédéfinie ou écris la tienne
        - Clique sur \"Exécuter\" pour voir les résultats
        
        🌓 Menu Apparence :
        - Change entre thème clair et thème sombre
        
        🔒 Attention aux clés primaires et étrangères :
        - Assure-toi que les valeurs référencées existent déjà dans les autres tables
        """
        
            text_widget = tk.Text(self.tab_guide, wrap="word", font=("Segoe UI", 11))
            text_widget.insert(tk.END, texte)
            text_widget.config(state="disabled")
            text_widget.pack(expand=True, fill="both", padx=10, pady=10)

    def import_specific_csv(self):
        filename = self.csv_choice.get()
        if not filename:
            messagebox.showwarning("Attention", "Choisis un fichier CSV.")
            return

        file_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(file_path):
            messagebox.showerror("Erreur", f"Le fichier {filename} est introuvable.")
            return

        try:
            df = pd.read_csv(file_path, sep=";", encoding="ISO-8859-1")
            df.columns = df.columns.str.strip()

            if filename == "entree.csv":
                df["dateEnt"] = pd.to_datetime(df["dateEnt"], dayfirst=True)
                df["dateEnt"] = df["dateEnt"].dt.strftime("%Y-%m-%d %H:%M:%S")
                for _, row in df.iterrows():
                    self.cursor.execute(
                        "INSERT INTO Entree (numEnt, dateEnt, qteEnt, numPdt, numSau) VALUES (%s, %s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE qteEnt=VALUES(qteEnt), numPdt=VALUES(numPdt), numSau=VALUES(numSau)",
                        (row["NumEnt"], row["dateEnt"], row["qteEnt"], row["numPdt"], row["numSau"])
                    )

            elif filename == "sortie.csv":
                df["dateSort"] = pd.to_datetime(df["dateSort"], dayfirst=True)
                df["dateSort"] = df["dateSort"].dt.strftime("%Y-%m-%d %H:%M:%S")
                for _, row in df.iterrows():
                    self.cursor.execute(
                        "INSERT INTO Sortie (numSort, dateSort, numCli) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE dateSort=VALUES(dateSort), numCli=VALUES(numCli)",
                        (row["NumSort"], row["dateSort"], row["numCli"])
                    )
                    self.cursor.execute(
                        "INSERT INTO Concerner (numPdt, numSort, qteSort) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE qteSort=VALUES(qteSort)",
                        (row["numPdt"], row["NumSort"], row["qteSort"])
                    )

            elif filename == "client.csv":
                for _, row in df.iterrows():
                    self.cursor.execute(
                        "INSERT INTO Client (numCli, nomCli, prenomCli, villeCli) VALUES (%s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE nomCli=VALUES(nomCli), prenomCli=VALUES(prenomCli), villeCli=VALUES(villeCli)",
                        (row["numCli"], row["nomCli"], row["prenomCli"], row["villeCli"])
                    )

            elif filename == "saunier.csv":
                for _, row in df.iterrows():
                    self.cursor.execute(
                        "INSERT INTO Saunier (numSau, nomSau, prenomSau, villeSau) VALUES (%s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE nomSau=VALUES(nomSau), prenomSau=VALUES(prenomSau), villeSau=VALUES(villeSau)",
                        (row["numSau"], row["nomSau"], row["prenomSau"], row["villeSau"])
                    )

            self.conn.commit()
            messagebox.showinfo("Succès", f"{filename} importé avec succès.")
        except Exception as e:
            self.afficher_erreur(e)

    def build_sql_tab(self):
        frame = ttk.Frame(self.tab_sql)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Requêtes prédéfinies :").pack(anchor="w")
        self.sql_queries = {
            "Tous les clients": "SELECT * FROM Client",
            "Toutes les sorties": "SELECT * FROM Sortie",
            "Quantité totale sortie par produit": "SELECT numPdt, SUM(qteSort) as total FROM Concerner GROUP BY numPdt",
            "Liste des produits avec leur stock": "SELECT * FROM Produit;",
            "Liste des clients par ville": "SELECT villeCli, COUNT(*) AS nb_clients FROM Client GROUP BY villeCli;",
            "Top 5 des produits les plus sortis": "SELECT numPdt, SUM(qteSort) AS totalSortie FROM Concerner GROUP BY numPdt ORDER BY totalSortie DESC LIMIT 5;",
            "Entrées par produit": "SELECT numPdt, SUM(qteEnt) AS totalEntree FROM Entree GROUP BY numPdt;",
            "Historique des sorties par client": "SELECT C.nomCli, S.dateSort, Co.qteSort FROM Client C JOIN Sortie S ON C.numCli = S.numCli JOIN Concerner Co ON S.numSort = Co.numSort;",
            "Produits sans entrée": "SELECT P.numPdt, P.libPdt FROM Produit P LEFT JOIN Entree E ON P.numPdt = E.numPdt WHERE E.numPdt IS NULL;",
            "Produits sans sortie": "SELECT P.numPdt, P.libPdt FROM Produit P LEFT JOIN Concerner C ON P.numPdt = C.numPdt WHERE C.numPdt IS NULL;",
            "Moyenne des quantités entrées par produit": "SELECT numPdt, AVG(qteEnt) AS moyenne FROM Entree GROUP BY numPdt;",
            "Total des sorties par ville de client": "SELECT villeCli, SUM(qteSort) AS totalSortie FROM Client C JOIN Sortie S ON C.numCli = S.numCli JOIN Concerner Co ON S.numSort = Co.numSort GROUP BY villeCli;",
            "Produits disponibles en stock > 1000": "SELECT * FROM Produit WHERE stockPdt > 1000;",
            "Ajouter un client test":"INSERT INTO Client (numCli, nomCli, prenomCli, villeCli) SELECT IFNULL(MAX(numCli), 0) + 1, 'TestNom', 'TestPrenom', 'VilleTest' FROM Client;",
            "Créer une vue comptable de toutes les tables":
                "CREATE VIEW comptable AS "
                "SELECT S.numSau, nomSau, prenomSau, villeSau, "
                "P.numPdt, libPdt, stockPdt, "
                "C.numCli, nomCli, prenomCli, villeCli, "
                "So.numSort, dateSort, "
                "E.numEnt, dateEnt, qteEnt, "
                "Co.qteSort, "
                "Pr.Annee, Prix_d_achat__Tonne_en___, Prix_de_vente__Tonne_en___ "
                "FROM Saunier S "
                "JOIN Entree E ON S.numSau = E.numSau "
                "JOIN Produit P ON E.numPdt = P.numPdt "
                "JOIN Concerner Co ON P.numPdt = Co.numPdt "
                "JOIN Sortie So ON Co.numSort = So.numSort "
                "JOIN Client C ON So.numCli = C.numCli "
                "JOIN Prix Pr ON P.numPdt = Pr.numPdt;",
            "Total des achats par année":
                "SELECT Pr.Annee, libPdt, SUM(qteEnt) AS totalQuantiteEntree "
                "FROM Entree E "
                "JOIN Produit Pdt ON E.numPdt = Pdt.numPdt "
                "JOIN Prix Pr ON Pdt.numPdt = Pr.numPdt "
                "GROUP BY Pr.Annee, Pdt.numPdt "
                "ORDER BY Pr.Annee, libPdt;",
            "Quantité totale sortie par produit et saunier (année 2024)":
                "SELECT nomSau, libPdt, SUM(Co.qteSort) AS totalQteSortie "
                "FROM Saunier S "
                "JOIN Entree E ON S.numSau = E.numSau "
                "JOIN Produit P ON E.numPdt = P.numPdt "
                "JOIN Concerner Co ON P.numPdt = Co.numPdt "
                "JOIN Sortie So ON Co.numSort = So.numSort "
                "WHERE YEAR(So.dateSort) = 2024 "
                "GROUP BY nomSau, libPdt;",
            "Sauniers et quantité de gros sel vendu pour chaque saunier":
                "SELECT nomSau, SUM(qteEnt) AS qteTotale FROM Saunier S "
                "JOIN Entree E ON S.numSau = E.numSau "
                "JOIN Produit P ON E.numPdt = P.numPdt "
                "WHERE libPdt = 'Gros sel' GROUP BY nomSau;"

        }
        self.query_choice = tk.StringVar()
        self.query_dropdown = ttk.Combobox(frame, textvariable=self.query_choice, values=list(self.sql_queries.keys()), state="readonly")
        self.query_dropdown.pack(fill="x", padx=5, pady=2)

        btn_use_query = ttk.Button(frame, text="Utiliser cette requête", command=self.load_predefined_query)
        btn_use_query.pack(pady=5)

        ttk.Label(frame, text="Requête SQL personnalisée :").pack(anchor="w")
        self.sql_input = tk.Text(self.tab_sql, height=6, font=("Consolas", 10))
        self.sql_input.pack(fill="both", expand=False, padx=10)

        btn_execute = ttk.Button(self.tab_sql, text="Exécuter la requête", command=self.execute_custom_query)
        btn_execute.pack(pady=10)

        self.sql_result = ttk.Treeview(self.tab_sql)
        self.sql_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_predefined_query(self):
        key = self.query_choice.get()
        if key and key in self.sql_queries:
            self.sql_input.delete("1.0", tk.END)
            self.sql_input.insert(tk.END, self.sql_queries[key])

    def execute_custom_query(self):
        query = self.sql_input.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Attention", "La requête est vide.")
            return
        try:
            self.cursor.execute(query)
            if query.lower().startswith("select"):
                rows = self.cursor.fetchall()
                columns = [desc[0] for desc in self.cursor.description]

                self.sql_result.delete(*self.sql_result.get_children())
                self.sql_result["columns"] = columns
                self.sql_result["show"] = "headings"

                for col in columns:
                    self.sql_result.heading(col, text=col)

                for row in rows:
                    self.sql_result.insert("", "end", values=row)
            else:
                self.conn.commit()
                messagebox.showinfo("Succès", "Requête exécutée avec succès.")
        except Exception as e:
            self.afficher_erreur(e)
            



if __name__ == "__main__":
    app = App()
    app.mainloop()
