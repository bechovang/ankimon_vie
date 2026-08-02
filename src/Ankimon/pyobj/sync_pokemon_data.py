import json
from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QPushButton, QDialog
from aqt import mw
from aqt.utils import showWarning, showInfo, tooltip
from ..resources import mypokemon_path, mainpokemon_path

class CheckPokemonData(QDialog):
    def __init__(self, settings_obj, logger):
        super().__init__()
        self.config = settings_obj
        self.logger = logger
        self.mypokemon_path = mypokemon_path
        self.mainpokemon_path = mainpokemon_path
        self.sync_pokemons()
        self.get_pokemon_data()
        self.setup_ui()
        self.display_data_comparison()

    def setup_ui(self):
        # Set the window title for the dialog
        self.setWindowTitle(mw.translator.translate("sync.window_title"))

        # Create a QLabel instance
        self.label = QLabel(mw.translator.translate("sync.dialog_message"), self)

        # Create two QPushButtons for syncing options
        self.sync_local_button = QPushButton(mw.translator.translate("sync.export_to_ankiweb"), self)
        self.sync_ankiweb_button = QPushButton(mw.translator.translate("sync.import_from_ankiweb"), self)
        self.sync_local_button.clicked.connect(self.sync_data_to_ankiweb)
        self.sync_ankiweb_button.clicked.connect(self.sync_data_to_local)

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Create two QTextEdit widgets for displaying data side by side
        self.local_text_area = QTextEdit(self)
        self.local_text_area.setReadOnly(True)  # Make it read-only
        #self.local_text_area.setWordWrapMode(QTextOption.NoWrap)  # Use QTextOption::NoWrap
        self.local_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap) # Correct usage in PyQt6
        self.web_text_area = QTextEdit(self)
        self.web_text_area.setReadOnly(True)  # Make it read-only
        #self.web_text_area.setWordWrapMode(QTextOption.NoWrap)  # Use QTextOption::NoWrap
        self.web_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap) # Correct usage in PyQt6
        # Add the QLabel and QPushButtons to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sync_local_button)
        self.layout.addWidget(self.sync_ankiweb_button)
        self.layout.addWidget(self.local_text_area)
        self.layout.addWidget(self.web_text_area)

        # Set the dialog's layout
        self.setLayout(self.layout)

    def get_pokemon_data(self):
        try:
            with open(self.mypokemon_path, 'r', encoding='utf-8') as file:
                self.pokemon_collection_sync_data = json.load(file)
            with open(self.mainpokemon_path, 'r', encoding='utf-8') as file:
                self.mainpokemon_sync_data = json.load(file)
        except Exception as e:
            self.logger.log("error", "Failed to load Pokémon data: " + str(e))
            self.pokemon_collection_sync_data = []
            self.mainpokemon_sync_data = []

    def sync_pokemons(self):
        try:
            self.mainpokemon_web_data = self.config.get('mainpokemon', [])
            self.pokemon_collection_web_data = self.config.get('pokemon_collection', [])
        except Exception as e:
            self.logger.log("error", "Failed to retrieve Pokémon data from AnkiWeb.")
            self.mainpokemon_web_data = []
            self.pokemon_collection_web_data = []
        self.get_pokemon_data()

        if self.mainpokemon_web_data != self.mainpokemon_sync_data or self.pokemon_collection_web_data != self.pokemon_collection_sync_data:
            self.show()

    def sync_data_to_local(self):
        try:
            with open(self.mypokemon_path, 'w', encoding='utf-8') as file:
                json.dump(self.pokemon_collection_web_data, file, ensure_ascii=False, indent=4)
            with open(self.mainpokemon_path, 'w', encoding='utf-8') as file:
                json.dump(self.mainpokemon_web_data, file, ensure_ascii=False, indent=4)
            showInfo(mw.translator.translate("sync.synced_to_local"))
        except Exception as e:
            showWarning(mw.translator.translate("sync.failed_sync_local", error=str(e)))
        self.close()

    def sync_data_to_ankiweb(self):
        try:
            self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
            self.config.set("mainpokemon", self.mainpokemon_sync_data)
            showInfo(mw.translator.translate("sync.synced_to_ankiweb"))
        except Exception as e:
            showWarning(mw.translator.translate("sync.failed_sync_ankiweb", error=str(e)))
        self.close()

    def sync_on_anki_close(self):
        tooltip(mw.translator.translate("sync.syncing_tooltip"))
        self.get_pokemon_data()
        self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
        self.config.set("mainpokemon", self.mainpokemon_sync_data)

    def modify_json_configuration_on_save(self, text: str) -> str:
        try:
            config = json.loads(text)
            self.get_pokemon_data()
            self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
            self.config.set("mainpokemon", self.mainpokemon_sync_data)
            tooltip(mw.translator.translate("sync.saved_config_restart"))
            modified_text = json.dumps(config, indent=4)
            return modified_text
        except json.JSONDecodeError:
            showWarning(mw.translator.translate("sync.invalid_json"))
            return text

    def display_pokemon_info(self, pokemon_data):
        # Display Pokémon information
        pokemon_info = mw.translator.translate(
            "sync.pokemon_info",
            name=pokemon_data['name'],
            gender=pokemon_data['gender'],
            level=pokemon_data['level'],
            id=pokemon_data['id'],
            ability=pokemon_data['ability'],
            type=', '.join(pokemon_data['type']),
            stats_hp=pokemon_data['stats']['hp'],
            stats_atk=pokemon_data['stats']['atk'],
            stats_def=pokemon_data['stats']['def'],
            stats_spa=pokemon_data['stats']['spa'],
            stats_spd=pokemon_data['stats']['spd'],
            stats_spe=pokemon_data['stats']['spe'],
            xp=pokemon_data['stats']['xp'],
            ev_hp=pokemon_data['ev']['hp'],
            ev_atk=pokemon_data['ev']['atk'],
            ev_def=pokemon_data['ev']['def'],
            ev_spa=pokemon_data['ev']['spa'],
            ev_spd=pokemon_data['ev']['spd'],
            ev_spe=pokemon_data['ev']['spe'],
            iv_hp=pokemon_data['iv']['hp'],
            iv_atk=pokemon_data['iv']['atk'],
            iv_def=pokemon_data['iv']['def'],
            iv_spa=pokemon_data['iv']['spa'],
            iv_spd=pokemon_data['iv']['spd'],
            iv_spe=pokemon_data['iv']['spe'],
            attacks=', '.join(pokemon_data['attacks']),
            base_experience=pokemon_data['base_experience'],
            current_hp=pokemon_data['current_hp'],
            growth_rate=pokemon_data['growth_rate'],
            evolves_to=', '.join(pokemon_data['evos']),
            individual_id=pokemon_data['individual_id'],
            everstone=pokemon_data['everstone'],
            shiny=pokemon_data['shiny'],
            friendship=pokemon_data['friendship'],
            pokemon_defeated=pokemon_data['pokemon_defeated'],
            captured_date=pokemon_data['captured_date'],
        )

        return pokemon_info

    def display_data_comparison(self):
        unknown = mw.translator.translate("sync.unknown")
        # Main Pokémon Data Comparison
        local_main_differences = []
        web_main_differences = []

        for local, ankiweb in zip(self.mainpokemon_sync_data, self.mainpokemon_web_data):
            pokemon_name = local.get('name', unknown)
            individual_id = local.get('individual_id', unknown)
            for key in local:
                local_value = local.get(key, unknown)
                web_value = ankiweb.get(key, unknown)
                if local_value != web_value:
                    local_main_differences.append(f"{pokemon_name} - {individual_id} - {key}: {local_value}")
                    web_main_differences.append(f"{pokemon_name} - {individual_id} - {key}: {web_value}")

        # Pokémon Collection Data Comparison
        local_pokemon_differences = []
        web_pokemon_differences = []

        for local, ankiweb in zip(self.pokemon_collection_sync_data, self.pokemon_collection_web_data):
            pokemon_name = local.get('name', unknown)
            individual_id = local.get('individual_id', unknown)
            for key in local:
                local_value = local.get(key, unknown)
                web_value = ankiweb.get(key, unknown)
                if local_value != web_value:
                    local_pokemon_differences.append(f"{pokemon_name} - {individual_id} - {key}: {local_value}")
                    web_pokemon_differences.append(f"{pokemon_name} - {individual_id} - {key}: {web_value}")

        # Prepare the local text content
        local_text_content = ""

        # Main Pokémon Data Differences
        if local_main_differences:
            local_text_content += mw.translator.translate("sync.diff.main_local") + "\n\n" + "\n".join(local_main_differences) + "\n\n"

        # Pokémon Collection Data Differences
        if local_pokemon_differences:
            local_text_content += mw.translator.translate("sync.diff.collection_local") + "\n\n" + "\n".join(local_pokemon_differences)

        # Set the local text area with the prepared content
        self.local_text_area.setPlainText(local_text_content)

        # Prepare the web text content
        web_text_content = ""

        # Main Pokémon Web Data Differences
        if web_main_differences:
            web_text_content += mw.translator.translate("sync.diff.main_web") + "\n\n" + "\n".join(web_main_differences) + "\n\n"

        # Pokémon Collection Web Data Differences
        if web_pokemon_differences:
            web_text_content += mw.translator.translate("sync.diff.collection_web") + "\n\n" + "\n".join(web_pokemon_differences)

        # Set the web text area with the prepared content
        self.web_text_area.setPlainText(web_text_content)
