from mycroft import MycroftSkill, intent_file_handler
import requests


class Meteo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def get_oauth_token(self):
        # followed: https://developer.srgssr.ch/content/easy-description-get-accesstoken

        # 1. encode credentials via base64
        encoded_credentials = "WDd2UkxYTEl6SnhFR2tHeW9pc0d6Rk9Fc0dvVnJsR0E6NnhRb25nRlFnN0E4Wld2aw=="
        # 2. get oauth access token

        headers = {
            'Authorization': 'Basic {}'.format(encoded_credentials),
            'Cache-Control': 'no-cache',
            'Content-Length': '0', 
            'Postman-Token': '24264e32-2de0-f1e3-f3f8-eab014bb6d76'
        }

        oauth_answer = requests.post(
                url='https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials', 
                headers=headers
            )
        return oauth_answer.json().get("access_token", "")


    def get_meteo(self, oauth_token, latitude, longitude):
        # get meteo data
        api_url = "https://api.srgssr.ch/forecasts/v1.0/weather/nexthour?latitude={}}%09&longitude={}".format(latitude, longitude)
        headers = {
            'authorization': "Bearer {}".format(oauth_token),
            'Cache-Control': 'no-cache',
            'Postman-Token': '56128353-805e-4974-6689-5ef6d86e2d80'
        }

        response = requests.get(url=api_url, headers=headers).json()
        # format:   
        # "info": {
        #     "id": 5000,
        #     "name": {
        #       "de": "Aarau"
        #     },
        #     "plz": 5000
        # },
        self.info_location = response.get("info")
        self.location_name = self.info_location.get("name").get("de")
        self.data = {}
        values_as_list = response.get("nexthour")[0].get("values")
        self.keys = []
        ### POSSIBLE VALUES
        # "dd3": "winddirection_10m_mean_3h",
        # "ddd": "winddirection_10m_mean_1d",
        # "ff3": "windspeed_10m_mean_3h",
        # "ffd": "windspeed_10m_mean_1d",
        # "fff": "windspeed_10m_mean_1h",
        # "ffx3":"windspeed_10m_max_3h",
        # "fxd": "windspeed_10m_max_1d",
        # "pr3": "probrain_3h",
        # "prd": "probrain_1d",
        # "rr3": "precipitation_1.5m_sum_3h",
        # "rsd": "precipitation_1.5m_sum_1d",
        # "ttn": "temperature_2m_min",
        # "ttt": "temperature_2m_act",
        # "ttx": "temperature_2m_max",
        for val in values_as_list:
            key = list(val.keys())[0]
            self.data[key] = val.get(key)
            keys.append(key)

    def get_data(self, message):
        # TODO read lat, long out from zip code and spoken message
        # Default 8000 ZH
        latitude = '47.3828'	
        longitude = '8.5307'
        oauth_token = self.get_oauth_token()
        if (not oauth_token): 
            self.speak("Kann keine Meteo Daten finden, login fehlgeschlagen")
            return 1
        self.get_meteo(oauth_token, latitude, longitude)
        return 0

    @intent_file_handler('meteo.general.intent')
    def handle_meteo(self, message):
        answer = self.get_data(message)
        if (answer == 1):
            return 

        # TODO add random output + files according to available data
        # output
        if (all(x in keys for x in ['ttt', 'fff', 'pr3', 'rr3'])):
            files = ['meteo.all', 'meteo.temp.rain', 'meteo.temp.wind']
            dialog_file = random.choice(files)
            self.speak_dialog('meteo.all', data={
                'location': self.location_name,
                'temp': self.data.get("ttt"), 
                'wind': self.data.get('fff'), 
                'probsRain': self.data.get('pr3'), 
                'mmRain': self.data.get('rr3')
            })


def create_skill():
    return Meteo()

