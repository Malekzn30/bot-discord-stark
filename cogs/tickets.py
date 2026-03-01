import nextcord
from nextcord.ext import commands
import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from nextcord import ui
from nextcord.ui import Modal, TextInput
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paths import TICKETS_CONFIG_PATH, TICKETS_DATA_PATH, TICKETS_PANELS_PATH

CONFIG_PATH = TICKETS_CONFIG_PATH
DATA_PATH = TICKETS_DATA_PATH
PANELS_PATH = TICKETS_PANELS_PATH

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
            "counter": 0,
            # Nouvelles fonctionnalités
            "pre_ticket_message": "🎫 Bienvenue ! Veuillez choisir une catégorie pour votre ticket.",
            "ticket_open_message": "✅ Votre ticket a été créé ! Notre staff vous aidera dans les plus brefs délais.",
            "categories": {
                "support": {
                    "name": "🛠️ Support Technique",
                    "description": "Problèmes techniques, bugs, aide",
                    "emoji": "🛠️",
                    "color": 0x3498db,
                    "questions": [
                        {
                            "label": "Décrivez votre problème",
                            "placeholder": "Expliquez en détail ce qui ne fonctionne pas...",
                            "style": "paragraph",
                            "required": True
                        }
                    ]
                },
                "general": {
                    "name": "💬 Discussion Générale",
                    "description": "Questions, suggestions, autre",
                    "emoji": "💬", 
                    "color": 0x2ecc71,
                    "questions": [
                        {
                            "label": "Quel est le sujet de votre demande ?",
                            "placeholder": "Décrivez brièvement votre demande...",
                            "style": "short",
                            "required": True
                        }
                    ]
                }
            }
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


