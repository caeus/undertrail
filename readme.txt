Es un proyecto Django con un solo servicio "/api/search_ticket". Copio la documentación del código aquí mismo, just in case.
	
    # Bueno pues... los parametros del query que hay que usar son "from" y "to" para la ciudad de destino
    # y origen, respectivamente... el valor esperado es el nombre de alguna de las ciudades (case insensitive).
    # el parametro "round_trip" es usado para indicar que se necesita pasaje de vuelta también, "true" si sí,
    # cualquier cosa de lo contrario.
    # los parametros "depart" y "return" esperan fechas en el formato "YYYY-MM-DD" e indican la fecha de ida
    # y regreso, respectivamente.
    # Disclaimer: Las malas prácticas se deben a mi inexperiencia con Python.