import time
import requests
import threading
from flask import Flask, request, jsonify
import os
import random

app = Flask(__name__)

TOKEN_TELEGRAM = "8806798911:AAHqoFfNFVS-jmMsq2S_h50z4-QjOaHdYLU"
CHAT_ID_TELEGRAM = "5830126430"
RAPIDAPI_KEY = "446a783e1amsh8ee8aa170210cf5p19e0e4jsn8df18624fa00"
RAPIDAPI_HOST = "://rapidapi.com"

ALERTAS_ENVIADOS = {}

print("🚀 [PREMIUM] Bot San com Comando /atualizar Inicializado!")

def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 Telegram Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

def buscar_grade_ao_vivo():
    url = f"https://{RAPIDAPI_HOST}/api/v1/sport/football/events/live"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("events", [])
    except Exception as e:
        print(f"⚠️ Erro ao acessar API Football: {e}")
    return []

def analisar_dados_futebol():
    jogos = buscar_grade_ao_vivo()
    if not jogos:
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
        
        if ap_home >= 15 or ap_away >= 15:
            cenario_pressao = "🔥 ABAFA ATIVO (Análise Automática)"
            time_dominante = home_team if ap_home >= ap_away else away_team
            maior_pressao = max(ap_home, ap_away)
            sugestao_mastigada = "Over 0.5 Gols HT" if tempo <= 35 else "Over Gols Limite FT / Cantos"

            msg_mastigada = (
                f"👑 **[ANÁLISE AUTOMÁTICA SAN]** 👑\n\n"
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

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        if "message" in update and "text" in update["message"]:
            texto_mensagem = update["message"]["text"].strip()
            chat_id_remetente = str(update["message"]["chat"]["id"])

            if texto_mensagem == "/atualizar" and chat_id_remetente == CHAT_ID_TELEGRAM:
                print("⚡ Comando /atualizar recebido!")
                jogos = buscar_grade_ao_vivo()
                
                jogos_visto_ao_vivo = []
                for jogo in jogos:
                    if jogo.get("status", {}).get("type") == "inprogress":
                        home = jogo.get("homeTeam", {}).get("name", "Casa")
                        away = jogo.get("awayTeam", {}).get("name", "Fora")
                        g_home = jogo.get("homeScore", {}).get("current", 0)
                        g_away = jogo.get("awayScore", {}).get("current", 0)
                        minuto = jogo.get("status", {}).get("elapsed", 0)
                        liga = jogo.get("tournament", {}).get("name", "Liga")
                        
                        jogos_visto_ao_vivo.append(f"⏱️ {minuto}' - {home} {g_home}x{g_away} {away} ({liga})")

                # MÓDULO DE AUDITORIA: Se a API real estiver vazia, injeta jogos simulados para testar o painel
                if not jogos_visto_ao_vivo:
                    print("📡 Grade real vazia. Injetando dados de auditoria para teste.")
                    jogos_visto_ao_vivo.append(f"⏱️ {random.randint(15,38)}' - 🔴 Japão (Simulado) 0 x 0 Uruguai (Amistoso Internacional)")
                    jogos_visto_ao_vivo.append(f"⏱️ {random.randint(60,82)}' - 🟡 Coreia do Sul (Simulado) 1 x 0 Equador (Amistoso Internacional)")

                resposta_lista = "📋 **PAINEL DE JOGOS ATIVOS NO RADAR:**\n\n" + "\n".join(jogos_visto_ao_vivo)
                enviar_alerta_telegram(resposta_lista)
                
        return jsonify({"status": "sucesso"})
    return "🤖 Robô San Profissional está ativo com Webhook do Telegram!"

def configurar_webhook_telegram():
    time.sleep(10)
    url_render = os.environ.get("RENDER_EXTERNAL_URL")
    if url_render:
        url_setup = f"https://telegram.org{TOKEN_TELEGRAM}/setWebhook?url={url_render}"
        try:
            res = requests.get(url_setup, timeout=10)
            print(f"⚙️ Configuração de Webhook concluída: {res.text}")
        except Exception as e:
            print(f"❌ Erro ao registrar Webhook: {e}")

def loop_do_robo():
    time.sleep(5)
    enviar_alerta_telegram("👑 **Bot San Auditado e Pronto para Receber Comandos!**")
    threading.Thread(target=configurar_webhook_telegram, daemon=True).start()
    while True:
        analisar_dados_futebol()
        time.sleep(180)

threading.Thread(target=loop_do_robo, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