class TicketQuestionnaire(Modal):
    """Modal pour le questionnaire avant création de ticket"""
    def __init__(self, category_key: str, category_data: Dict, bot):
        super().__init__(title=f"Ticket - {category_data.get('name', 'Questionnaire')}")
        self.category_key = category_key
        self.category_data = category_data
        self.bot = bot
        
        # Ajouter les questions dynamiquement
        for i, question in enumerate(category_data.get("questions", [])):
            text_input = TextInput(
                label=question["label"],
                placeholder=question.get("placeholder", "Tapez votre réponse ici..."),
                required=question.get("required", True),
                style=nextcord.TextInputStyle.paragraph if question.get("style") == "paragraph" else nextcord.TextInputStyle.short,
                custom_id=f"question_{i}"
            )
            self.add_item(text_input)

    async def callback(self, interaction: nextcord.Interaction):
        # Récupérer les réponses
        responses = {}
        for i, item in enumerate(self.children):
            responses[f"question_{i}"] = item.value
        
        # Créer le ticket avec les réponses
        await self._create_ticket_with_responses(interaction, responses)

    async def _create_ticket_with_responses(self, interaction: nextcord.Interaction, responses: Dict):
        """Créer le ticket avec les réponses du questionnaire"""
        category_data = self.category_data
        guild = interaction.guild
        
        # Trouver la catégorie Discord
        discord_category = guild.get_channel(CONFIG.get("category"))
        if not discord_category:
            return await interaction.response.send_message("❌ La catégorie de tickets n'est pas configurée.", ephemeral=True)
        
        # Incrémenter le compteur
        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"{category_data.get('emoji', '🎫')}-ticket-{CONFIG['counter']}"
        
        # Créer le canal avec permissions
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Ajouter permissions pour les rôles gestionnaires
        for rid in CONFIG.get("manager_roles", []):
            role = guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        chan = await guild.create_text_channel(
            name, 
            category=discord_category, 
            overwrites=overwrites,
            topic=f"Ticket {category_data.get('name')} - {interaction.user}"
        )
        
        # Créer l'embed d'ouverture avec les réponses
        embed = nextcord.Embed(
            title=f"{category_data.get('emoji', '🎫')} {category_data.get('name', 'Ticket')}",
            description=CONFIG.get("ticket_open_message", "✅ Votre ticket a été créé !"),
            color=category_data.get("color", 0x3498db),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']} • Créé par {interaction.user}")
        embed.add_field(name="👤 Utilisateur", value=interaction.user.mention, inline=True)
        embed.add_field(name="📂 Catégorie", value=category_data.get("name", "Inconnue"), inline=True)
        
        # Ajouter les réponses du questionnaire
        if responses:
            embed.add_field(name="📝 Réponses", value="", inline=False)
            for i, question in enumerate(category_data.get("questions", [])):
                response = responses.get(f"question_{i}", "Non renseigné")
                embed.add_field(name=question["label"], value=response, inline=False)
        
        # Envoyer le message d'ouverture
        await chan.send(f"{interaction.user.mention} {CONFIG.get('manager_roles', [])}", embed=embed)
        
        # Ajouter la vue d'actions
        view = TicketActionView(self.bot)
        await chan.send("🛠️ **Actions du ticket** :", view=view)
        
        # Sauvegarder les données du ticket
        thread_id = await self.bot.get_cog("Tickets")._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {
            "thread_id": thread_id, 
            "owner": interaction.user.id,
            "category": self.category_key,
            "responses": responses
        }
        save_data(TICKET_DATA)
        
        await interaction.response.send_message(f"✅ Ticket créé : {chan.mention}", ephemeral=True)


class CategorySelectView(ui.View):
    """Vue pour la sélection des catégories de tickets"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
        # Ajouter les boutons pour chaque catégorie
        categories = CONFIG.get("categories", {})
        for cat_key, cat_data in categories.items():
            button = ui.Button(
                label=cat_data.get("name", cat_key.title()),
                emoji=cat_data.get("emoji"),
                style=nextcord.ButtonStyle.primary,
                custom_id=f"category_{cat_key}"
            )
            button.callback = self.create_category_callback(cat_key, cat_data)
            self.add_item(button)

    def create_category_callback(self, category_key: str, category_data: Dict):
        """Créer un callback pour chaque catégorie"""
        async def callback(interaction: nextcord.Interaction):
            # Vérifier si la catégorie a des questions
            if category_data.get("questions"):
                # Ouvrir la modal de questionnaire
                modal = TicketQuestionnaire(category_key, category_data, self.bot)
                await interaction.response.send_modal(modal)
            else:
                # Créer directement le ticket
                await self._create_simple_ticket(interaction, category_key, category_data)
        return callback

    async def _create_simple_ticket(self, interaction: nextcord.Interaction, category_key: str, category_data: Dict):
        """Créer un ticket simple sans questionnaire"""
        guild = interaction.guild
        discord_category = guild.get_channel(CONFIG.get("category"))
        
        if not discord_category:
            return await interaction.response.send_message("❌ La catégorie de tickets n'est pas configurée.", ephemeral=True)
        
        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"{category_data.get('emoji', '🎫')}-ticket-{CONFIG['counter']}"
        
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        for rid in CONFIG.get("manager_roles", []):
            role = guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        chan = await guild.create_text_channel(name, category=discord_category, overwrites=overwrites)
        
        embed = nextcord.Embed(
            title=f"{category_data.get('emoji', '🎫')} {category_data.get('name', 'Ticket')}",
            description=CONFIG.get("ticket_open_message", "✅ Votre ticket a été créé !"),
            color=category_data.get("color", 0x3498db),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']} • Créé par {interaction.user}")
        embed.add_field(name="👤 Utilisateur", value=interaction.user.mention, inline=True)
        embed.add_field(name="📂 Catégorie", value=category_data.get("name", "Inconnue"), inline=True)
        
        await chan.send(f"{interaction.user.mention}", embed=embed)
        
        view = TicketActionView(self.bot)
        await chan.send("🛠️ **Actions du ticket** :", view=view)
        
        thread_id = await self.bot.get_cog("Tickets")._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {
            "thread_id": thread_id, 
            "owner": interaction.user.id,
            "category": category_key
        }
        save_data(TICKET_DATA)
        
        await interaction.response.send_message(f"✅ Ticket créé : {chan.mention}", ephemeral=True)


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
        if ctx.author != self.author and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Seul l'auteur ou un admin peut modifier.")
            return False
        return True

    async def handle_text(self, interaction, prompt, check):
        await ctx.send(prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            return msg
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé, annulation.")
            return None

    def panel(self):
        return PANELS.get(self.panel_id, {})

    @ui.button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="panel_title")
    async def b_title(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Nouveau titre? (`cancel` pour annuler)", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        self.panel()["title"] = msg.content
        save_panels(PANELS)
        await interaction.followup.send("✅ Titre mis à jour.")

    @ui.button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="panel_description")
    async def b_desc(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Nouvelle description? (`cancel`)", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        self.panel()["description"] = msg.content
        save_panels(PANELS)
        await interaction.followup.send("✅ Description mise à jour.")

    @ui.button(label="Canal", style=nextcord.ButtonStyle.primary, custom_id="panel_channel")
    async def b_channel(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez un salon textuel ou `cancel`.", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        cid = int("".join(ch for ch in msg.content if ch.isdigit()))
        ch = ctx.guild.get_channel(cid)
        if not isinstance(ch, nextcord.TextChannel):
            return await interaction.followup.send("⚠️ Salon invalide.")
        self.panel()["channel_id"] = ch.id
        save_panels(PANELS)
        await interaction.followup.send("✅ Salon modifié.")

    @ui.button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="panel_category")
    async def b_cat(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez une catégorie ou `cancel`.", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        cid = int("".join(ch for ch in msg.content if ch.isdigit()))
        cat = ctx.guild.get_channel(cid)
        if not isinstance(cat, nextcord.CategoryChannel):
            return await interaction.followup.send("⚠️ Catégorie invalide.")
        self.panel()["category"] = cat.id
        save_panels(PANELS)
        await interaction.followup.send("✅ Catégorie modifiée.")

    @ui.button(label="Avertissement", style=nextcord.ButtonStyle.primary, custom_id="panel_warning")
    async def b_warning(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez le message d'avertissement (ou `none`/`cancel`).", check)
        if not msg: return
        txt = msg.content
        if txt.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt.lower() == "none":
            self.panel().pop("warning", None)
        else:
            self.panel()["warning"] = txt
        save_panels(PANELS)
        await interaction.followup.send("✅ Avertissement mis à jour.")

    @ui.button(label="Champs", style=nextcord.ButtonStyle.primary, custom_id="panel_fields")
    async def b_fields(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        await ctx.send(
            "Gestion des champs : 1️⃣ ajouter 2️⃣ supprimer\nRépondez 1 ou 2 (`cancel` pour quitter)",
            
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏱️ Temps écoulé.")
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        choice = msg.content.strip()
        if choice == "1":
            await interaction.followup.send("Entrez le label du champ, puis `short` ou `paragraph` séparés par |.")
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            parts = msg2.content.split("|",1)
            if len(parts)<2:
                return await interaction.followup.send("Format invalide.")
            label, style = parts[0].strip(), parts[1].strip()
            if style not in ("short","paragraph"):
                return await interaction.followup.send("Style invalide.")
            flds = self.panel().setdefault("fields",[])
            flds.append({"label":label,"style":style})
            save_panels(PANELS)
            await interaction.followup.send(f"✅ Champ '{label}' ajouté.")
        elif choice == "2":
            await interaction.followup.send("Indiquez le label du champ à supprimer.")
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            lbl = msg2.content.strip()
            before = len(self.panel().get("fields",[]))
            self.panel()["fields"] = [f for f in self.panel().get("fields",[]) if f.get("label")!=lbl]
            save_panels(PANELS)
            if len(self.panel().get("fields",[]))<before:
                await interaction.followup.send(f"✅ Champ '{lbl}' supprimé.")
            else:
                await interaction.followup.send("⚠️ Champ non trouvé.")
        else:
            await interaction.followup.send("Choix invalide.")
    
    @ui.button(label="Rôles autorisés", style=nextcord.ButtonStyle.secondary, custom_id="panel_allowed")
    async def b_allowed(self, button, interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez les rôles @mention séparés, `none` ou `cancel`.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            self.panel()["allowed_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            self.panel()["allowed_roles"] = [rid for rid in ids if rid and interaction.ctx.guild.get_role(rid)]
        save_panels(PANELS)
        await interaction.followup.send("✅ Rôles mis à jour.")

    @ui.button(label="Supprimer panel", style=nextcord.ButtonStyle.danger, custom_id="panel_delete")
    async def b_delete(self, button, interaction):
        PANELS.pop(self.panel_id, None)
        save_panels(PANELS)
        await ctx.send("✅ Panel supprimé.")

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
        embed.add_field(name="Titre", value=CONFIG.get("embed_title",""), inline=False)
        embed.add_field(name="Description", value=CONFIG.get("embed_description",""), inline=False)
        embed.add_field(name="Canal", value=str(CONFIG.get("channel_id","—")), inline=False)
        embed.add_field(name="Catégorie", value=str(CONFIG.get("category","—")), inline=False)
        roles = CONFIG.get("allowed_roles",[])
        embed.add_field(name="Rôles autorisés", value=" ".join(f"<@&{r}>" for r in roles) or "aucun", inline=False)
        # warning if any
        warn = CONFIG.get("warning")
        if warn:
            embed.add_field(name="Avertissement", value=warn, inline=False)
        # fields list
        flds = CONFIG.get("fields",[])
        if flds:
            embed.add_field(name="Champs", value="\n".join(f['label'] for f in flds), inline=False)
        else:
            embed.add_field(name="Champs", value="(aucun)", inline=False)
        # options
        opts = CONFIG.get("options",[])
        if opts:
            embed.add_field(name="Options", value="\n".join(o.get('label','') for o in opts), inline=False)
        view = PanelEditView(interaction.client, pid, ctx.author)
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
            return await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
        owner = TDATA[cid]["owner"]
        if ctx.author.id != owner and not any(r.id in CONFIG["manager_roles"] for r in ctx.author.roles):
            return await ctx.send("❌ Vous ne pouvez pas fermer ce ticket.")
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id,
                                                      "✅ Ticket fermé",
                                                      f"Fermé par {ctx.author}\nRaison : Aucune")
        await interaction.channel.set_permissions(ctx.author, send_messages=False)
        await ctx.send("🔒 Ticket fermé. Le canal restera ouvert.")

    @ui.button(label="Récupérer un billet", style=nextcord.ButtonStyle.primary, custom_id="action_claim")
    async def claim(self, button: ui.Button, interaction: nextcord.Interaction):
        cid = str(interaction.channel.id)
        if cid not in TICKET_DATA:
            return await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
        if not any(r.id in CONFIG["manager_roles"] for r in ctx.author.roles):
            return await ctx.send("❌ Vous n'avez pas la permission de réclamer.")
        await interaction.channel.set_topic(f"Claimed by {ctx.author}")
        await ctx.send(f"✋ Ticket pris par {ctx.author.mention}.")
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id,
                                                      "✋ Ticket réclamé",
                                                      f"Réclamé par {ctx.author}")


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
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Vous devez être administrateur.")
            return False
        return True

    async def on_timeout(self):
        # no need to remove view
        pass

    async def handle_text(self, interaction: nextcord.Interaction, prompt: str, check):
        await ctx.send(prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            return msg
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé, annulation.")
            return None

    @ui.button(label="Catégorie", style=nextcord.ButtonStyle.primary, custom_id="cfg_category")
    async def button_category(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez la catégorie ou `none` ; `cancel` pour annuler.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            CONFIG["category"] = None
        else:
            cid = int("".join(ch for ch in msg.content if ch.isdigit()))
            cat = ctx.guild.get_channel(cid)
            if not isinstance(cat, nextcord.CategoryChannel):
                return await interaction.followup.send("⚠️ Catégorie invalide.")
            CONFIG["category"] = cat.id
        save_config(CONFIG)
        await interaction.followup.send("✅ Catégorie mise à jour.")

    @ui.button(label="Logs", style=nextcord.ButtonStyle.primary, custom_id="cfg_logs")
    async def button_logs(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Mentionnez le salon de logs ou `none`.", check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            CONFIG["log_channel"] = None
        else:
            cid = int("".join(ch for ch in msg.content if ch.isdigit()))
            ch = ctx.guild.get_channel(cid)
            if not isinstance(ch, nextcord.TextChannel):
                return await interaction.followup.send("⚠️ Salon invalide.")
            CONFIG["log_channel"] = ch.id
        save_config(CONFIG)
        await interaction.followup.send("✅ Salon de logs mis à jour.")

    @ui.button(label="Titre", style=nextcord.ButtonStyle.primary, custom_id="cfg_title")
    async def button_title(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez le nouveau titre (ou `cancel`).", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        CONFIG["embed_title"] = msg.content
        save_config(CONFIG)
        await interaction.followup.send("✅ Titre mis à jour.")

    @ui.button(label="Description", style=nextcord.ButtonStyle.primary, custom_id="cfg_description")
    async def button_description(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        msg = await self.handle_text(interaction, "Envoyez la nouvelle description (ou `cancel`).", check)
        if not msg: return
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        CONFIG["embed_description"] = msg.content
        save_config(CONFIG)
        await interaction.followup.send("✅ Description mise à jour.")

    @ui.button(label="Gestionnaires", style=nextcord.ButtonStyle.secondary, custom_id="cfg_managers")
    async def button_managers(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        prompt = "Envoyez les rôles gestionnaires (@mention séparés) ou `none`/`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            CONFIG["manager_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["manager_roles"] = [rid for rid in ids if rid and interaction.ctx.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles gestionnaires mis à jour.")

    @ui.button(label="Deletors", style=nextcord.ButtonStyle.secondary, custom_id="cfg_deletors")
    async def button_deletors(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        prompt = "Envoyez les rôles deletor (@mention séparés) ou `none`/`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            CONFIG["deletor_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["deletor_roles"] = [rid for rid in ids if rid and interaction.ctx.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles deletor mis à jour.")

    @ui.button(label="Accès", style=nextcord.ButtonStyle.secondary, custom_id="cfg_access")
    async def button_access(self, button: ui.Button, interaction: nextcord.Interaction):
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        prompt = "Envoyez les rôles avec accès (@mention séparés) ou `none` pour tout le monde /`cancel`."
        msg = await self.handle_text(interaction, prompt, check)
        if not msg: return
        txt = msg.content.lower()
        if txt == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        if txt == "none":
            CONFIG["access_roles"] = []
        else:
            ids = [int("".join(ch for ch in tok if ch.isdigit())) for tok in msg.content.split()]
            CONFIG["access_roles"] = [rid for rid in ids if rid and interaction.ctx.guild.get_role(rid)]
        save_config(CONFIG)
        await interaction.followup.send("✅ Rôles d'accès mis à jour.")

    @ui.button(label="Panels", style=nextcord.ButtonStyle.success, custom_id="cfg_panels")
    async def button_panels(self, button: ui.Button, interaction: nextcord.Interaction):
        # display selector to pick a panel to edit
        if not PANELS:
            return await ctx.send("❌ Aucun panel configuré.")
        embed = nextcord.Embed(title="Sélectionner un panel", color=0x3498db)
        view = PanelSelectorView(self.bot, ctx.author)
        await ctx.send(embed=embed, view=view)

    @ui.button(label="Options", style=nextcord.ButtonStyle.secondary, custom_id="cfg_options")
    async def button_options(self, button: ui.Button, interaction: nextcord.Interaction):
        # manage options for a panel
        def check(m): return m.author == ctx.author and m.channel == interaction.channel
        if not PANELS:
            return await ctx.send("❌ Aucun panel à modifier.")
        await ctx.send(
            "**Gestion des options de panels**\n1️⃣ Ajouter\n2️⃣ Supprimer\n3️⃣ Modifier les champs d'une option\nVotre choix? (1/2/3, `cancel` pour sortir)",
            
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏱️ Temps écoulé.")
        if msg.content.lower() == "cancel":
            return await interaction.followup.send("❌ Annulé.")
        choice = msg.content.strip()
        if choice == "1":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option, séparés par un espace.")
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.")
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel:
                return await interaction.followup.send("❌ Panel introuvable.")
            opts = panel.setdefault("options", [])
            opts.append({"label": label, "fields": [{"label": "Sujet", "style": "short"}, {"label": "Description", "style": "paragraph"}]})
            save_panels(PANELS)
            await interaction.followup.send(f"✅ Option '{label}' ajoutée au panel {pid}.")
        elif choice == "2":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option à supprimer.")
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.")
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel or "options" not in panel:
                return await interaction.followup.send("❌ Panel ou options introuvables.")
            before = len(panel["options"])
            panel["options"] = [o for o in panel["options"] if o.get("label") != label]
            save_panels(PANELS)
            if len(CONFIG.get("options", [])) < before:
                await interaction.followup.send(f"✅ Option '{label}' supprimée.")
            else:
                await interaction.followup.send("⚠️ Option non trouvée.")
        elif choice == "3":
            await interaction.followup.send("Mentionnez l'ID du panel puis le nom de l'option à modifier.")
            try:
                msg2 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            parts = msg2.content.split(None, 1)
            if len(parts) < 2:
                return await interaction.followup.send("Format invalide.")
            pid, label = parts[0], parts[1]
            panel = PANELS.get(pid)
            if not panel or "options" not in panel:
                return await interaction.followup.send("❌ Panel ou options introuvables.")
            opt = next((o for o in panel["options"] if o.get("label") == label), None)
            if not opt:
                return await interaction.followup.send("⚠️ Option non trouvée.")
            # manage fields of this option similar to panel fields
            await interaction.followup.send("Gestion des champs : 1️⃣ ajouter 2️⃣ supprimer\nRépondez 1 ou 2 (`cancel` pour quitter)")
            try:
                msg3 = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏱️ Temps écoulé.")
            if msg3.content.lower() == "cancel":
                return await interaction.followup.send("❌ Annulé.")
            sub = msg3.content.strip()
            if sub == "1":
                await interaction.followup.send("Entrez le label du champ, puis `short` ou `paragraph` séparés par |.")
                try:
                    msg4 = await self.bot.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                    return await interaction.followup.send("⏱️ Temps écoulé.")
                parts2 = msg4.content.split("|",1)
                if len(parts2)<2:
                    return await interaction.followup.send("Format invalide.")
                lbl, style = parts2[0].strip(), parts2[1].strip()
                if style not in ("short","paragraph"):
                    return await interaction.followup.send("Style invalide.")
                opt.setdefault("fields",[]).append({"label":lbl,"style":style})
                save_panels(PANELS)
                await interaction.followup.send(f"✅ Champ '{lbl}' ajouté à l'option.")
            elif sub == "2":
                await interaction.followup.send("Indiquez le label du champ à supprimer.")
                try:
                    msg4 = await self.bot.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                    return await interaction.followup.send("⏱️ Temps écoulé.")
                lbl = msg4.content.strip()
                before = len(opt.get("fields",[]))
                opt["fields"] = [f for f in opt.get("fields",[]) if f.get("label")!=lbl]
                save_panels(PANELS)
                if len(opt.get("fields",[]))<before:
                    await interaction.followup.send(f"✅ Champ '{lbl}' supprimé.")
                else:
                    await interaction.followup.send("⚠️ Champ non trouvé.")
            else:
                await interaction.followup.send("Choix invalide.")
        else:
            await interaction.followup.send("Choix invalide.")

    @ui.button(label="Assistant complet", style=nextcord.ButtonStyle.success, custom_id="cfg_wizard")
    async def button_wizard(self, button: ui.Button, interaction: nextcord.Interaction):
        await ctx.send(
            "Tapez `+ticket setup wizard` pour lancer l'assistant pas-à-pas.",
            
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
    # Commande principale de ticket (désactivée - utilisation via panels)
    # ---------------------------
    @commands.group(name="ticket", invoke_without_command=True)
    async def ticket(self, ctx):
        """⚠️ Utilisez les boutons dans le panel de tickets pour créer un ticket"""
        await ctx.send("🎫 Pour créer un ticket, utilisez les boutons dans le panel de tickets !\nSi vous êtes admin, utilisez `+ticket setup panel_add` pour créer un panel.")

    # ---------------------------
    # Commandes de configuration
    # ---------------------------
    @commands.group(name="setup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx):
        """Afficher ou modifier la configuration des tickets via un panneau interactif."""
        embed = nextcord.Embed(
            title="📋 Configuration des tickets",
            color=0x3498db,
            description=(
                f"Catégorie actuelle : <#{CONFIG.get('category')}>\n"
                f"Salon de logs : <#{CONFIG.get('log_channel')}>\n"
                f"Rôles gestionnaires : {', '.join(f'<@&{r}>' for r in CONFIG.get('manager_roles', [])) or 'aucun'}\n"
                f"Rôles suppression : {', '.join(f'<@&{r}>' for r in CONFIG.get('deletor_roles', [])) or 'aucun'}\n"
                f"Rôles accès : {', '.join(f'<@&{r}>' for r in CONFIG.get('access_roles', [])) or 'tout le monde'}\n"
                f"Message avant ticket : {CONFIG.get('pre_ticket_message', 'Non configuré')}\n"
                f"Message d'ouverture : {CONFIG.get('ticket_open_message', 'Non configuré')}\n"
                f"Catégories configurées : {len(CONFIG.get('categories', {}))}"
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

    @ticket_setup.command(name="categories")
    @commands.has_permissions(administrator=True)
    async def setup_categories(self, ctx, action: str = None, *, name: str = None):
        """Gérer les catégories de tickets.
        
        Usage : 
        +ticket setup categories list - Lister les catégories
        +ticket setup categories add "Nom de la catégorie" - Ajouter une catégorie
        +ticket setup categories remove "Nom de la catégorie" - Supprimer une catégorie
        """
        if not action:
            # Afficher le menu interactif pour gérer les catégories
            embed = nextcord.Embed(
                title="📂 Gestion des Catégories",
                description="Choisissez une action pour gérer les catégories de tickets.",
                color=0x3498db
            )
            
            categories = CONFIG.get("categories", {})
            if categories:
                for cat_key, cat_data in categories.items():
                    embed.add_field(
                        name=f"{cat_data.get('emoji', '🎫')} {cat_data.get('name', cat_key.title())}",
                        value=f"ID: `{cat_key}`\n{cat_data.get('description', 'Aucune description')}\n{len(cat_data.get('questions', []))} question(s)",
                        inline=False
                    )
            else:
                embed.description += "\n\n⚠️ Aucune catégorie configurée."
            
            view = CategoryManagementView(self.bot)
            await ctx.send(embed=embed, view=view)
            return
        
        action = action.lower()
        
        if action == "list":
            categories = CONFIG.get("categories", {})
            if not categories:
                return await ctx.send("❌ Aucune catégorie configurée.")
            
            embed = nextcord.Embed(title="📂 Catégories de Tickets", color=0x3498db)
            for cat_key, cat_data in categories.items():
                embed.add_field(
                    name=f"{cat_data.get('emoji', '🎫')} {cat_data.get('name', cat_key.title())}",
                    value=f"**ID**: `{cat_key}`\n**Description**: {cat_data.get('description', 'Aucune')}\n**Questions**: {len(cat_data.get('questions', []))}",
                    inline=False
                )
            await ctx.send(embed=embed)
            
        elif action == "add" and name:
            # Lancer le modal pour ajouter une catégorie
            modal = CategoryCreationModal(name)
            await ctx.send("🛠️ Configuration de la nouvelle catégorie :", view=CategorySetupView(self.bot, name))
            
        else:
            await ctx.send("❌ Usage invalide. Utilisez `+ticket setup categories` pour le menu interactif.")

    @ticket_setup.command(name="message")
    @commands.has_permissions(administrator=True)
    async def setup_message(self, ctx, message_type: str, *, message: str = None):
        """Configurer les messages personnalisés.
        
        Usage :
        +ticket setup message pre "Message avant création"
        +ticket setup message open "Message d'ouverture"
        """
        message_type = message_type.lower()
        
        if message_type not in ["pre", "open", "avant", "ouverture"]:
            return await ctx.send("❌ Type invalide. Utilisez `pre`/`avant` ou `open`/`ouverture`.")        
        if not message:
            return await ctx.send("❌ Vous devez fournir un message.")
        
        if message_type in ["pre", "avant"]:
            CONFIG["pre_ticket_message"] = message
            await ctx.send("✅ Message avant création de ticket mis à jour.")
        else:
            CONFIG["ticket_open_message"] = message
            await ctx.send("✅ Message d'ouverture de ticket mis à jour.")
        
        save_config(CONFIG)

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
    async def panel_add(self, ctx, channel: nextcord.TextChannel, *, title: str = "🎫 Création de Ticket"):
        """
        Créer un panel de tickets avec les catégories configurées.
        
        Usage: +ticket setup panel_add #salon "Titre du panel"
        """
        # Vérifier qu'il y a des catégories configurées
        categories = CONFIG.get("categories", {})
        if not categories:
            return await ctx.send("❌ Aucune catégorie configurée ! Utilisez `+ticket setup categories` d'abord.")
        
        # Créer l'embed pour le panel
        embed = nextcord.Embed(
            title=title,
            description=CONFIG.get("pre_ticket_message", "🎫 Choisissez une catégorie pour votre ticket :"),
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        # Ajouter les informations sur chaque catégorie
        for cat_key, cat_data in categories.items():
            embed.add_field(
                name=f"{cat_data.get('emoji', '🎫')} {cat_data.get('name', cat_key.title())}",
                value=cat_data.get('description', 'Aucune description'),
                inline=True
            )
        
        # Créer le panel
        pid = str(int(datetime.utcnow().timestamp() * 1000))
        panel = {
            "channel_id": channel.id,
            "message_id": None,
            "title": title,
            "description": CONFIG.get("pre_ticket_message", "🎫 Choisissez une catégorie pour votre ticket :"),
            "allowed_roles": []
        }
        PANELS[pid] = panel
        save_panels(PANELS)
        
        # Créer la vue avec les boutons de catégories
        view = CategoryPanelView(self.bot, pid)
        sent = await channel.send(embed=embed, view=view)
        panel["message_id"] = sent.id
        save_panels(PANELS)
        
        await ctx.send(f"✅ Panel créé dans {channel.mention} !\nLes membres peuvent maintenant cliquer sur les boutons pour créer des tickets.")

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


    # ----------------------------------
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
    # ------------------------------
    async def _open_ticket(self, ctx):
        category_id = CONFIG.get("category")
        if category_id is None:
            # fallback vers la première catégorie définie dans un panel
            for p in PANELS.values():
                if p.get("category"):
                    category_id = p["category"]
                    break
        if category_id is None:
            return await ctx.send("❌ La catégorie de tickets n'est pas configurée.")
        category = ctx.guild.get_channel(category_id)
        if category is None or not isinstance(category, nextcord.CategoryChannel):
            return await ctx.send("❌ La catégorie configurée est invalide.")

        # incrémenter le compteur
        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"ticket-{CONFIG['counter']}"

        overwrites = {ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
        overwrites[ctx.author] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        for rid in CONFIG.get("manager_roles", []):
            role = ctx.guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)

        chan = await ctx.guild.create_text_channel(name, category=category, overwrites=overwrites)
        embed = nextcord.Embed(
            title=panel.get("title", CONFIG.get("embed_title")),
            description=panel.get("description", CONFIG.get("embed_description")),
            color=0x95A5A6,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']}")
        await chan.send(ctx.author.mention, embed=embed)

        thread_id = await self._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {"thread_id": thread_id, "owner": ctx.author.id}
        save_data(TICKET_DATA)

        await ctx.send(
            f"✅ Ticket créé : {chan.mention}")

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

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Vous devez être administrateur.", ephemeral=True)
            return False
        return True

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


class CategoryPanelView(ui.View):
    """Vue pour les panels de tickets avec boutons de catégories"""
    def __init__(self, bot, panel_id: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.panel_id = panel_id
        
        # Ajouter les boutons pour chaque catégorie
        categories = CONFIG.get("categories", {})
        for cat_key, cat_data in categories.items():
            button = ui.Button(
                label=cat_data.get("name", cat_key.title()),
                emoji=cat_data.get("emoji"),
                style=nextcord.ButtonStyle.primary,
                custom_id=f"panel_category_{cat_key}"
            )
            button.callback = self.create_category_callback(cat_key, cat_data)
            self.add_item(button)

    def create_category_callback(self, category_key: str, category_data: Dict):
        """Créer un callback pour chaque catégorie"""
        async def callback(interaction: nextcord.Interaction):
            # Vérifier les permissions d'accès
            if CONFIG.get("access_roles"):
                if not any(r.id in CONFIG["access_roles"] for r in interaction.user.roles):
                    return await interaction.response.send_message("❌ Vous n'avez pas le rôle requis pour ouvrir un ticket.", ephemeral=True)
            
            # Vérifier si la catégorie a des questions
            if category_data.get("questions"):
                # Ouvrir la modal de questionnaire
                modal = TicketQuestionnaire(category_key, category_data, self.bot)
                await interaction.response.send_modal(modal)
            else:
                # Créer directement le ticket
                await self._create_simple_ticket(interaction, category_key, category_data)
        return callback

    async def _create_simple_ticket(self, interaction: nextcord.Interaction, category_key: str, category_data: Dict):
        """Créer un ticket simple sans questionnaire"""
        guild = interaction.guild
        discord_category = guild.get_channel(CONFIG.get("category"))
        
        if not discord_category:
            return await interaction.response.send_message("❌ La catégorie de tickets n'est pas configurée.", ephemeral=True)
        
        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"{category_data.get('emoji', '🎫')}-ticket-{CONFIG['counter']}"
        
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        for rid in CONFIG.get("manager_roles", []):
            role = guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        chan = await guild.create_text_channel(name, category=discord_category, overwrites=overwrites)
        
        embed = nextcord.Embed(
            title=f"{category_data.get('emoji', '🎫')} {category_data.get('name', 'Ticket')}",
            description=CONFIG.get("ticket_open_message", "✅ Votre ticket a été créé !"),
            color=category_data.get("color", 0x3498db),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']} • Créé par {interaction.user}")
        embed.add_field(name="👤 Utilisateur", value=interaction.user.mention, inline=True)
        embed.add_field(name="📂 Catégorie", value=category_data.get("name", "Inconnue"), inline=True)
        
        await chan.send(f"{interaction.user.mention}", embed=embed)
        
        view = TicketActionView(self.bot)
        await chan.send("🛠️ **Actions du ticket** :", view=view)
        
        thread_id = await self.bot.get_cog("Tickets")._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {
            "thread_id": thread_id, 
            "owner": interaction.user.id,
            "category": category_key
        }
        save_data(TICKET_DATA)
        
        await interaction.response.send_message(f"✅ Ticket créé : {chan.mention}", ephemeral=True)


class TicketActionView(ui.View):
    """Vue pour les actions dans un ticket (claim, close, delete)"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        
        self.add_item(ui.Button(
            label="✋ Réclamer", 
            style=nextcord.ButtonStyle.primary,
            custom_id="ticket_claim"
        ))
        
        self.add_item(ui.Button(
            label="🔒 Fermer", 
            style=nextcord.ButtonStyle.secondary,
            custom_id="ticket_close"
        ))
        
        self.add_item(ui.Button(
            label="🗑️ Supprimer", 
            style=nextcord.ButtonStyle.danger,
            custom_id="ticket_delete"
        ))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        # Vérifier si on est dans un ticket
        if str(interaction.channel.id) not in TICKET_DATA:
            await interaction.response.send_message("❌ Cette commande ne fonctionne que dans un ticket.", ephemeral=True)
            return False
        return True

    @ui.button(label="✋ Réclamer", style=nextcord.ButtonStyle.primary, custom_id="ticket_claim")
    async def claim_ticket(self, button: ui.Button, interaction: nextcord.Interaction):
        if not any(r.id in CONFIG.get("manager_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Vous n'avez pas la permission de réclamer.", ephemeral=True)
        
        await interaction.channel.set_topic(f"Claimed by {interaction.user}")
        await interaction.response.send_message(f"✋ Ticket pris par {interaction.user.mention}.")
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id, "✋ Ticket réclamé", f"Réclamé par {interaction.user}")

    @ui.button(label="🔒 Fermer", style=nextcord.ButtonStyle.secondary, custom_id="ticket_close")
    async def close_ticket(self, button: ui.Button, interaction: nextcord.Interaction):
        cid = str(interaction.channel.id)
        ticket_data = TICKET_DATA.get(cid, {})
        owner = ticket_data.get("owner")
        
        if interaction.user.id != owner and not any(r.id in CONFIG.get("manager_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Vous ne pouvez pas fermer ce ticket.", ephemeral=True)
        
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id, "✅ Ticket fermé", f"Fermé par {interaction.user}")
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 Ticket fermé. Le canal restera ouvert.")

    @ui.button(label="🗑️ Supprimer", style=nextcord.ButtonStyle.danger, custom_id="ticket_delete")
    async def delete_ticket(self, button: ui.Button, interaction: nextcord.Interaction):
        if not any(r.id in CONFIG.get("deletor_roles", []) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Vous n'avez pas la permission de supprimer ce ticket.", ephemeral=True)
        
        await self.bot.get_cog("Tickets")._log_event(interaction.channel.id, "🗑️ Ticket supprimé", f"Supprimé par {interaction.user}")
        await interaction.channel.delete(reason=f"Ticket supprimé par {interaction.user}")
        TICKET_DATA.pop(str(interaction.channel.id), None)
        save_data(TICKET_DATA)


def setup(bot):
    bot.add_cog(Tickets(bot))


class TicketPanelView(ui.View):
    def __init__(self, bot, panel_id: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.panel_id = panel_id

    @ui.button(label="Ouvrir un ticket", style=nextcord.ButtonStyle.primary,
               custom_id="ticket_open_button")
    async def open_button(self, button: ui.Button,
                          interaction: nextcord.Interaction):
        panel = PANELS.get(self.panel_id)
        if not panel:
            return await ctx.send(
                "❌ Panel introuvable.")

        allowed = CONFIG.get("allowed_roles", [])
        if allowed and not any(r.id in allowed for r in ctx.author.roles):
            return await ctx.send(
                "❌ Vous n'avez pas la permission d'ouvrir ce ticket.",
                )

        warn = CONFIG.get("warning")
        if warn:
            await ctx.send(
                embed=nextcord.Embed(description=warn, color=0xFFA500),
                )
            await asyncio.sleep(0.5)

        guild = ctx.guild
        category = guild.get_channel(CONFIG.get("category"))
        if category is None:
            return await ctx.send(
                "❌ Catégorie du panel invalide.")

        CONFIG["counter"] = CONFIG.get("counter", 0) + 1
        save_config(CONFIG)
        name = f"ticket-{CONFIG['counter']}"

        overwrites = {ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
        overwrites[ctx.author] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        for rid in CONFIG.get("manager_roles", []):
            role = ctx.guild.get_role(rid)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(read_messages=True, send_messages=True)

        chan = await ctx.guild.create_text_channel(name, category=category, overwrites=overwrites)
        embed = nextcord.Embed(
            title=panel.get("title", CONFIG.get("embed_title")),
            description=panel.get("description", CONFIG.get("embed_description")),
            color=0x95A5A6,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket #{CONFIG['counter']}")
        await chan.send(ctx.author.mention, embed=embed)

        thread_id = await self._create_log_thread(chan)
        TICKET_DATA[str(chan.id)] = {"thread_id": thread_id, "owner": ctx.author.id}
        save_data(TICKET_DATA)

        await ctx.send(
            f"✅ Ticket créé : {chan.mention}")
