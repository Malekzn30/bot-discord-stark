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

    @ticket.group(name="setup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ticket_setup(self, ctx):
        """sous‑commandes : category, logs, title, description"""
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
        await ctx.send(embed=embed)

    @ticket_setup.command(name="category")
    @commands.has_permissions(administrator=True)
    async def setup_category(self, ctx, category: nextcord.CategoryChannel):
        CONFIG["category"] = category.id
        save_config(CONFIG)
        await ctx.send(f"✅ Catégorie de tickets définie sur {category.mention}.")

    @ticket_setup.command(name="logs")
    @commands.has_permissions(administrator=True)
    async def setup_logs(self, ctx, channel: nextcord.TextChannel):
        CONFIG["log_channel"] = channel.id
        save_config(CONFIG)
        await ctx.send(f"✅ Salon de logs défini sur {channel.mention}.")

    @ticket_setup.command(name="title")
    @commands.has_permissions(administrator=True)
    async def setup_title(self, ctx, *, title: str):
        CONFIG["embed_title"] = title
        save_config(CONFIG)
        await ctx.send("✅ Titre de l'embed modifié.")

    @ticket_setup.command(name="description")
    @commands.has_permissions(administrator=True)
    async def setup_description(self, ctx, *, desc: str):
        CONFIG["embed_description"] = desc
        save_config(CONFIG)
        await ctx.send("✅ Description de l'embed modifiée.")

    @ticket_setup.command(name="addmanager")
    @commands.has_permissions(administrator=True)
    async def add_manager(self, ctx, role: nextcord.Role):
        if role.id in CONFIG["manager_roles"]:
            return await ctx.send("✅ Ce rôle est déjà gestionnaire.")
        CONFIG["manager_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant voir/fermer/claim des tickets.")

    @ticket_setup.command(name="removemanager")
    @commands.has_permissions(administrator=True)
    async def remove_manager(self, ctx, role: nextcord.Role):
        if role.id not in CONFIG["manager_roles"]:
            return await ctx.send("❌ Ce rôle n'est pas gestionnaire.")
        CONFIG["manager_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} n'est plus gestionnaire.")

    @ticket_setup.command(name="adddeletor")
    @commands.has_permissions(administrator=True)
    async def add_deletor(self, ctx, role: nextcord.Role):
        if role.id in CONFIG["deletor_roles"]:
            return await ctx.send("✅ Ce rôle peut déjà supprimer des tickets.")
        CONFIG["deletor_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant supprimer des tickets.")

    @ticket_setup.command(name="removedeletor")
    @commands.has_permissions(administrator=True)
    async def remove_deletor(self, ctx, role: nextcord.Role):
        if role.id not in CONFIG["deletor_roles"]:
            return await ctx.send("❌ Ce rôle ne peut pas supprimer de tickets.")
        CONFIG["deletor_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} ne peut plus supprimer de tickets.")

    @ticket_setup.command(name="access_add")
    @commands.has_permissions(administrator=True)
    async def access_add(self, ctx, role: nextcord.Role):
        if role.id in CONFIG["access_roles"]:
            return await ctx.send("✅ Ce rôle a déjà accès aux tickets.")
        CONFIG["access_roles"].append(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} peut maintenant ouvrir des tickets.")

    @ticket_setup.command(name="panel_add")
    @commands.has_permissions(administrator=True)
    async def panel_add(self, ctx, channel: nextcord.TextChannel, category: nextcord.CategoryChannel, *, title: str = "🎫 Ticket", description: str = "Cliquez pour ouvrir un ticket."):
        """Créer un panel de ticket minimal et l'envoyer dans <channel>."""
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
            desc += f"• {pid} — channel: {ch.mention if ch else p.get('channel_id')} — category: {cat.name if cat else p.get('category')} — title: {p.get('title')}\n"
        await ctx.send(embed=nextcord.Embed(title="Panels", description=desc, color=0x3498db))

    @ticket_setup.command(name="access_remove")
    @commands.has_permissions(administrator=True)
    async def access_remove(self, ctx, role: nextcord.Role):
        if role.id not in CONFIG["access_roles"]:
            return await ctx.send("❌ Ce rôle n'avait pas accès aux tickets.")
        CONFIG["access_roles"].remove(role.id)
        save_config(CONFIG)
        await ctx.send(f"✅ {role.mention} ne peut plus ouvrir de tickets.")

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