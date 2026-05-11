import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QGroupBox,
    QStatusBar, QFileDialog
)
from PySide6.QtCore import Qt

from PySide6 import QtWidgets, QtCore

from trieur_de_fichiers_api import existing_folders, create_folders, organise_files, my_dico

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trieur de Fichiers")
        self.setup_ui()
        self.setup_connections()

    
    def setup_ui(self):
        
        # Créer le widget central et le layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        content_layout = QHBoxLayout()

        # Créer un champ de saisie pour le nom du dossier et un bouton pour choisir le dossier source
        source_folder_layout = QHBoxLayout()
        self.source_folder = QLineEdit() 
        self.source_folder.setPlaceholderText("Chemin du dossier source...")
        self.browse_button = QPushButton("Parcourir")
        source_folder_layout.addWidget(self.source_folder)
        source_folder_layout.addWidget(self.browse_button)

        # Créer une liste pour afficher les dossiers existants dans le dossier source et un champ de saisie pour créer un nouveau dossier
        folder_group = QGroupBox("Dossiers existants")
        folder_layout = QVBoxLayout(folder_group)

        self.folder_list = QListWidget()
        folder_layout.addWidget(self.folder_list)

        self.new_folder_input = QLineEdit()
        self.new_folder_input.setPlaceholderText("Nom du nouveau dossier")
        folder_layout.addWidget(self.new_folder_input)

        self.create_button = QPushButton("Créer dossier")
        folder_layout.addWidget(self.create_button)

        # Créer une section pour gérer les types de fichiers associés à chaque dossier
        type_group = QGroupBox("Types de fichiers par dossier")
        type_layout = QVBoxLayout(type_group)

        self.selected_folder_label = QLabel("Sélectionnez un dossier")
        type_layout.addWidget(self.selected_folder_label)

        self.type_list = QListWidget()
        type_layout.addWidget(self.type_list)

        add_type_layout = QHBoxLayout()
        self.new_type_input = QLineEdit()
        self.new_type_input.setPlaceholderText("Exemple : jpg")
        add_type_layout.addWidget(self.new_type_input)
        self.add_type_button = QPushButton("Ajouter type")
        add_type_layout.addWidget(self.add_type_button)
        type_layout.addLayout(add_type_layout)


        # Layout pour les actions d'organisation et de rafraîchissement
        action_layout = QHBoxLayout()
        self.organize_button = QPushButton("Organiser les fichiers")
        action_layout.addWidget(self.organize_button)

        self.refresh_button = QPushButton("Rafraîchir")
        action_layout.addWidget(self.refresh_button)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


        # Ajouter tous les éléments au layout (L'ordre d'ajout correspond à l'ordre d'affichage)
        main_layout.addLayout(source_folder_layout)
        main_layout.addLayout(content_layout)
        content_layout.addWidget(folder_group, 1)
        content_layout.addWidget(type_group, 1)
        main_layout.addLayout(action_layout)


    def setup_connections(self):
        self.browse_button.clicked.connect(self._browse_folder) # A créer : _browse_folder()
        # self.browse_button.clicked.connect(my_dico.clear()) # A créer : _on_folder_selected()
        self.create_button.clicked.connect(self._create_folder) # A créer : _create_folder()
        self.add_type_button.clicked.connect(self._add_file_type) # A créer : _add_file_type()
        self.folder_list.currentItemChanged.connect(self._on_folder_selected)
        self.organize_button.clicked.connect(self._organize_files) # A créer : _organize_files()
        self.refresh_button.clicked.connect(self._load_existing_folders) # A créer : _load_existing_folders()


    def _browse_folder(self):
        # Logique pour ouvrir un dialogue de sélection de dossier et mettre à jour le champ de saisie du dossier source
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            self.source_folder.setText(folder)
            self._load_existing_folders()
            my_dico.clear()
            return True
        return False
            

    def _load_existing_folders(self):
        # Logique pour charger les dossiers existants dans le dossier source et les afficher dans la liste
        directory_name = self.source_folder.text()
        if directory_name:
            all_existing_folders = existing_folders(directory_name)
            self.folder_list.clear()
            self.folder_list.addItems(all_existing_folders)
     

    def _create_folder(self):
        # Logique pour créer un nouveau dossier
        directory_name = self.source_folder.text() # Recuperer la chaine de caractères du champ de saisie du dossier source
        if not directory_name:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier source avant de créer un nouveau dossier.")
            return False
        
        create_new_folder = create_folders(directory_name, self.new_folder_input.text())
        if create_new_folder is not True:
            QMessageBox.warning(self, "Erreur", create_new_folder)

        self.new_folder_input.clear()
        self._load_existing_folders() # Rafraîchir la liste des dossiers existants après
        return True


    def _get_selected_folder_directory(self):
        return self.folder_list.currentItem().text() if self.folder_list.currentItem() else None


    def _on_folder_selected(self):
        directory_name = self.source_folder.text() # Recuperer la chaine de caractères du champ de saisie du dossier source
        if directory_name:
            self.type_list.clear()
            self.selected_folder_label.setText("Selctionnez un dossier")
            selected_folder = self._get_selected_folder_directory()
            if selected_folder is not None:
                self.selected_folder_label.setText(f"Dossier sélectionné : {selected_folder}")
                
                if selected_folder not in my_dico:
                    my_dico[selected_folder] = []
                    return 
                self.type_list.addItems(my_dico[selected_folder])
                

    def _add_file_type(self):
        # Logique pour ajouter un type de fichier à un dossier sélectionné
        folder_name = self._get_selected_folder_directory()
        if self.folder_list.currentItem() is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier avant d'ajouter un type de fichier.")
            return False
        if self.new_type_input.text() == "" or self.new_type_input.text() in my_dico[folder_name]:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un type de fichier valide et non déjà ajouté.")
            return False

        my_dico[folder_name].append(self.new_type_input.text())
        self.type_list.clear()
        self.type_list.addItems(my_dico[folder_name])
        self.new_type_input.clear()

        return True


    def _organize_files(self):
        # Logique pour organiser les fichiers dans le dossier source en fonction des types associés à chaque dossier
        texte = """
Imposisible d'organiser les fichiers. Veuillez vous assurer que :

- Un dossier source est sélectionné
- Au moins un dossier de destination est créé ou existe déjà dans le dossier source
- Au moins un type de fichier est associé à au moins un dossier de destination
                """
        if not (self._on_folder_selected() and any(my_dico.values())):
            QMessageBox.warning(self, "Erreur", texte)
            return False
        number_of_files_organised = organise_files(Path(self.source_folder.text()), my_dico)
        my_dico.clear()
        self.type_list.clear()
        QMessageBox.information(self, "Succès", f"Les {number_of_files_organised} fichiers ont été organisés avec succès.")

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())