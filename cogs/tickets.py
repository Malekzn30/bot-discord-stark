import nextcord
from nextcord.ext import commands
from datetime import datetime
import os
import json
import asyncio
from typing import List
import nextcord
from nextcord import ui

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "tickets_config.json")
DATA_PATH = os.path.join(os.path.dirname(__file__), "tickets_data.json")
PANELS_PATH = os.path.join(os.path.dirname(__file__), "tickets_panels.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        default = {
            "category": None,
            "log_channel": None,
            "manager_roles": [],
            "deletor_roles": [],
            "access_roles": [],
            "embed_title": "🎫 Ticket",
            "embed_description": "Décrivez votre problème ci‑dessous. Un membre du staff viendra bientôt.",
            "counter": 0
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(default, f, indent=4)
        return default
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur write config tickets : {e}")

def load_data():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    try:
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur write data tickets : {e}")

def load_panels():
    if not os.path.exists(PANELS_PATH):
        with open(PANELS_PATH, "w") as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open(PANELS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_panels(data):
    try:
        with open(PANELS_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Erreur save panels: {e}")

CONFIG = load_config()
TICKET_DATA = load_data()  # { "channel_id": { "thread_id": ..., "owner": ... } }
PANELS = load_panels()  # { panel_id: {"channel_id":..., "message_id":..., "category":..., "title":..., "description":..., "allowed_roles": [...], "fields": [{"label":"...","style":"short|paragraph"}] } }


class PanelEditView(ui.View):
    def __init__(self, bot, panel_id: str, author):
        super().__init__(timeout=None)
        self.bot = bot
        self.panel_id = panel_id
        self.author = author
        self.add_item(ui.Button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="panel_title"))
        self.add_item(ui.Button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="panel_description"))
        self.add_item(ui.Button(label="Canal", style=nextcord.ButtonStyle.primary, custom_id="panel_channel"))
        self.add_item(ui.Button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="panel_category"))
        self.add_item(ui.Button(label="Avertissement", style=nextcord.ButtonStyle.primary, custom_id="panel_warning"))
        self.add_item(ui.Button(label="Champs", style=nextcord.ButtonStyle.primary, custom_id="panel_fields"))
        self.add_item(ui.Button(label="Rôles autorisés", style=nextcord.ButtonStyle.secondary, custom_id="panel_allowed"))
        self.add_item(ui.Button(label="Supprimer panel", style=nextcord.ButtonStyle.danger, custom_id="panel_delete"))
        self.add_item(ui.Button(label="Retour", style=nextcord.ButtonStyle.secondary, custom_id="panel_back"))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user != self.author and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Seul l'auteur ou un admin peut modifier.", ephemeral=True)
            return False
        return True

    async def handle_text(self, interaction, prompt, check):
        await interaction.response.send_message(prompt, ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            return msg
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé, annulation.", ephemeral=True)
            return None

    def panel(self):
        return PANELS.get(self.panel_id, {})

    @ui.button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="panel_title")
    async def b_title(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Nouveau titre? (`cancel` pour annuler)", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        self.panel()["title"] = msg.content
        save_panels(PANELS)
        await interaction.followup.send("✅ Titre mis à jour.", ephemeral=True)

    @ui.button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="panel_description")
    async def b_desc(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Nouvelle description? (`cancel`)", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        self.panel()["description"] = msg.content
        save_panels(PANELS)
        await interaction.followup.send("✅ Description mise à jour.", ephemeral=True)

    @ui.button(label="Canal", style=nextcord.ButtonStyle.primary, custom_id="panel_channel")
    async def b_channel(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez un salon textuel ou `cancel`.", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        cid = int("".join(ch for ch in msg.content if ch.isdigit()))
        ch = interaction.guild.get_channel(cid)
        if not isinstance(ch, nextcord.TextChannel):
            return await interaction.followup.send("⚠️ Salon invalide.", ephemeral=True)
        self.panel()["channel_id"] = ch.id
        save_panels(PANELS)
        await interaction.followup.send("✅ Salon modifié.", ephemeral=True)

    @ui.button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="panel_category")
    async def b_cat(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez une catégorie ou `cancel`.", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        cid = int("".join(ch for ch in msg.content if ch.isdigit()))
        cat = interaction.guild.get_channel(cid)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await interaction.followup.send("⚠️ Catégorie invalide.", ephemeral=True)
        self.panel()["category"] = cat.id
        save_panels(PANELS)
        await interaction.followup.send("✅ Catégorie modifiée.", ephemeral=True)

    @ui.button(label="Avertissement", style=nextcord.ButtonStyle.primary, custom_id="panel_warning")
    async def b_warning(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez le message d'avertissement (ou `none`/`cancel`).", check)
        if not msg: return
        txt = msg.content
        if txt.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt.lower() == "none":
            self.panel().pop("warning", None)
        else:
            self.panel()["warning"] = txt
        save_panels(PANELS)
        await interaction.followup.send("✅ Avertissement mis à jour.", ephemeral=True)

    @ui.button(label="Champs", style=nextcord.ButtonStyle.primary, custom_id="panel_fields")
    async def b_fields(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        await interaction.response.send_message(
            "Gestion des champs : 1️⃣ ajouter 2️⃣ supprimer\nRépondez 1 ou 2 (`cancel` pour quitter)",
            ephemeral=True
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        choice = msg.content.strip()
        if choice == "1":
            await interaction.followup.send("Entrez le label du champ, puis `short` ou `paragraph` séparés par |.", ephemeral=True)
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            parts = msg2.content.split("|",1)
            if len(parts)<2:
                return await interaction.followup.send("Format invalide.", ephemeral=True)
            label, style = parts[0].strip(), parts[1].strip()
            if style not in ("short","paragraph"):
                return await interaction.followup.send("Style invalide.", ephemeral=True)
            flds = self.panel().setdefault("fields",[])
            flds.append({"label":label,"style":style})
            save_panels(PANELS)
            await interaction.followup.send(f"✅ Champ '{label}' ajouté.", ephemeral=True)
        elif choice == "2":
            await interaction.followup.send("Indiquez le label du champ à supprimer.", ephemeral=True)
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            lbl = msg2.content.strip()
            before = len(self.panel().get("fields",[]))
            self.panel()["fields"] = [f for f in self.panel().get("fields",[]) if f.get("label")!=lbl]
            save_panels(PANELS)
            if len(self.panel().get("fields",[]))<before:
                await interaction.followup.send(f"✅ Champ '{lbl}' supprimé.", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Champ non trouvé.", ephemeral=True)
        else:
            await interaction.followup.send("Choix invalide.", ephemeral=True)
    
    @ui.button(label="Rôles autorisés", style=nextcord.ButtonStyle.secondary, custom_id="panel_allowed")
    async def b_allowed(self, button, interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez les rôles @mention séparés, `none` ou `cancel`.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            self.panel()["allowed_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            self.panel()["allowed_roles"] = [rid for rid in ids if rid and interaction.guild.get_role(rid)]
        save_panels(PANELS)
        await interaction.followup.send("✅ Rôles mis à jour.", ephemeral=True)

    @ui.button(label="Supprimer panel", style=nextcord.ButtonStyle.danger, custom_id="panel_delete")
    async def b_delete(self, button, interaction):
        PANELS.pop(self.panel_id, None)
        save_panels(PANELS)
        await interaction.response.send_message("✅ Panel supprimé.", ephemeral=True)

    @ui.button(label="Retour", style=nextcord.ButtonStyle.secondary, custom_id="panel_back")
    async def b_back(self, button, interaction):
        embed = nextcord.Embed(title="Sélectionner un panel", color=0x3498db)
        view = PanelSelectorView(self.bot, self.author)
        await interaction.response.edit_message(embed=embed, view=view)


class PanelSelect(ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Choisissez un panel…", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        pid = self.values[0]
        panel = PANELS.get(pid, {})
        embed = nextcord.Embed(title=f"Panel {pid}", color=0x3498db,
                                   description="Utilisez les boutons ci-dessous pour modifier ce panel (titres, canaux, champs, avertissement ou options).")
        # basic info
        embed.add_field(name="Titre", value=panel.get("title",""), inline=False)
        embed.add_field(name="Description", value=panel.get("description",""), inline=False)
        embed.add_field(name="Canal", value=str(panel.get("channel_id","—")), inline=False)
        embed.add_field(name="Catégorie", value=str(panel.get("category","—")), inline=False)
        roles = panel.get("allowed_roles",[])
        embed.add_field(name="Rôles autorisés", value=" ".join(f"<@&{r}>" for r in roles) or "aucun", inline=False)
        # warning if any
        warn = panel.get("warning")
        if warn:
            embed.add_field(name="Avertissement", value=warn, inline=False)
        # fields list
        flds = panel.get("fields",[])
        if flds:
            embed.add_field(name="Champs", value="\n".join(f['label'] for f in flds), inline=False)
        else:
            embed.add_field(name="Champs", value="(aucun)", inline=False)
        # options
        opts = panel.get("options",[])
        if opts:
            embed.add_field(name="Options", value="\n".join(o.get('label','') for o in opts), inline=False)
        view = PanelEditView(interaction.client, pid, interaction.user)
        await interaction.response.edit_message(embed=embed, view=view)


class PanelSelectorView(ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author
        options = []
        for pid, p in PANELS.items():
            label = p.get('title') or pid
            desc = f"chan {p.get('channel_id')}"[:50]
            options.append(nextcord.SelectOption(label=label, value=pid, description=desc))
        if options:
            self.add_item(PanelSelect(options))
        else:
            # no panels, disable
            pass


class TicketActionView(ui.View):
    """Buttons shown inside a ticket for staff actions."""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Fermer le billet", style=nextcord.ButtonStyle.danger, custom_id="action_close")
    async def close(self, button: ui.Button, interaction: nextcord.Interaction):
        cid = str(interaction.channel.id)
        # reuse existing logic from Tickets.ticket_close
        TDATA = TICKET_DATA
        if cid not in TDATA:
            return await interaction.response.send_message("❌ Cette commande ne fonctionne que dans un ticket.", ephemeral=True)
        owner = TDATA[cid]["owner"]
        if interaction.user.id != owner and not any(r.id in CONFIG["manager_roles"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Vous ne pouvez pas fermer ce ticket.", ephemeral=True)
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id,
                                                      "✅ Ticket fermé",
                                                      f"Fermé par {interaction.user}\nRaison : Aucune")
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 Ticket fermé. Le canal restera ouvert.", ephemeral=True)

    @ui.button(label="Récupérer un billet", style=nextcord.ButtonStyle.primary, custom_id="action_claim")
    async def claim(self, button: ui.Button, interaction: nextcord.Interaction):
        cid = str(interaction.channel.id)
        if cid not in TICKET_DATA:
            return await interaction.response.send_message("❌ Cette commande ne fonctionne que dans un ticket.", ephemeral=True)
        if not any(r.id in CONFIG["manager_roles"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Vous n'avez pas la permission de réclamer.", ephemeral=True)
        await interaction.channel.set_topic(f"Claimed by {interaction.user}")
        await interaction.response.send_message(f"✋ Ticket pris par {interaction.user.mention}.", ephemeral=True)
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id,
                                                      "✋ Ticket réclamé",
                                                      f"Réclamé par {interaction.user}")


class TicketConfigView(ui.View):
    """Interactive view shown by `+ticket setup` to modify configuration."""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(ui.Button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="cfg_category"))
        self.add_item(ui.Button(label="Logs", style=nextcord.ButtonStyle.primary, custom_id="cfg_logs"))
        self.add_item(ui.Button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="cfg_title"))
        self.add_item(ui.Button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="cfg_description"))
        self.add_item(ui.Button(label="Gestionnaires", style=nextcord.ButtonStyle.secondary, custom_id="cfg_managers"))
        self.add_item(ui.Button(label="Deletors", style=nextcord.ButtonStyle.secondary, custom_id="cfg_deletors"))
        self.add_item(ui.Button(label="Accès", style=nextcord.ButtonStyle.secondary, custom_id="cfg_access"))
        self.add_item(ui.Button(label="Panels", style=nextcord.ButtonStyle.success, custom_id="cfg_panels"))
        self.add_item(ui.Button(label="Options", style=nextcord.ButtonStyle.secondary, custom_id="cfg_options"))
        self.add_item(ui.Button(label="Assistant complet", style=nextcord.ButtonStyle.success, custom_id="cfg_wizard"))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        # no need to remove view
        pass

    async def handle_text(self, interaction: nextcord.Interaction, prompt: str, check):
        await interaction.response.send_message(prompt, ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            return msg
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé, annulation.", ephemeral=True)
            return None

    @ui.button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="cfg_category")
    async def button_category(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez la catégorie ou `none` ; `cancel` pour annuler.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            CONFIG["category"] = None
        else:
            cid = int("".join(ch for ch in msg.content if ch.isdigit()))
            cat = interaction.guild.get_channel(cid)
            if not isinstance(cat, nextcord.CategoryChannel):
                return await interaction.followup.send("⚠️ Catégorie invalide.", ephemeral=True)
            CONFIG["category"] = cat.id
        save_config(CONFIG)
        await interaction.followup.send("✅ Catégorie mise à jour.", ephemeral=True)

    @ui.button(label="Logs", style=nextcord.ButtonStyle.primary, custom_id="cfg_logs")
    async def button_logs(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez le salon de logs ou `none`.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            CONFIG["log_channel"] = None
        else:
            cid = int("".join(ch for ch in msg.content if ch.isdigit()))
            ch = interaction.guild.get_channel(cid)
            if not isinstance(ch, nextcord.TextChannel):
                return await interaction.followup.send("⚠️ Salon invalide.", ephemeral=True)
            CONFIG["log_channel"] = ch.id
        save_config(CONFIG)
        await interaction.followup.send("✅ Salon de logs mis à jour.", ephemeral=True)

    @ui.button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="cfg_title")
    async def button_title(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez le nouveau titre (ou `cancel`).", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        CONFIG["embed_title"] = msg.content
        save_config(CONFIG)
        await interaction.followup.send("✅ Titre mis à jour.", ephemeral=True)

    @ui.button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="cfg_description")
    async def button_description(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez la nouvelle description (ou `cancel`).", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        CONFIG["embed_description"] = msg.content
        save_config(CONFIG)
        await interaction.followup.send("✅ Description mise à jour.", ephemeral=True)

    @ui.button(label="Gestionnaires", style=nextcord.ButtonStyle.secondary, custom_id="cfg_managers")
    async def button_managers(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        prompt = "Envoyez les rôles gestionnaires (@mention séparés) ou `none`/`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            CONFIG["manager_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["manager_roles"] = [rid for rid in ids if rid and interaction.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles gestionnaires mis à jour.", ephemeral=True)

    @ui.button(label="Deletors", style=nextcord.ButtonStyle.secondary, custom_id="cfg_deletors")
    async def button_deletors(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        prompt = "Envoyez les rôles deletor (@mention séparés) ou `none`/`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            CONFIG["deletor_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["deletor_roles"] = [rid for rid in ids if rid and interaction.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles deletor mis à jour.", ephemeral=True)

    @ui.button(label="Accès", style=nextcord.ButtonStyle.secondary, custom_id="cfg_access")
    async def button_access(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        prompt = "Envoyez les rôles avec accès (@mention séparés) ou `none` pour tout le monde /`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        if txt == "none":
            CONFIG["access_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["access_roles"] = [rid for rid in ids if rid and interaction.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles d'accès mis à jour.", ephemeral=True)

    @ui.button(label="Panels", style=nextcord.ButtonStyle.success, custom_id="cfg_panels")
    async def button_panels(self, button: ui.Button, interaction: nextcord.Interaction):
        # display selector to pick a panel to edit
        if not PANELS:
            return await interaction.response.send_message("❌ Aucun panel configuré.", ephemeral=True)
        embed = nextcord.Embed(title="Sélectionner un panel", color=0x3498db)
        view = PanelSelectorView(self.bot, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ui.button(label="Options", style=nextcord.ButtonStyle.secondary, custom_id="cfg_options")
    async def button_options(self, button: ui.Button, interaction: nextcord.Interaction):
        # manage options for a panel
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        if not PANELS:
            return await interaction.response.send_message("❌ Aucun panel à modifier.", ephemeral=True)
        await interaction.response.send_message(
            "**Gestion des options de panels**\n1️⃣ Ajouter\n2️⃣ Supprimer\n3️⃣ Modifier les champs d'une option\nVotre choix? (1/2/3, `cancel` pour sortir)",
            ephemeral=True
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.", ephemeral=True)
        choice = msg.content.strip()
        if choice == "1":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option, séparés par un espace.", ephemeral=True)
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.", ephemeral=True)
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel:
                return await interaction.followup.send("❌ Panel introuvable.", ephemeral=True)
            opts = panel.setdefault("options", [])
            opts.append({"label": label, "fields": [{"label": "Sujet", "style": "short"}, {"label": "Description", "style": "paragraph"}]})
            save_panels(PANELS)
            await interaction.followup.send(f"✅ Option '{label}' ajoutée au panel {pid}.", ephemeral=True)
        elif choice == "2":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option à supprimer.", ephemeral=True)
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.", ephemeral=True)
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel or "options" not in panel:
                return await interaction.followup.send("❌ Panel ou options introuvables.", ephemeral=True)
            before = len(panel["options"])
            panel["options"] = [o for o in panel["options"] if o.get("label") != label]
            save_panels(PANELS)
            if len(panel.get("options", [])) < before:
                await interaction.followup.send(f"✅ Option '{label}' supprimée.", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Option non trouvée.", ephemeral=True)
        elif choice == "3":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option à modifier.", ephemeral=True)
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.", ephemeral=True)
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel or "options" not in panel:
                return await interaction.followup.send("❌ Panel ou options introuvables.", ephemeral=True)
            opt = next((o for o in panel["options"] if o.get("label") == label), None)
            if not opt:
                return await interaction.followup.send("⚠️ Option non trouvée.", ephemeral=True)
            # manage fields of this option similar to panel fields
            await interaction.followup.send("Gestion des champs : 1️⃣ ajouter 2️⃣ supprimer\nRépondez 1 ou 2 (`cancel` pour quitter)", ephemeral=True)
            try:
                msg3 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
            if msg3.content.lower() == "cancel":
                return await interaction.followup.send("❌ Annulé.", ephemeral=True)
            sub = msg3.content.strip()
            if sub == "1":
                await interaction.followup.send("Entrez le label du champ, puis `short` ou `paragraph` séparés par |.", ephemeral=True)
                try:
                    msg4 = await self.bot.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                    return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
                parts2 = msg4.content.split("|",1)
                if len(parts2)<2:
                    return await interaction.followup.send("Format invalide.", ephemeral=True)
                lbl, style = parts2[0].strip(), parts2[1].strip()
                if style not in ("short","paragraph"):
                    return await interaction.followup.send("Style invalide.", ephemeral=True)
                opt.setdefault("fields",[]).append({"label":lbl,"style":style})
                save_panels(PANELS)
                await interaction.followup.send(f"✅ Champ '{lbl}' ajouté à l'option.", ephemeral=True)
            elif sub == "2":
                await interaction.followup.send("Indiquez le label du champ à supprimer.", ephemeral=True)
                try:
                    msg4 = await self.bot.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                    return await interaction.followup.send("⏱️ Temps écoulé.", ephemeral=True)
                lbl = msg4.content.strip()
                before = len(opt.get("fields",[]))
                opt["fields"] = [f for f in opt.get("fields",[]) if f.get("label")!=lbl]
                save_panels(PANELS)
                if len(opt.get("fields",[]))<before:
                    await interaction.followup.send(f"✅ Champ '{lbl}' supprimé.", ephemeral=True)
                else:
                    await interaction.followup.send("⚠️ Champ non trouvé.", ephemeral=True)
            else:
                await interaction.followup.send("Choix invalide.", ephemeral=True)
        else:
            await interaction.followup.send("Choix invalide.", ephemeral=True)

    @ui.button(label="Assistant complet", style=nextcord.ButtonStyle.success, custom_id="cfg_wizard")
    async def button_wizard(self, button: ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Tapez `+ticket setup wizard` pour lancer l'assistant pas-à-pas.",
            ephemeral=True
        )


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # restore views for existing panels on startup
        for pid, panel in PANELS.items():
            try:
                chan = self.bot.get_channel(panel["channel_id"]) if panel.get("channel_id") else None
                if chan:
                    msg = None
                    try:
                        msg = chan.fetch_message(panel.get("message_id"))
                    except Exception:
                        msg = None
                    # can't reattach non-persistent views easily here; they will work when re-created
            except Exception:
                pass

    # ---------------------------
    # commandes de configuration
    # ---------------------------
    @commands.group(name="ticket", invoke_without_command=True)
    async def ticket(self, ctx):
        """+ticket → ouvre un nouveau ticket"""
        # contrôle des rôles « access »
        if CONFIG["access_roles"]:
            if not any(r.id in CONFIG["access_roles"] for r in ctx.author.roles):
                return await ctx.send("❌ Vous n'avez pas le rôle requis pour ouvrir un ticket.")
        await self._open_ticket(ctx)

    @commands.group(name="setup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx):
        """Afficher ou modifier la configuration des tickets via un panneau interactif."""
        embed = nextcord.Embed(
            title="📋 Configuration des tickets",
            color=0x3498db,
            description=(
                f"Catégorie actuelle : <#{CONFIG['category']}>\n"
                f"Salon de logs : <#{CONFIG['log_channel']}>\n"
                f"Rôles gestionnaires : {', '.join(f'<@&{r}>' for r in CONFIG['manager_roles']) or 'aucun'}\n"
                f"Rôles suppression : {', '.join(f'<@&{r}>' for r in CONFIG['deletor_roles']) or 'aucun'}\n"
                f"Rôles accès : {', '.join(f'<@&{r}>' for r in CONFIG['access_roles']) or 'tout le monde'}\n"
                f"Titre embed : {CONFIG['embed_title']}\n"
                f"Description embed : {CONFIG['embed_description']}"
            )
        )
        view = TicketConfigView(self.bot)
        await ctx.send(embed=embed, view=view)

    @ticket_setup.command(name="category")
    @commands.has_permissions(administrator=True)
    async def setup_category(self, ctx, category: nextcord.CategoryChannel):
        """Définit la **catégorie** où les tickets seront créés.

        Usage : `+ticket setup category <#catégorie>`
        Exemple : `+ticket setup category #tickets`
        """
        CONFIG["category"] = category.id
        save_config(CONFIG)
        await ctx.send(f"✅ Catégorie de tickets définie sur {category.mention}.")

    @ticket_setup.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def setup_logs(self, ctx, channel: nextcord.TextChannel):
        """Spécifie le **salon de logs** où les événements de tickets seront notés.

        Usage : `+ticket setup logs <#salon>`
        Exemple : `+ticket setup logs #logs-tickets`
        """
        CONFIG["log_channel"] = channel.id
        save_config(CONFIG)
        await ctx.send(f"✅ Salon de logs défini sur {channel.mention}.")

    @ticket_setup.command(name="title")
    @commands.has_permissions(administrator=True)
    async def setup_title(self, ctx, *, title: str):
        """Change le **titre** de l'embed envoyé dans chaque nouveau ticket.

        Usage : `+ticket setup title <texte>`
        Exemple : `+ticket setup title "🎫 Assistance"`
        """
        CONFIG["embed_title"] = title
        save_config(CONFIG)
        await ctx.send("✅ Titre de l'embed modifié.")

    @ticket_setup.command(name="description")
    @commands.has_permissions(administrator=True)
    async def setup_description(self, ctx, *, desc: str):
        """Modifie la **description** de l'embed initial d'un ticket.

        Usage : `+ticket setup description <texte>`
        Exemple : `+ticket setup description "Expliquez votre problème ci-dessous."`
        """
        CONFIG["embed_description"] = desc
        save_config(CONFIG)
        await ctx.send("✅ Description de l'embed modifiée.")

    @ticket_setup.command(name="addmanager", aliases=["add_manager","manager_add","add-manager"])
    @commands.has_permissions(administrator=True)
    async def add_manager(self, ctx, role: nextcord.Role):
        """Ajoute un rôle à la liste des **gestionnaires** (peuvent voir/fermer/claim).

        Usage : `+ticket setup addmanager <@rôle>`
        Exemple : `+ticket setup addmanager @Modérateur`
        """
        if role.id in CONFIG["manager_roles"]:
            return await ctx.send("✅ Ce rôle est déjà gestionnaire.")
        CONFIG["manager_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant voir/fermer/claim des tickets.")

    @ticket_setup.command(name="removemanager", aliases=["remove_manager","manager_remove","remove-manager"])
    @commands.has_permissions(administrator=True)
    async def remove_manager(self, ctx, role: nextcord.Role):
        """Retire un rôle de la liste des gestionnaires.

        Usage : `+ticket setup removemanager <@rôle>`
        Exemple : `+ticket setup removemanager @Modérateur`
        """
        if role.id not in CONFIG["manager_roles"]:
            return await ctx.send("❌ Ce rôle n'est pas gestionnaire.")
        CONFIG["manager_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} n'est plus gestionnaire.")

    @ticket_setup.command(name="adddeletor", aliases=["add_deletor","deletor_add","add-deletor"])
    @commands.has_permissions(administrator=True)
    async def add_deletor(self, ctx, role: nextcord.Role):
        """Ajoute un rôle autorisé à **supprimer** des tickets.

        Usage : `+ticket setup adddeletor <@rôle>`
        Exemple : `+ticket setup adddeletor @Admin`
        """
        if role.id in CONFIG["deletor_roles"]:
            return await ctx.send("✅ Ce rôle peut déjà supprimer des tickets.")
        CONFIG["deletor_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant supprimer des tickets.")

    @ticket_setup.command(name="removedeletor", aliases=["remove_deletor","deletor_remove","remove-deletor"])
    @commands.has_permissions(administrator=True)
    async def remove_deletor(self, ctx, role: nextcord.Role):
        """Retire un rôle de la liste des rôles autorisés à supprimer des tickets.

        Usage : `+ticket setup removedeletor <@rôle>`
        Exemple : `+ticket setup removedeletor @Admin`
        """
        if role.id not in CONFIG["deletor_roles"]:
            return await ctx.send("❌ Ce rôle ne peut pas supprimer de tickets.")
        CONFIG["deletor_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} ne peut plus supprimer de tickets.")

    @ticket_setup.command(name="access_add", aliases=["addaccess","access-add","add_access"])
    @commands.has_permissions(administrator=True)
    async def access_add(self, ctx, role: nextcord.Role):
        """Donne à un rôle **l'accès** pour ouvrir des tickets (par défaut tout le monde).

        Usage : `+ticket setup access_add <@rôle>`
        Exemple : `+ticket setup access_add @Membre`
        """
        if role.id in CONFIG["access_roles"]:
            return await ctx.send("✅ Ce rôle a déjà accès aux tickets.")
        CONFIG["access_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant ouvrir des tickets.")

    @ticket_setup.command(name="panel_add")
    @commands.has_permissions(administrator=True)
    async def panel_add(self, ctx, channel: nextcord.TextChannel, category: nextcord.CategoryChannel, *, title: str = "🎫 Ticket", description: str = "Cliquez pour ouvrir un ticket."):
        """Créer un panel de ticket minimal et l'envoyer dans <channel>.

        Les champs par défaut (sujet+description) peuvent être modifiés, et un
        avertissement ou des options spécifiques ajoutés via ``+ticket setup``
        (boutons "Panels" puis sélection du panel) ou avec la commande
        interactive correspondante.
        """
        pid = str(int(datetime.utcnow().timestamp() * 1000))
        panel = {
            "channel_id": channel.id,
            "message_id": None,
            "category": category.id,
            "title": title,
            "description": description,
            "allowed_roles": [],
            # default fields: sujet (short) + description (paragraph)
            "fields": [
                {"label": "Sujet", "style": "short"},
                {"label": "Description", "style": "paragraph"}
            ]
        }
        PANELS[pid] = panel
        save_panels(PANELS)

        view = TicketPanelView(self.bot, pid)
        sent = await channel.send(embed=nextcord.Embed(title=title, description=description, color=0x3498db), view=view)
        panel["message_id"] = sent.id
        save_panels(PANELS)

        await ctx.send(f"✅ Panel créé et envoyé (id: {pid}) dans {channel.mention}.")

    @ticket_setup.command(name="panel_remove")
    @commands.has_permissions(administrator=True)
    async def panel_remove(self, ctx, panel_id: str):
        if panel_id not in PANELS:
            return await ctx.send("❌ Panel introuvable.")
        PANELS.pop(panel_id)
        save_panels(PANELS)
        await ctx.send(f"✅ Panel {panel_id} supprimé.")

    @ticket_setup.command(name="panel_list")
    @commands.has_permissions(administrator=True)
    async def panel_list(self, ctx):
        if not PANELS:
            return await ctx.send("❌ Aucun panel configuré.")
        desc = ""
        for pid, p in PANELS.items():
            ch = ctx.guild.get_channel(p.get("channel_id"))
            cat = ctx.guild.get_channel(p.get("category"))
            opts = p.get("options")
            optcount = len(opts) if isinstance(opts, list) else 0
            desc += (f"• {pid} — channel: {ch.mention if ch else p.get('channel_id')} "
                     f"— category: {cat.name if cat else p.get('category')} "
                     f"— title: {p.get('title')} "
                     f"— options: {optcount}\n")
        await ctx.send(embed=nextcord.Embed(title="Panels", description=desc, color=0x3498db))

    @ticket_setup.command(name="access_remove", aliases=["removeaccess","access-remove","remove_access"])
    @commands.has_permissions(administrator=True)
    async def access_remove(self, ctx, role: nextcord.Role):
        """Retire l'accès d'un rôle pour l'ouverture de tickets.

        Usage : `+ticket setup access_remove <@rôle>`
        Exemple : `+ticket setup access_remove @Visiteur`
        """
        if role.id not in CONFIG["access_roles"]:
            return await ctx.send("❌ Ce rôle n'avait pas accès aux tickets.")
        CONFIG["access_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} ne peut plus ouvrir de tickets.")

    @ticket_setup.command(name="wizard", aliases=["interactive","config","menu"])
    @commands.has_permissions(administrator=True)
    async def setup_wizard(self, ctx):
        """Assistant pas-à-pas pour configurer les tickets."""
        def parse_id(text: str):
            import re
            m = re.search(r"\d+", text)
            return int(m.group()) if m else None

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("🛠️ **Assistant de configuration des tickets**\nEnvoyez `cancel` à tout moment pour quitter.")

        # category
        await ctx.send(f"1️⃣ Catégorie actuelle : <#{CONFIG.get('category')}>")
        await ctx.send("Mentionnez la catégorie ou écrivez `none` pour ne pas en définir.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() == "none":
            CONFIG["category"] = None
        else:
            cid = parse_id(msg.content)
            cat = ctx.guild.get_channel(cid) if cid else None
            if not isinstance(cat, nextcord.CategoryChannel):
                await ctx.send("⚠️ Catégorie invalide, elle restera inchangée.")
            else:
                CONFIG["category"] = cat.id

        # log channel
        await ctx.send(f"2️⃣ Salon de logs actuel : <#{CONFIG.get('log_channel')}>")
        await ctx.send("Mentionnez un salon textuel pour les logs ou `none`.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() == "none":
            CONFIG["log_channel"] = None
        else:
            cid = parse_id(msg.content)
            ch = ctx.guild.get_channel(cid) if cid else None
            if not isinstance(ch, nextcord.TextChannel):
                await ctx.send("⚠️ Salon invalide, il restera inchangé.")
            else:
                CONFIG["log_channel"] = ch.id

        # manager roles
        await ctx.send(f"3️⃣ Rôles gestionnaires actuels : {', '.join(f'<@&{r}>' for r in CONFIG.get('manager_roles', [])) or 'aucun'}")
        await ctx.send("Envoyez des rôles @mention séparés par un espace, ou `none` pour aucun.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() == "none":
            CONFIG["manager_roles"] = []
        else:
            ids = [parse_id(tok) for tok in msg.content.split()]
            CONFIG["manager_roles"] = [rid for rid in ids if rid and ctx.guild.get_role(rid)]

        # deletor roles
        await ctx.send(f"4️⃣ Rôles deletor actuels : {', '.join(f'<@&{r}>' for r in CONFIG.get('deletor_roles', [])) or 'aucun'}")
        await ctx.send("Envoyez des rôles @mention séparés par un espace, ou `none` pour aucun.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() == "none":
            CONFIG["deletor_roles"] = []
        else:
            ids = [parse_id(tok) for tok in msg.content.split()]
            CONFIG["deletor_roles"] = [rid for rid in ids if rid and ctx.guild.get_role(rid)]

        # access roles
        await ctx.send(f"5️⃣ Rôles avec accès actuels : {', '.join(f'<@&{r}>' for r in CONFIG.get('access_roles', [])) or 'tout le monde'}")
        await ctx.send("Envoyez des rôles @mention séparés par un espace, ou `none` pour tout le monde.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() == "none":
            CONFIG["access_roles"] = []
        else:
            ids = [parse_id(tok) for tok in msg.content.split()]
            CONFIG["access_roles"] = [rid for rid in ids if rid and ctx.guild.get_role(rid)]

        # embed title
        await ctx.send(f"6️⃣ Titre actuel de l'embed : {CONFIG.get('embed_title')}")
        await ctx.send("Envoyez le nouveau titre ou `none` pour garder.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() != "none":
            CONFIG["embed_title"] = msg.content

        # embed description
        await ctx.send(f"7️⃣ Description actuelle de l'embed : {CONFIG.get('embed_description')}\nEnvoyez la nouvelle description ou `none` pour garder.")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=180)
        except asyncio.TimeoutError:
            return await ctx.send("⏱️ Temps écoulé, assistant annulé.")
        if msg.content.lower() == "cancel":
            return await ctx.send("❌ Assistant annulé.")
        if msg.content.lower() != "none":
            CONFIG["embed_description"] = msg.content

        # summary and save
        save_config(CONFIG)
        await ctx.send("✅ Configuration sauvegardée !")

    # ---------------------------
    # actions dans un ticket
    # ---------------------------
    @ticket.command(name="claim")
    async def ticket_claim(self, ctx):
        if str(ctx.channel.id) not in TICKET_DATA:
            return await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
        if not any(r.id in CONFIG["manager_roles"] for r in ctx.author.roles):
            return await ctx.send("❌ Vous n'avez pas la permission de réclamer.")
        await ctx.channel.set_topic(f"Claimed by {ctx.author}")
        await ctx.send(f"✋ Ticket pris par {ctx.author.mention}.")
        await self._log_event(ctx.channel.id, "✋ Ticket réclamé", f"Réclamé par {ctx.author}")

    @ticket.command(name="close")
    async def ticket_close(self, ctx, *, reason: str = None):
        cid = str(ctx.channel.id)
        if cid not in TICKET_DATA:
            return await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
        owner = TICKET_DATA[cid]["owner"]
        if ctx.author.id != owner and not any(r.id in CONFIG["manager_roles"] for r in ctx.author.roles):
            return await ctx.send("❌ Vous ne pouvez pas fermer ce ticket.")
        await self._log_event(ctx.channel.id,
                              "✅ Ticket fermé",
                              f"Fermé par {ctx.author}\nRaison : {reason or 'Aucune'}")
        # empêche l'auteur d'envoyer à nouveau
        await ctx.channel.set_permissions(ctx.author, send_messages=False)
        await ctx.send("🔒 Ticket fermé. Le canal restera ouvert.")
    
    @ticket.command(name="delete")
    async def ticket_delete(self, ctx):
        cid = str(ctx.channel.id)
        if cid not in TICKET_DATA:
            return await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
        if not any(r.id in CONFIG["deletor_roles"] for r in ctx.author.roles):
            return await ctx.send("❌ Vous n'avez pas la permission de supprimer ce ticket.")
        await self._log_event(ctx.channel.id,
                              "🗑️ Ticket supprimé",
                              f"Supprimé par {ctx.author}")
        await ctx.channel.delete(reason=f"Ticket supprimé par {ctx.author}")
        TICKET_DATA.pop(cid, None)
        save_data(TICKET_DATA)

    # ---------------------------
    # helpers & logs
    # ---------------------------
    async def _open_ticket(self, ctx):
        # Backwards-compatible: if called without panel, use global CONFIG
        category_id = CONFIG.get("category")
        if category_id is None:
            return await ctx.send("❌ La catégorie de tickets n'est pas configurée.")
        category = ctx.guild.get_channel(category_id)
        if category is None or not isinstance(category, nextcord.CategoryChannel):
            return await ctx.send("❌ La catégorie configurée est invalide.")

        # incrémenter le compteur
        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"ticket-{CONFIG['counter']}"

        overwrites = {
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            ctx.author: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for rid in CONFIG["manager_roles"]:
            role = ctx.guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)

        chan = await ctx.guild.create_text_channel(name, category=category, overwrites=overwrites)
        embed = nextcord.Embed(
            title=CONFIG["embed_title"],
            description=CONFIG["embed_description"],
            color=0x95A5A6,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']}")
        await chan.send(ctx.author.mention, embed=embed)

        # création du thread de logs
        thread_id = await self._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {"thread_id": thread_id, "owner": ctx.author.id}
        save_data(TICKET_DATA)

        await ctx.send(f"✅ Ticket créé : {chan.mention}")

    async def _create_log_thread(self, ticket_chan: nextcord.TextChannel):
        if CONFIG["log_channel"] is None:
            return None
        log_chan = self.bot.get_channel(CONFIG["log_channel"])
        if log_chan is None:
            return None
        embed = nextcord.Embed(
            title="🎫 Ticket créé",
            description=f"Canal : {ticket_chan.mention}\nPropriétaire : {ticket_chan.topic or ticket_chan.name}",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        msg = await log_chan.send(embed=embed)
        thread = await msg.create_thread(name=f"ticket-{ticket_chan.id}", auto_archive_duration=1440)
        return thread.id

    async def _log_event(self, ticket_chan_id: int, title: str, description: str):
        cid = str(ticket_chan_id)
        info = TICKET_DATA.get(cid)
        if not info:
            return
        thread = self.bot.get_channel(info["thread_id"])
        if thread:
            embed = nextcord.Embed(
                title=title,
                description=description,
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            await thread.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        cid = str(message.channel.id)
        if cid in TICKET_DATA:
            await self._log_event(message.channel.id, "💬 Message", f"{message.author} :\n{message.content or '(embed/fichier)'}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        cid = str(before.channel.id)
        if cid in TICKET_DATA and before.content != after.content:
            await self._log_event(before.channel.id,
                                  "✏️ Message édité",
                                  f"Avant : {before.content or '(vide)'}\nAprès : {after.content or '(vide)'}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        cid = str(message.channel.id)
        if cid in TICKET_DATA:
            await self._log_event(message.channel.id,
                                  "🗑️ Message supprimé",
                                  f"{message.author} :\n{message.content or '(embed/fichier)'}")


def setup(bot):
    bot.add_cog(Tickets(bot))


class TicketPanelView(ui.View):
    def __init__(self, bot, panel_id: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.panel_id = panel_id

    @ui.button(label="Ouvrir un ticket", style=nextcord.ButtonStyle.primary, custom_id="ticket_open_button")
    async def open_button(self, button: ui.Button, interaction: nextcord.Interaction):
        pid = self.panel_id
        panel = PANELS.get(pid)
        if not panel:
            return await interaction.response.send_message("❌ Panel introuvable.", ephemeral=True)

        # permission check
        allowed = panel.get("allowed_roles", []) or []
        if allowed:
            if not any(r.id in allowed for r in interaction.user.roles):
                return await interaction.response.send_message("❌ Vous n'avez pas la permission d'ouvrir ce ticket.", ephemeral=True)
        # warn first so it's shown even if there are options
        warn = panel.get("warning")
        if warn:
            wembed = nextcord.Embed(description=warn, color=0xFFA500)
            await interaction.response.send_message(embed=wembed, ephemeral=True)
            await asyncio.sleep(0.5)
        # if the panel has options, ask the user to pick one first
        opts = panel.get("options", [])
        if opts:
            # create a view with select menu
            class OptionSelector(ui.Select):
                def __init__(self):
                    select_opts = []
                    for idx, o in enumerate(opts):
                        select_opts.append(nextcord.SelectOption(label=o.get("label","option"), value=str(idx)))
                    super().__init__(placeholder="Choisissez une option…", min_values=1, max_values=1, options=select_opts)

                async def callback(self, interaction: nextcord.Interaction):
                    choice = int(self.values[0])
                    opt = opts[choice]
                    # build modal using the chosen option's fields
                    class OptModal(ui.Modal):
                        def __init__(self):
                            super().__init__(title=opt.get("label", panel.get("title","Ticket")))
                            for f in opt.get("fields", []):
                                style = nextcord.TextInputStyle.short if f.get("style") == "short" else nextcord.TextInputStyle.paragraph
                                self.add_item(nextcord.ui.TextInput(label=f.get("label","Réponse"), style=style, required=True))

                        async def callback(self, modal_interaction: nextcord.Interaction):
                            # reuse creation logic from parent open_button
                            guild = modal_interaction.guild
                            category = guild.get_channel(panel.get("category"))
                            if category is None:
                                return await modal_interaction.response.send_message("❌ Catégorie du panel invalide.", ephemeral=True)
                            CONFIG["counter"] = CONFIG.get("counter", 0) + 1
                            save_config(CONFIG)
                            name = f"ticket-{CONFIG['counter']}"
                            overwrites = {guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
                            overwrites[modal_interaction.user] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
                            for rid in CONFIG.get("manager_roles", []):
                                role = guild.get_role(rid)
                                if role:
                                    overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
                            chan = await guild.create_text_channel(name, category=category, overwrites=overwrites)
                            desc = ""
                            for item in self.children:
                                desc += f"**{item.label}**\n{item.value}\n\n"
                            embed = nextcord.Embed(title=panel.get("title","Ticket ouvert"), description=panel.get("description",""), color=0x95A5A6, timestamp=datetime.utcnow())
                            embed.add_field(name="Infos", value=desc, inline=False)
                            embed.set_footer(text=f"Ticket #{CONFIG['counter']}")
                            await chan.send(modal_interaction.user.mention, embed=embed)
                            TICKET_DATA[str(chan.id)] = {"thread_id": None, "owner": modal_interaction.user.id}
                            save_data(TICKET_DATA)
                            await modal_interaction.response.send_message(f"✅ Ticket créé : {chan.mention}", ephemeral=True)
                    await interaction.response.send_modal(OptModal())

            view = ui.View(timeout=None)
            view.add_item(OptionSelector())
            return await interaction.response.send_message("Veuillez choisir une option pour votre ticket :", view=view, ephemeral=True)

        # build modal
        class TicketModal(ui.Modal):
            def __init__(self):
                super().__init__(title=panel.get("title", "Ticket"))
                for f in panel.get("fields", []):
                    style = nextcord.TextInputStyle.short if f.get("style") == "short" else nextcord.TextInputStyle.paragraph
                    self.add_item(nextcord.ui.TextInput(label=f.get("label", "Réponse"), style=style, required=True))

            async def callback(self, modal_interaction: nextcord.Interaction):
                # create ticket channel
                guild = modal_interaction.guild
                category = guild.get_channel(panel.get("category"))
                if category is None:
                    return await modal_interaction.response.send_message("❌ Catégorie du panel invalide.", ephemeral=True)

                # increment counter
                CONFIG["counter"] = CONFIG.get("counter", 0) + 1
                save_config(CONFIG)
                name = f"ticket-{CONFIG['counter']}"

                overwrites = {guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
                # owner
                overwrites[modal_interaction.user] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
                # managers
                for rid in CONFIG.get("manager_roles", []):
                    role = guild.get_role(rid)
                    if role:
                        overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)

                chan = await guild.create_text_channel(name, category=category, overwrites=overwrites)

                # prepare embed with modal responses
                desc = ""
                for item in self.children:
                    desc += f"**{item.label}**\n{item.value}\n\n"

                embed = nextcord.Embed(title=panel.get("title", "Ticket ouvert"), description=panel.get("description", ""), color=0x95A5A6, timestamp=datetime.utcnow())
                embed.add_field(name="Infos", value=desc, inline=False)
                embed.set_footer(text=f"Ticket #{CONFIG['counter']}")

                await chan.send(modal_interaction.user.mention, embed=embed)

                # track ticket
                thread_id = await Tickets._create_log_thread if False else None
                TICKET_DATA[str(chan.id)] = {"thread_id": None, "owner": modal_interaction.user.id}
                save_data(TICKET_DATA)

                await modal_interaction.response.send_message(f"✅ Ticket créé : {chan.mention}", ephemeral=True)

        await interaction.response.send_modal(TicketModal())