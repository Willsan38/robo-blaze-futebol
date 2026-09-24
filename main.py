import time
import requests
import threading
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Robô San Inteligência Analítica está ativo na nuvem!"

TOKEN_TELEGRAM = "8806798911:AAHqoFfNFVS-jmMsq2S_h50z4-QjOaHdYLU"
CHAT_ID_TELEGRAM = "5830126430"
RAPIDAPI_KEY = "446a783e1amsh8ee8aa170210cf5p19e0e4jsn8df18624fa00"
RAPIDAPI_HOST = "://rapidapi.com"

ALERTAS_ENVIADOS = {}

print("🚀 [ANALÍTICO] Bot San de Estatísticas Mastigadas Inicializado!")

def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 Telegram Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

def analisar_dados_futebol():
    url = f"https://{RAPIDAPI_HOST}/api/v1/sport/football/events/live"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return
            
        dados = response.json()
        jogos = dados.get("events", [])
        
        if not jogos:
            print("💤 Monitorando... Nenhuma partida ativa no radar.")
            return

        for jogo in jogos:
            match_id = jogo.get("id")
            if not match_id: continue

            status_jogo = jogo.get("status", {})
            if status_jogo.get("type") != "inprogress": continue
            
            tempo = status_jogo.get("elapsed", 0)
            if not tempo or tempo < 1: continue

            campeonato = jogo.get("tournament", {}).get("name", "Liga")
            home_team = jogo.get("homeTeam", {}).get("name", "Casa")
            away_team = jogo.get("awayTeam", {}).get("name", "Fora")
            
            gols_home = jogo.get("homeScore", {}).get("current", 0)
            gols_away = jogo.get("awayScore", {}).get("current", 0)

            periodo_jogo = "HT" if tempo <= 45 else "FT"
            chave_alerta = f"{match_id}_{periodo_jogo}"
            if chave_alerta in ALERTAS_ENVIADOS: continue

            ap_home = jogo.get("pressureIndex", {}).get("home", 0)
            ap_away = jogo.get("pressureIndex", {}).get("away", 0)
            
            # ========================================================================
            # MÓDULO SUPER SENSÍVEL DE TESTE (Modificado para pegar qualquer jogo ativo)
            # ========================================================================
            if ap_home >= 15 or ap_away >= 15:
                cenario_pressao = "🔥 ABAFA ATIVO (Análise de Teste de Sinal)"
                nivel_critico = True
            else:
                cenario_pressao = "💤 RITMO COMPASSADO (Análise de Teste de Sinal)"
                nivel_critico = True # Força o disparo mesmo se estiver lento

            time_dominante = home_team if ap_home >= ap_away else away_team
            maior_pressao = max(ap_home, ap_away)

            if tempo <= 35:
                sugestao_mastigada = "Over 0.5 Gols HT (Modo Teste Ativo)"
            else:
                sugestao_mastigada = "Over Gols Limite FT ou Cantos (Modo Teste Ativo)"

            if nivel_critico:
                msg_mastigada = (
                    f"👑 **[ANÁLISE MASTIGADA SAN - TESTE]** 👑\n\n"
                    f"🏆 **Competição:** {campeonato}\n"
                    f"🏟️ **Partida:** {home_team} x {away_team}\n"
                    f"⏰ **Tempo de Jogo:** {tempo}' minutos\n"
                    f"⚽ **Placar Atual:** {gols_home} x {gols_away}\n\n"
                    f"📈 **Diagnóstico Técnico:**\n"
                    f"└ {cenario_pressao}\n"
                    f"└ **Time Dominante:** {time_dominante}\n"
                    f"└ **Poder de Ataque:** {maior_pressao}% de controle\n\n"
                    f"💰 **Sugestão Pronta:**\n"
                    f"👉 `{sugestao_mastigada}`"
                )
                enviar_alerta_telegram(msg_mastigada)
                ALERTAS_ENVIADOS[chave_alerta] = True

    except Exception as e:
        print(f"⚠️ Erro de leitura analítica: {e}")

def loop_do_robo():
    time.sleep(5)
    enviar_alerta_telegram("👑 **Bot San com Módulo Super Sensível Iniciado no Render!**")
    while True:
        print("📡 Analisando partidas e mastigando estatísticas...")
        analisar_dados_futebol()
        time.sleep(180)

threading.Thread(target=loop_do_robo, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
