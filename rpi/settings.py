"""
* -----------------------------------------------------------------------------------
* Last update :   15/05/2024
* Arrosage Automatique / IrriPi
* NOT WORK
* -----------------------------------------------------------------------------------
"""

class Settings:  
    #initializing the variables  
    Coef = 100
    Mode = "Auto"
    TestDuree = 30
    SequenceDemande = "S1"
    HeureDemande = 12
    MinuteDemande = 0
    Source = "Canal"
    PressionSeuilBas = 1
    PressionSeuilHaut = 8
    PressionDiffMax = 0.3
    TestPressionCanal = 0
    TestPressionCuve = 0
    TestPressionVille = 0
    TestHauteurEauCuve = 0
    SeuilMinCapaciteCuve = 10

    #constructor  
    def __init__(self, SettingsCoef, SettingsMode, SettingsTestDuree, SettingsSequenceDemande, SettingsHeureDemande, SettingsMinuteDemande, SettingsSource, SettingsPressionSeuilBas, SettingsPressionSeuilHaut, SettingsPressionDiffMax, SettingsTestPressionCanal, SettingsTestPressionCuve, SettingsTestPressionVille, SettingsTestHauteurEauCuve, SettingsSeuilMinCapaciteCuve):  
        self.Mode = SettingsMode
        self.Coef = SettingsCoef  
        self.TestDuree =  SettingsTestDuree
        self.SequenceDemande = SettingsSequenceDemande  
        self.HeureDemande = SettingsHeureDemande
        self.MinuteDemande = SettingsMinuteDemande
        self.Source = SettingsSource
        self.PressionSeuilBas = SettingsPressionSeuilBas
        self.PressionSeuilHaut = SettingsPressionSeuilHaut
        self.PressionDiffMax = SettingsPressionDiffMax
        self.TestPressionCanal = SettingsTestPressionCanal
        self.TestPressionCuve =  SettingsTestPressionCuve
        self.TestPressionVille = SettingsTestPressionVille
        self.TestHauteurEauCuve = SettingsTestHauteurEauCuve
        self.SeuilMinCapaciteCuve = SettingsSeuilMinCapaciteCuve
  


canalpupstream = global_settings["pression_canal_amont"].iloc[0]
canalpdownstream = global_settings["pression_canal_aval"].iloc[0]
tankpupstream = global_settings["pression_cuve_amont"].iloc[0]
tankpdownstream = global_settings["pression_cuve_aval"].iloc[0]
pville = global_settings["pression_ville"].iloc[0]
pvarrosage = global_settings["pression_arrosage"].iloc[0]
height = global_settings["hauteur_eau_cuve"].iloc[0]

