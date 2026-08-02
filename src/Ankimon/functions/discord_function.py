import threading
import random
import time
from ..addon_files.lib.pypresence import Presence
from aqt.utils import showWarning, tooltip
from aqt import mw

class DiscordPresence:
    def __init__(self, client_id, large_image_url, ankimon_tracker, logger, settings_obj, parent=mw):
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            self.large_image_url = large_image_url
            self.ankimon_tracker = ankimon_tracker
            self.logger_obj = mw.logger
            self.settings = settings_obj
            self.loop = True
            self.start_time = time.time()
            self.thread = None
            self.quotes = [
                mw.translator.translate("discord.q1"),
                mw.translator.translate("discord.q2"),
                mw.translator.translate("discord.q3"),
                mw.translator.translate("discord.q4"),
                mw.translator.translate("discord.q5"),
                mw.translator.translate("discord.q6"),
                mw.translator.translate("discord.q7"),
                mw.translator.translate("discord.q8"),
                mw.translator.translate("discord.q9"),
                mw.translator.translate("discord.q10"),
            ]
            _main = self.ankimon_tracker.main_pokemon
            _enemy = self.ankimon_tracker.enemy_pokemon
            _tr = self.ankimon_tracker
            self.special_quotes = [
                mw.translator.translate("discord.s_in_battle", name=_main.name.capitalize(), level=_main.level),
                mw.translator.translate("discord.s_battling", name=_enemy.name.capitalize(), level=_enemy.level),
                mw.translator.translate("discord.s_fired_up", name=_main.name.capitalize()),
                mw.translator.translate("discord.s_opponent_tough", name=_enemy.name.capitalize()),
                mw.translator.translate("discord.s_waiting", name=_main.name.capitalize()),
                mw.translator.translate("discord.s_take_down", name=_enemy.name.capitalize()),
                mw.translator.translate("discord.s_victory", name=(_main.nickname or _main.name.capitalize())),
                mw.translator.translate("discord.s_determined", name=_main.name.capitalize()),
                mw.translator.translate("discord.s_guard_up", name=_enemy.name.capitalize()),
                mw.translator.translate("discord.s_intense", name=_main.name.capitalize()),
                mw.translator.translate("discord.s_strategy", name=_enemy.name.capitalize()),
                mw.translator.translate("discord.s_stakes", name=_main.name.capitalize()),
                mw.translator.translate("discord.s_total_reviews", count=_tr.total_reviews),
                mw.translator.translate("discord.s_good", count=_tr.good_count),
                mw.translator.translate("discord.s_again", count=_tr.again_count),
                mw.translator.translate("discord.s_easy", count=_tr.easy_count),
                mw.translator.translate("discord.s_hard", count=_tr.hard_count),
            ]
            self.state = random.choice(self.quotes)
        except Exception as e:
            mw.logger.log("info",f"Error with Discord setup: {e}")

    def update_presence(self):
        """
        Update the Discord Rich Presence with a new state message.
        """
        try:
            while self.loop:
                self.RPC.update(
                    state = random.choice(self.quotes) if int(self.settings.get("misc.discord_rich_presence_text", 1)) == 1 else random.choice(self.special_quotes),
                    large_image=self.large_image_url,
                    start=self.start_time
                )
                time.sleep(30)  # Sleep for 30 seconds before updating again
        except Exception as e:
            mw.logger.log("error",f"Error updating Discord Rich Presence: {e}")

    def start(self):
        """
        Start updating the Discord Rich Presence in a separate thread.
        """
        try:
            if not hasattr(self, 'thread') or self.thread is None or not self.thread.is_alive():
                self.loop = True
                self.thread = threading.Thread(target=self.update_presence, daemon=True)
                self.thread.start()
        except Exception as e:
            mw.logger.log("error",f"Error starting Discord Rich Presence: {e}")

    def stop(self):
        """
        Stop updating the Discord Rich Presence.
        """
        try:
            self.loop = False
            if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
                self.thread.join() # Wait for the thread to finish
                self.thread = None  # Reset the thread
            self.RPC.clear()
        except Exception as e:
            mw.logger.log("error",f"Error clearing Discord Rich Presence: {e}")

    def stop_presence(self):
        """
        Update the Discord Rich Presence to indicate a break when stopping.
        """
        try:
            self.loop = False
            if not self.loop:
                self.RPC.update(
                    state=mw.translator.translate("discord.break"),
                    large_image=self.large_image_url
                )
        except Exception as e:
            mw.logger.log("error",f"Error updating presence to break state: {e}")
