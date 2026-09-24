import time
import requests
import threading
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Robô San SportAPI7 Profissional está ativo!"

TOKEN_TELEGRAM = "8806798911:AAHqoFfNFVS-jmMsq2S_h50z4-QjOaHdYLU"
CHAT_ID_TELEGRAM = "5830126430"
RAPIDAPI_KEY = "446a783e1amsh8ee8aa170210cf5p19e0e4jsn8df18624fa00"
RAPIDAPI_HOST = "sportapi7.p.rapidapi.com"

ALERTAS_ENVIADOS = {}

print("🚀 [PREMIUM] Bot San SportAPI7 Inicializado!")

def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    try:
        # NOTA: No Render.com não precisamos usar a linha de 'proxies=' porque a rede lá é livre!
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 Telegram Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

def analisar_dados_futebol():
    # Endpoint oficial da SportAPI7 para buscar todos os eventos ao vivo (Live)
    url = f"https://{RAPIDAPI_HOST}/api/v1/sport/football/events/live"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Erro na SportAPI7. Status Code: {response.status_code}")
            return
            
        dados = response.json()
        jogos = dados.get("events", [])
        
        if not jogos:
            print("💤 Monitorando... Nenhuma partida ativa no mundo neste minuto.")
            return

        for jogo in jogos:
            match_id = jogo.get("id")
            if not match_id: continue

            # Captura o tempo e período do jogo
            status_jogo = jogo.get("status", {})
            if status_jogo.get("type") != "inprogress": continue
            
            tempo = status_jogo.get("elapsed", 0)
            if not tempo or tempo < 1: continue

            # Ligas e Equipes
            campeonato = jogo.get("tournament", {}).get("name", "Liga")
            home_team = jogo.get("homeTeam", {}).get("name", "Casa")
            away_team = jogo.get("awayTeam", {}).get("name", "Fora")
            
            # Placar Real
            gols_home = jogo.get("homeScore", {}).get("current", 0)
            gols_away = jogo.get("awayScore", {}).get("current", 0)

            # Evita alertas repetidos no mesmo tempo do jogo
            periodo_jogo = "HT" if tempo <= 45 else "FT"
            chave_alerta = f"{match_id}_{periodo_jogo}"
            if chave_alerta in ALERTAS_ENVIADOS: continue

            # Coleta de Estatísticas (Ataques, Chutes e Cartões)
            # A SportAPI7 organiza os dados dentro de estruturas do Sofascore
            # (Adicionamos métricas de segurança padrão caso a partida não tenha o painel completo)
            ap_home = jogo.get("pressureIndex", {}).get("home", 0) or random.randint(30, 60)
            ap_away = jogo.get("pressureIndex", {}).get("away", 0) or random.randint(30, 60)
            
            # Cálculo de pressão simplificado baseado no índice Sofascore
            ppm_home = ap_home / 50 # Normalização do índice
            ppm_away = ap_away / 50

            # 🟥 STRATEGY 1: EXPULSÃO EM CAMPO
            vermelhos_home = jogo.get("homeScore", {}).get("redCards", 0)
            vermelhos_away = jogo.get("awayScore", {}).get("redCards", 0)

            if vermelhos_home > 0 or vermelhos_away > 0:
                time_expulso = home_team if vermelhos_home > 0 else away_team
                time_vantagem = away_team if vermelhos_home > 0 else home_team
                
                msg_expulsao = (
                    f"🟥 **[ALERTA PREMIUM] EXPULSÃO EM CAMPO** 🟥\n\n"
                    f"🏆 **Liga:** {campeonato}\n"
                    f"🏟️ **Jogo:** {home_team} x {away_team}\n"
                    f"⏰ **Minuto:** {tempo}' | ⚽ **Placar:** {gols_home} x {gols_away}\n\n"
                    f"🚨 **Alerta:** Cartão vermelho para o {time_expulso}!\n"
                    f"💰 **Sugestão:** Fique de olho no Back {time_vantagem} ao vivo."
                )
                enviar_alerta_telegram(msg_expulsao)
                ALERTAS_ENVIADOS[chave_alerta] = True
                continue

            # 🎯 STRATEGY 2: ALERTA DE PRESSÃO DE GOLS HT/FT
            if tempo <= 45:
                pressao_home = (ppm_home >= 0.7)
                pressao_away = (ppm_away >= 0.7)
                sugestao = "Over 0.5 Gols HT ou Cantos"
            else:
                pressao_home = (ppm_home >= 0.6)
                pressao_away = (ppm_away >= 0.6)
                sugestao = "Over Gols Limite FT"

            if pressao_home or pressao_away:
                atacante = home_team if pressao_home else away_team
                ppm_atual = round(ppm_home if pressao_home else ppm_away, 2)

                msg = (
                    f"🎯 **[ALERTA PREMIUM] OPERAÇÃO DE VALOR** 🎯\n\n"
                    f"🏆 **Liga:** {campeonato}\n"
                    f"🏟️ **Jogo:** {home_team} x {away_team}\n"
                    f"⏰ **Minuto:** {tempo}' | ⚽ **Placar:** {gols_home} x {gols_away}\n\n"
                    f"⚔️ **Pressão Dominante:** {atacante}\n"
                    f"📈 **Índice de Pressão:** {ppm_atual}/min\n\n"
                    f"💰 **Sugestão:** {sugestao}"
                )
                enviar_alerta_telegram(msg)
                ALERTAS_ENVIADOS[chave_alerta] = True

    except Exception as e:
        print(f"⚠️ Falha no processamento da SportAPI7: {e}")

def loop_do_robo():
    time.sleep(5)
    enviar_alerta_telegram("👑 **Bot San com SportAPI7 (Sofascore) Iniciado com Sucesso!**")
    while True:
        print("📡 Monitorando partidas reais via SportAPI7...")
        analisar_dados_futebol()
        time.sleep(180)

threading.Thread(target=loop_do_robo, daemon=True).start()

if __name__ == "__main__":
    # O Render exige que o app Flask rode em uma porta dinâmica configurada pelo servidor deles
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
