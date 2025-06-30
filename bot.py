import discord
import aiohttp
import json
from discord.ext import tasks
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
GUILD_ID= """""""Seu id""""""" #Guild_ID
FIVEM_URL = "http://nobre.santagroup.gg:30120/info.json"

async def get_fivem_name():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://nobre.santagroup.gg:30120/info.json") as response:
                if response.status == 200:
                    raw = await response.text()
                    data = json.loads(raw)
                    return data.get("vars", {}).get("sv_projectName", "Nome não encontrado")
                else:
                    print(f"Erro: status {response.status}")
                    return "Servidor Offline"
    except Exception as e:
        print(f"Erro ao obter nome FiveM: {e}")
        return "Servidor Offline"

def is_admin(interaction: discord.Interaction):
    cargo_restrito = discord.utils.get(interaction.guild.roles, name="Admin")
    return cargo_restrito in interaction.user.roles if cargo_restrito else False

@tasks.loop(minutes=5)
async def atualizar_status():
    try:
        nome = await get_fivem_name()
        await bot.change_presence(activity=discord.Game(name=nome))
        print(f"🔁 Status atualizado para: {nome}")
    except Exception as e:
        print(f"❌ Erro ao atualizar status: {e}")

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} está online!')
    atualizar_status.start()
    try:
        nome = await get_fivem_name()
    except Exception as e:
        print(f"⚠️ Erro ao obter nome FiveM: {e}")
        nome = "Servidor Offline"  # fallback seguro
    try:
        await bot.change_presence(activity=discord.Game(name=f"{nome}"))
        print(f"✅ Online — status definido para: {nome}")      
        guild = discord.Object(id="""""""""""Seu Id""""""""""""")  # ID do seu servidor para sincronização local
        synced = await bot.tree.sync(guild=guild)
        print(f"🔧 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")
        nome = await get_fivem_name()

@bot.tree.command(name="dm", description="Envia uma mensagem privada para todos que possuem o cargo mencionado.")
@app_commands.describe(
    cargo="Cargo que deve receber a mensagem",
    mensagem="Mensagem a ser enviada"
)
async def dm(interaction: discord.Interaction, cargo: discord.Role, mensagem: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    membros = [m for m in interaction.guild.members if cargo in m.roles and not m.bot]

    if not membros:
        await interaction.response.send_message(f"Nenhum membro encontrado com o cargo {cargo.mention}.", ephemeral=True)
        return

    await interaction.response.send_message(f"📨 Enviando mensagem para {len(membros)} membros com o cargo {cargo.mention}...", ephemeral=True)

    enviados, erros = 0, 0
    for membro in membros:
        try:
            await membro.send(mensagem)
            enviados += 1
        except Exception as e:
            print(f"Erro ao enviar DM para {membro}: {e}")
            erros += 1

    await interaction.followup.send(f"✅ Mensagem enviada para {enviados} membros. ❌ Falhou em {erros} casos.")

@bot.tree.command(name="cobranca", description="Envia mensagem de cobrança para cargo.")
@app_commands.describe(
    cargo="Cargo que deve receber a mensagem"
)
async def cobranca(interaction: discord.Interaction, cargo: discord.Role):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    membros = [m for m in interaction.guild.members if cargo in m.roles and not m.bot]
    if not membros:
        await interaction.response.send_message(f"Nenhum membro com o cargo {cargo.mention} encontrado.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🛠️ Aviso de Repasse Semanal da Mecânica",
        description=(
            "**Mecânicos**, hoje é dia de **realizar o pagamento semanal** no valor de **💸3kk**!!!\n\n"
            "Os **mecânicos** que não **realizarem o pagamento** serão **advertidos** ou até mesmo **removidos da mecânica** ⚠️\n\n"
            "**Grato** pelos membros que já **realizaram** ou estão **adiantados no pagamento**.\n\n"
            "@here @everyone @mecanicos\n\n"
            "📌 **instruções para o pagamento:**\n"
            "💣 Aperte **esc** no jogo e abra o **painel da organização**\n"
            "💣 Clique na opção **banco** no painel\n"
            "💣 Realize o **depósito de 3kk** no banco da organização\n"
            "💣 **Tire print da tela** confirmando o depósito\n"
            "💣 Envie o print no canal 💲・**deposito-semanal-aberto** da mecanica"
        ),
        color=cargo.color if cargo.color.value != 0 else discord.Color.purple()
    )
    file = discord.File("banner.png", filename="banner.png")
    embed.set_image(url="attachment://banner.png")

    await interaction.response.send_message(f"📨 Enviando cobrança para {len(membros)} membros com o cargo {cargo.mention}...", ephemeral=True)

    enviados, erros = 0, 0
    for membro in membros:
        try:
            await membro.send(embed=embed, file=file)
            enviados += 1
        except Exception as e:
            print(f"Erro ao enviar DM para {membro}: {e}")
            erros += 1

    await interaction.followup.send(f"✅ Mensagem de cobrança enviada para {enviados} membros. ❌ Falhou em {erros} casos.")

@bot.tree.command(name="reuniao", description="Envia mensagem de reunião para cargo, com dia e hora customizados.")
@app_commands.describe(
    cargo="Cargo que deve receber a mensagem",
    dia="Dia da reunião (ex: segunda-feira)",
    hora="Hora da reunião (ex: 18:30)"
)
async def reuniao(interaction: discord.Interaction, cargo: discord.Role, dia: str, hora: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    membros = [m for m in interaction.guild.members if cargo in m.roles and not m.bot]
    if not membros:
        await interaction.response.send_message(f"Nenhum membro com o cargo {cargo.mention} encontrado.", ephemeral=True)
        return

    descricao = (
    f"📢 **AVISO DE REUNIÃO DA GESTÃO**\n\n"
    f"🔔 **ATENÇÃO, 🔹@Dono(a) 🔹@Lider 🔹@Chefe 🔹@Gerente Geral 🔹@Gerente 🔹@Recrutador**\n\n"
    f"📅 **Data:** {dia.capitalize()}\n"
    f"⏰ **Horário:** {hora}\n"
    f"📌 **Local:** Canal de voz <#1370633913889849454>\n\n"
    f"💬 Pauta: **Alinhamento de atividades, recrutamentos, comunicados entre outros**\n\n"
    f"✅ **Sua presença é indispensável!**\n\n"
    f"⚠️ **Ausência sem justificativa poderá resultar em advertência e rebaixamento.**"
)

    embed = discord.Embed(
        description=descricao,
        color=cargo.color if cargo.color.value != 0 else discord.Color.blue()
    )
    file = discord.File("banner.png", filename="banner.png")
    embed.set_image(url="attachment://banner.png")

    await interaction.response.send_message(f"📨 Enviando mensagem de reunião para {len(membros)} membros com o cargo {cargo.mention}...", ephemeral=True)

    enviados, erros = 0, 0
    for membro in membros:
        try:
            await membro.send(embed=embed, file=file)
            enviados += 1
        except Exception as e:
            print(f"Erro ao enviar DM para {membro}: {e}")
            erros += 1

    await interaction.followup.send(f"✅ Mensagem de reunião enviada para {enviados} membros. ❌ Falhou em {erros} casos.")

@bot.tree.command(name="rei", description="Envia mensagem do evento REI DO CRIME 2.0 para o cargo.")
@app_commands.describe(
    cargo="Cargo que deve receber a mensagem"
)
async def rei(interaction: discord.Interaction, cargo: discord.Role):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    membros = [m for m in interaction.guild.members if cargo in m.roles and not m.bot]
    if not membros:
        await interaction.response.send_message(f"Nenhum membro com o cargo {cargo.mention} encontrado.", ephemeral=True)
        return

    descricao = (
    "👑 **REI DO CRIME 2.0** 👑\n"
    "➡️ Prepare-se para o REI DO CRIME 2.0 na CIDADE NOBRE! Um evento épico para decidir o líder supremo das facções.\n\n"
    "📢 **REGRAS:**\n"
    "• Todos os veículos são permitidos, mas BATE-BATE e Aliança de Facs são proibidos.\n"
    "• Os jogadores serão levados a um mundo exclusivo para o evento.\n"
    "• Quando a zona segura diminuir, DV será aplicado, levando a um confronto final.\n\n"
    "📅 **HOJE:**\n"
    "Conquiste seu lugar como o verdadeiro REI DO CRIME! Não perca a chance de fazer história e levar sua facção à glória!\n\n"
    "@everyone @here\n\n"
    "📌 **Instruções:**\n"
    "💣 Alinhamento no Terceiro Andar da mecanica\n"
    "💣 Não perde nada ao morrer\n"
    "💣 Vamos fornecer todo o armamento necessário\n"
    "💣 Valendo 1kk por KILL (enviar clip em 💬・chat-elite )\n"
    "💣 1kk só por participar\n\n"
    "**Critérios para ganhar:**\n"
    "• Último QG vivo dentro da Zona Azul\n"
    "• Proibido o abuso de bandagem\n"
    "• Só será permitido ficar fora da Zona Azul por 5 segundos, caso contrário será eliminado do evento\n\n"
    "Quem será que leva hoje no REI DO CRIME? 👀\n"
    "👑 **REI DO CRIME 2.0** 👑\n"
    "➡️ no dia a equipe de entretenimento vai passar nas facções explicando o REI DO CRIME 2.0\n"
    "➡️ Os líderes terão até 20:20 para alinhar contingência máxima dentro do QG no mundo padrão\n\n"
    "⬇️ Não poderá ser puxado membros depois de mudarmos de mundo\n"
    "➡️ O REI DO CRIME 2.0 VAI COMEÇAR ÀS 21H00"
)

    embed = discord.Embed(
        title="REI DO CRIME 2.0 | Mecanica Overspeed 🛠",
        description=descricao,
        color=cargo.color if cargo.color.value != 0 else discord.Color.gold()
    )
    file = discord.File("rei.png", filename="rei.png")
    embed.set_image(url="attachment://rei.png")

    await interaction.response.send_message(f"📨 Enviando mensagem REI DO CRIME 2.0 para {len(membros)} membros com o cargo {cargo.mention}...", ephemeral=True)

    enviados, erros = 0, 0
    for membro in membros:
        try:
            await membro.send(embed=embed, file=file)
            enviados += 1
        except Exception as e:
            print(f"Erro ao enviar DM para {membro}: {e}")
            erros += 1

    await interaction.followup.send(f"✅ Mensagem REI DO CRIME 2.0 enviada para {enviados} membros. ❌ Falhou em {erros} casos.")

@bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis do bot.")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📬 Comandos do Bot",
        description="Aqui estão os comandos disponíveis e como usá-los:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="/dm cargo mensagem",
        value="📤Envia uma mensagem privada para todos que possuem o cargo mencionado.",
        inline=False
    )
    embed.add_field(
        name="/cobranca cargo",
        value="💸Envia mensagem de cobrança para o cargo.",
        inline=False
    )
    embed.add_field(
        name="/reuniao cargo dia hora",
        value="⏰Envia mensagem de reunião para o cargo com dia e hora especificados.",
        inline=False
    )
    embed.add_field(
        name="/rei cargo",
        value="👑Envia mensagem do evento REI DO CRIME 2.0 para o cargo.",
        inline=False
    )
    embed.add_field(
        name="/limparcache",
        value="🔃Limpa e ressincroniza os comandos do bot",
        inline=False
    )
    embed.add_field(
        name="/ajuda",
        value="📜Mostra esta mensagem de ajuda.",
        inline=False
    )
    embed.add_field(
        name="/termos",
        value="📜Mostra o Termo de Serviço do bot.",
        inline=False
    )
    embed.add_field(
        name="/clausulas",
        value="⛔Mostra a lista das cláusulas de advertências.",
        inline=False
    )
    
    embed.set_footer(text="</> Desenvolvido por Guilherme#191344")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="limparcache", description="Limpa e ressincroniza os comandos do bot.")
async def limparcache(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return

    guild = interaction.guild
    try:
        await interaction.response.send_message("🧹 Limpando cache e ressincronizando comandos localmente...", ephemeral=True)
        bot.tree.clear_commands(guild=guild)  # Removi o await daqui
        await bot.tree.sync(guild=guild)
        await interaction.followup.send("✅ Cache limpo e comandos ressincronizados localmente com sucesso!", ephemeral=True)
    except Exception as e:
        print(f"Erro ao limpar comandos: {e}")
        await interaction.followup.send("❌ Ocorreu um erro ao tentar limpar e ressincronizar os comandos.", ephemeral=True)

@bot.command(name="termos")
async def termos_command(ctx):
    embed = discord.Embed(
        title="📜 Termo de Serviço do Bot",
        description="Ao utilizar este bot no Discord, você concorda com os termos abaixo. Caso não concorde, não utilize os serviços oferecidos por este bot.",
        color=discord.Color.dark_gold()
    )
    embed.add_field(
        name="✅ Uso do Bot",
        value=(
            "• O bot destina-se exclusivamente para uso dentro do servidor da mecanica em que foi autorizado.\n"
            "• O bot fornece funcionalidades como envio de mensagens privadas, avisos, cobranças e organização de eventos conforme configurado pelos administradores do servidor."
        ),
        inline=False
    )
    embed.add_field(
        name="🚫 Restrições",
        value=(
            "• É proibido utilizar o bot para atividades ilegais, assédio, spam ou qualquer ação que viole as [Diretrizes da Comunidade do Discord](https://discord.com/guidelines).\n"
            "• Apenas usuários com permissões adequadas (ex.: cargo 'Admin') podem executar comandos restritos do bot."
        ),
        inline=False
    )
    embed.add_field(
        name="⚠️ Limitação de Responsabilidade",
        value=(
            "• O criador do bot não se responsabiliza por qualquer dano direto, indireto ou consequente do uso do bot, "
            "incluindo exclusão de mensagens, envio incorreto de informações ou uso indevido por parte dos membros do servidor."
        ),
        inline=False
    )
    embed.add_field(
        name="🔒 Privacidade",
        value=(
            "• O bot apenas processa dados necessários para o funcionamento dos comandos, como IDs de usuário, nomes de usuário e cargos.\n"
            "• Nenhum dado pessoal é armazenado permanentemente fora do Discord ou compartilhado com terceiros."
        ),
        inline=False
    )
    embed.add_field(
        name="📌 Alterações no Termo",
        value="• Este termo poderá ser alterado a qualquer momento.",
        inline=False
    )
    embed.add_field(
        name="🛠 Suporte",
        value="• Para dúvidas ou problemas relacionados ao bot, entre em contato com o administrador do servidor ou o criador do bot.",
        inline=False
    )
    embed.set_footer(text="</> Desenvolvido por Guilherme#191344")
    await ctx.send(embed=embed)

@bot.command(name="clausulas")
async def clausulas_command(ctx):
    embed = discord.Embed(
        title="⛔ Clausulas de advertencias",
        description="Ao utilizar este bot no Discord, você concorda com os termos abaixo. Caso não concorde, não utilize os serviços oferecidos por este bot.",
        color=discord.Color.dark_gold()
    )
    embed.add_field(
        name="OBS. 01",
        value=(
	"**Conduta legal**:  Mecânica é um serviço legal com isso qualquer ação envolvendo roubo, assaltos e tudo mais relacionado a isso você será demitido(a) automaticamente e você receberá @Blacklist\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 02",
        value=(
        "**Acumulo de advertências**: Se acumular 3 ADV, será automaticamente demitido da mecânica e vai entrar na @Blacklist\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 03",
        value=(
	"**Funções**: Qualquer cargo que estiver fazendo funções que não é para o seu cargo vai ser advertido; \n"
        "`Consequência: Multa 500k e Advertência`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 04",
        value=(
	"Preços da mecânica**:  Não manipule os preços da mecânica. Qualquer violação resultará em multa e demissão; `Consequência: Multa 2kk, Demissão`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 05",
        value=(
	"**Venda de itens**: Venda de itens da mecânica é somente permitido pelos gerentes; \n"
        "`Consequência: 1 Advertência`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 06",
        value=(
	"**Repasse semanal**:  Mecânicos(as) tem obrigatoriedade de realizar deposito semanal TODA SEXTA-FEIRA NO VALOR DE 3kk (3 milhões). Informações disponíveis em <⁠💲・deposito-semanal-aberto> ; \n"
        "`Consequência: Multa Valor do deposito semanal + 20% desse valor e Advertência`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 07",
        value=(
	"**Uso Obrigatório do Microfone no Baixo**: Todos os membros da Mecânica Over Speed devem exercer suas funções exclusivamente com o microfone no volume baixo\n"
        "`Consequência: Multa 500k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 08",
        value=(
	"**Uso do uniforme e veiculo obrigatório**: Use o uniforme completo da mecânica enquanto estiver trabalhando e não use seu carro pessoal para trabalhar na mecânica. Lembre-se: atendimentos de chamados sempre com o veículo da mecânica;"
	    "`Consequência: Multa 600k e 1 Advertência`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 09",
        value=(
	"**Uso do uniforme e veiculo fora de serviço**: É proibido a utilização do uniforme e veiculo da mecânica fora de serviço; \n"
        "`Consequência: 1 Advertência`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 10",
        value=(
	"**Trabalho e conduta nas baias**: Não fique na frente da mecânica tentando pegar clientes, escolha uma baia e fique nela os esperando além disso é proibido ficar assoviando, gritando, realizando animações ou chamar cliente na baia;"
	    "`Consequência: Multa 500k e 1 Advertência `\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 11",
        value=(
	"**Drifting e musica na mecânica** : É proibido a realização de drifting e colocar musica dentro da mecânica por parte de vocês;\n"
        "`Consequência: Multa 500k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 12",
        value=(
	"**Conflitos internos**:  Em caso de conflitos entre mecânicos ou clientes na mecânica, chame um superior na rádio para resolver a situação;\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 13",
        value=(
	"**Obrigatoriedade na rádio**: Fique na rádio 120 enquanto estiver trabalhando; \n"
        "`Consequência: Multa 200k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 14",
        value=(
	"** Call de serviço**: Proibido ficar em call de serviço caso não esteja em serviço;\n"
        "`Consequência: Multa 200k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 15",
        value=(
	"**Farmando horas**: Caso você fique burlando o sistema e farmando horas;"
	"`Consequência: Ponto Cancelado e Multa 500k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 16",
        value=(
	"**AFK com fardamento**: Está proibido ficar afk em baia com roupa de mecânico;"
	"`Consequência: Multa 1kk`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 17",
        value=(
	"**Tunagem fora de serviço**: Está proibido a tunagem de veiculo se você não estiver em serviço;"
	"`Consequência: Multa 500k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 18",
        value=(
	"**Comunicação de ausência**:  Se você ficar ausente por mais de 5 dias avise no canal de <🤒・afastamento> ou estará sujeito a demissão\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 19",
        value=(
	"**Itens do Baú**: É permitido pegar somente 5 itens dentro do nosso baú por vez dentre (Bandagens, Analgésico, Radio, Energético e Celular);\n"
        "`Consequência: Multa 600k` \n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 20",
        value=(
	"**Proibido pular do segundo andar**: Não é permitido pular do segundo andar , sempre desça pela rampa;\n"
        "`Consequência: Multa 500k`\n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 21",
        value=(
	"**Uso Obrigatório da calculador**: Sempre usar a calculadora durante o serviço de mecânico;\n"
        "Calculadora Da Mecânica: https://calculadoramecanica.netlify.app/ \n"
        ),
        inline=False
    )
    embed.add_field(
        name="OBS. 22",
        value=(
	"**Vigência demissão. ** Qualquer pessoa que pedir PD (pedido de demissão) da mecânica com menos de 5 dias de contratado tera que pagar uma multa de 5kk ou entrara na <@Blacklist>."
        ),
        inline=False
    )

    embed.set_footer(text="</> Desenvolvido por Guilherme#191344")
    await ctx.send(embed=embed)

# 🚀 Iniciar o bot
bot.run('Token id')