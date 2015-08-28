import time
import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
import requests
from bs4 import BeautifulSoup, CData


# Create your views here.

def index(request):
    return HttpResponse("index")


# Con esto mapeo de el nombre de una ciudad, al código interno de teletiquet
city_mappings = {"barrancabermeja": "2848", "bogota": "1710", "bucaramanga": "2845", "cimitarra": "2868",
                 "cucuta": "2850",
                 "el banco": "2849", "medellin": "2860", "ccana": "2851", "pamplona": "1712", "pto berrio": "2861", }


# Mirando la respuesta del servicio, me doy cuenta que hay un form muy similar para pasajes de ida y
# venida, por tanto uso el mismo método helper
def extract_rides(soup_raw, form_id):
    rows = soup_raw.select("#%(form_id)s table tr" % {"form_id": form_id})
    rows.pop(0)
    rides = []
    for i, row in enumerate(rows):
        columns = list(row.find_all("td"))
        if len(columns) < 5:
            return []

        rides.append({"date": next(columns[1].strings),
                      "ride_type": next(columns[2].strings),
                      "available_seats": int(next(columns[3].strings)),
                      "online_price": (next(columns[4].strings))
                      })
    return rides


# Aquí hago el post request... Noté que la respuesta venía en un formato xml raro con <<[CDATA[]> que incluía el
# codigo relevante, por eso toca hacer parsing de la respuesta, y del texto interno de la respuesta también.
# xajaxargs tiene la información relevante como un esque urlencoded... me copié casi literalmente de lo que saqué
# de la consola de Chrome. queryParams igual, me copié de lo que decía Chrome
def teletiquete_rides(from_city, to_city, depart_date, return_date, round_trip=False, ):
    returns = "ida_regreso" if round_trip else "ida"
    xajaxargs = "<xjxquery><q>optOrigen=%(from_city)s&optDestino=%(to_city)s&rdViaje=%(returns)s&txtFecSalida=%(depart_date)s" \
                "&txtFecRegreso=%(return_date)s&idOperacionIda=&valTiqueteIda=&idOperacionRegreso=&valTiqueteRegreso=" \
                "&fecSalida=&fecSalidaLetra=&HoraSalida=&HoraRegreso=&fecRegresoLetra=&nomCiudadIda=&nomCiudadRegreso=" \
                "&nomTipoVehiculoIda=&nomTipoVehiculoRegreso=&ordenCompra=&totalTransaccion=</q></xjxquery>" % locals()
    queryParams = dict(funcion0="buscar_horario_viaje", funcion1="mostrar_bus_operacion",
                       funcion2="seleccionar_silla_operacion",
                       funcion3="resumen_pago_tiquete", funcion4="vende_silla_tiquete_online",
                       funcion5="seleccionar_silla_operacion_regreso", funcion6="consultar_estado_orden_compra",
                       funcion7="crear_usuario_online", funcion8="validar_usuario",
                       funcion9="cerrar_session_usuario",
                       funcion10="verificar_session_usuario", funcion11="mostrar_info_usuario",
                       funcion12="frm_mod_usuario_online",
                       funcion13="mod_usuario_online", funcion14="enviar_email_passwd")

    payload = {"xajax": "buscar_horario_viaje", "xajaxr": int(round(time.time() * 1000)),
               "xajaxargs[]": xajaxargs}
    response = requests.post("http://gateway.omega.teletiquete.com/includes/ajax/server.funciones_ajax.php",
                             params=queryParams, data=payload)
    response = BeautifulSoup(response.content, "html.parser")
    result = {}
    soup_depart = BeautifulSoup("%s" % response.find("cmd", attrs={"t": "divResultadoIda"}).contents[0],
                                "html.parser")

    result["departures"] = extract_rides(soup_depart, "frmOpIda")


    if round_trip:
        soup_return = BeautifulSoup("%s" % response.find("cmd", attrs={"t": "divResultadoRegreso"}).contents[0])
        result["returns"] = extract_rides(soup_return, "frmOpRegreso")
    return result


class SearchTickets(View):
    # Bueno pues... los parametros del query que hay que usar son "from" y "to" para la ciudad de destino
    # y origen, respectivamente... el valor esperado es el nombre de alguna de las ciudades (case insensitive).
    # el parametro "round_trip" es usado para indicar que se necesita pasaje de vuelta también, "true" si sí,
    # cualquier cosa de lo contrario.
    # los parametros "depart" y "return" esperan fechas en el formato "YYYY-MM-DD" e indican la fecha de ida
    # y regreso, respectivamente.
    # Disclaimer: Las malas prácticas se deben a mi inexperiencia con Python.
    def get(self, request):
        try:
            from_city = city_mappings[request.GET.get("from").lower()]
            to_city = city_mappings[request.GET.get("to").lower()]
            round_trip = request.GET.get("round_trip") == "true"

            depart_date = request.GET.get("depart")
            return_date = "" if not round_trip else request.GET.get("return")

            result = teletiquete_rides(from_city, to_city, depart_date, return_date, round_trip)

            return HttpResponse(json.dumps(result), content_type="application/json")
        except Exception as e:
            return HttpResponseBadRequest(json.dumps({"data": e.args}))
