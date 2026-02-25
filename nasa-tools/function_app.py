import azure.functions as func
import json
import requests
from datetime import datetime
import random
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

NASA_KEY = os.getenv("NASA_API_KEY")

@app.route(route="nasa_asteroids_monitor")
def nasa_asteroids_monitor(req: func.HttpRequest) -> func.HttpResponse:

    data_query = req.params.get('date')
    
    if not data_query:
        data_query = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={data_query}&end_date={data_query}&api_key={NASA_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        asteroides_na_data = data.get('near_earth_objects', {}).get(data_query, [])
        
        lista_resumo = []
        for astro in asteroides_na_data:
            resumo = {
                "nome": astro.get('name'),
                "perigoso": astro.get('is_potentially_hazardous_asteroid'),
                "tamanho_estimado_metros": {
                    "min": round(astro['estimated_diameter']['meters']['estimated_diameter_min'], 2),
                    "max": round(astro['estimated_diameter']['meters']['estimated_diameter_max'], 2)
                },
                "velocidade_km_h": round(float(astro['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']), 2),
                "distancia_da_terra_km": round(float(astro['close_approach_data'][0]['miss_distance']['kilometers']), 2)
            }
            lista_resumo.append(resumo)

        payload = {
            "data_pesquisada": data_query,
            "total_asteroides_detectados": len(lista_resumo),
            "asteroides": lista_resumo[:10]
        }

        return func.HttpResponse(
            json.dumps(payload, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Falha ao processar dados da NASA: {str(e)}"}),
            status_code=500
        )
    
@app.route(route="nasa_apod_gallery")
def nasa_apod_gallery(req: func.HttpRequest) -> func.HttpResponse:
    data_query = req.params.get('date')
    
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}"
    if data_query:
        url += f"&date={data_query}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        payload = {
            "titulo": data.get("title"),
            "data": data.get("date"),
            "explicacao": data.get("explanation"),
            "url_imagem": data.get("url"),
            "tipo_midia": data.get("media_type"),
            "copyright": data.get("copyright", "Domínio Público")
        }

        return func.HttpResponse(
            json.dumps(payload, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
    
@app.route(route="nasa_earth_events")
def nasa_earth_events(req: func.HttpRequest) -> func.HttpResponse:
    days_query = req.params.get('days')
    
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    
    params = {}
    if days_query:
        params['days'] = days_query
        params['status'] = 'all'
    else:
        params['status'] = 'open'

    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            return func.HttpResponse(json.dumps({"error": "Erro na EONET"}), status_code=response.status_code)

        data = response.json()
        events = data.get('events', [])

        if not events:
            return func.HttpResponse(
                json.dumps({"message": "Nenhum evento detectado no período informado."}),
                status_code=200
            )

        lista_eventos = []
        for ev in events[:10]:
            last_geom = ev.get('geometry', [{}])[-1]
            lista_eventos.append({
                "titulo": ev.get('title'),
                "categoria": ev.get('categories', [{}])[0].get('title'),
                "data_inicio": ev.get('geometry', [{}])[0].get('date'),
                "data_atualizacao": last_geom.get('date'),
                "coordenadas": last_geom.get('coordinates'),
                "status": "Ativo" if not ev.get('closed') else "Encerrado"
            })

        return func.HttpResponse(
            json.dumps({"periodo_dias": days_query or "atual", "eventos": lista_eventos}, ensure_ascii=False),
            mimetype="application/json", status_code=200
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)
    
@app.route(route="nasa_people_in_space")
def nasa_people_in_space(req: func.HttpRequest) -> func.HttpResponse:
    try:
        res_astros = requests.get("http://api.open-notify.org/astros.json", timeout=10)
        data_astros = res_astros.json()

        res_iss = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        data_iss = res_iss.json()

        astros = data_astros.get('people', [])
        
        payload = {
            "total_humanos_no_espaco": data_astros.get('number'),
            "astronautas": astros,
            "iss_posicao_atual": {
                "latitude": data_iss.get('iss_position', {}).get('latitude'),
                "longitude": data_iss.get('iss_position', {}).get('longitude')
            },
            "mensagem": "Dados em tempo real sobre a presença humana no espaço."
        }

        return func.HttpResponse(
            json.dumps(payload, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": "Não foi possível rastrear os astronautas agora."}), status_code=200)