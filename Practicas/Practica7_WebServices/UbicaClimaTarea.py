import requests

def obtener_informacion_ubicacion(geonames_username, lugar):
    url = f"http://api.geonames.org/searchJSON?name={lugar}&maxRows=1&username={geonames_username}"

    try:
        response = requests.get(url)
        data = response.json()
        if "geonames" in data and data["geonames"]:
            ubicacion = data["geonames"][0]
            nombre = ubicacion['name']
            pais = ubicacion['countryName']
            print(f"Nombre: {nombre}")
            print(f"País: {pais}")
            print(f"Población: {ubicacion['population']}")
            return nombre, pais
        else:
            print("Ubicación no encontrada.")
            return None, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

def obtener_datos_meteorologicos(api_key, ciudad):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        if "main" in data and "weather" in data:
            temperatura = data["main"]["temp"] - 273.15  # Convertir de Kelvin a Celsius
            condiciones_climaticas = data["weather"][0]["description"]
            print(f"Temperatura: {temperatura:.2f}°C")
            print(f"Condiciones Climáticas: {condiciones_climaticas}")
        else:
            print("Datos meteorológicos no disponibles.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Coloca tu usuario de geonames
    geonames_username = "bealeth"
    
    lugar = input("Ingresa el lugar que deseas consultar: ")  # Solicita la entrada del usuario
    nombre, pais = obtener_informacion_ubicacion(geonames_username, lugar)
    
    if nombre and pais:
        api_key = "e11ca42a4de6cf90b055f8c4fe9062a2"  # tu api key
        obtener_datos_meteorologicos(api_key, nombre)  # Usamos el nombre del lugar obtenido
