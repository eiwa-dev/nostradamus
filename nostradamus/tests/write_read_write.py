from .. import *
from ..drivers import *
from ..drivers.built_in import *


class Buta(Referenceable):
    SECTION = 'butas'

    def __init__(self, carontido, **kwargs):
        super().__init__(**kwargs)
        self.carontido = carontido
    
    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        carontido = d['carontido']
        return cls(carontido = carontido, **kwargs)

    def as_dict(self, write_func = None):
        return {'carontido': self.carontido}

class Tafirosis(Referenceable):
    SECTION = 'tafirosisis'

    def __init__(self, cajeta_de_amarula, buta, **kwargs):
        super().__init__(**kwargs)
        self.cajeta_de_amarula = cajeta_de_amarula
        self.buta = buta
    
    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        cajeta_de_amarula = d['cajeta_de_amarula']
        buta = Buta.from_ref(d['buta'], read_func = read_func)
        return cls(cajeta_de_amarula = cajeta_de_amarula, buta = buta, **kwargs)

    def as_dict(self, write_func = None):
        return {'cajeta_de_amarula': self.cajeta_de_amarula,
                'buta': self.buta.as_ref(write_func = write_func) }

class GarlopaPiponguista(Referenceable):
    pass 

class Pichingo(Serializable):
    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        return cls()

    def as_dict(self, write_func = None):
        return {'tarangueta': 'choriblingo'}

class Pichileta(Referenceable):
    SECTION = 'pichiletas'

    def __init__(self, pichingo, sucutrule = 1, tafirosis = None, butas = [], **kwargs):
        super().__init__(**kwargs)
        self.sucutrule = sucutrule
        self.pichingo = pichingo
        self.tafirosis = tafirosis
        self.butas = Buta.List(butas)
    
    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        sucutrule = d['sucutrule']
        pichingo = Pichingo.from_dict(d['pichingo'], read_func = read_func, **kwargs)
        tafirosis = Tafirosis.from_ref(d['tafirosis'], read_func = read_func)
        butas = Buta.List.from_dict(d['butas'], read_func = read_func)
        return cls(sucutrule = sucutrule,
                   pichingo = pichingo,
                   tafirosis = tafirosis,
                   butas = butas,
                   **kwargs)

    def as_dict(self, write_func = None):
        return {'sucutrule': self.sucutrule,
                'pichingo': self.pichingo.as_dict(write_func = write_func),
                'tafirosis': self.tafirosis.as_ref(write_func = write_func),
                'butas': self.butas.as_dict(write_func = write_func) }


driver = DictionaryDriver()
db = Database(driver)


karina = Buta(carontido = 21)
anastasia = Buta(carontido = 18, name = 'Anastasia')
carola = Buta(carontido = 27, name = 'Carola')

buta = Buta(carontido = 23, name = 'Buta Generica')
tafirosis = Tafirosis(cajeta_de_amarula = 'caipiroska', buta = buta)
pichileta = Pichileta(name = 'Diego Nul',
                      tafirosis = tafirosis,
                      pichingo = Pichingo(),
                      butas = [anastasia, carola],
                      sucutrule = 9001)

db.write(pichileta)

first_d = dict(driver.d)

diego_nul = db.read((Pichileta, 'Diego Nul'))

driver = DictionaryDriver()
db = Database(driver)

db.write(diego_nul)

if first_d == driver.d:
    print('Dictionaries match')
else:
    print('Dictionaries DO NOT match')

