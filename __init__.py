from mycroft import MycroftSkill, intent_file_handler


class Meteo(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('meteo.intent')
    def handle_meteo(self, message):
        weather = ''

        self.speak_dialog('meteo', data={
            'weather': weather
        })


def create_skill():
    return Meteo()

