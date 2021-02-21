import random
from time import sleep
from numpy import append
from pymongo.common import SERVER_SELECTION_TIMEOUT
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time 
import pandas as pd
from pymongo import MongoClient
import json

## conectar con Mongo

client=MongoClient('localhost')

db= client['premier_League_datos']
col=db['datos']
col_part=db['datos partidos']
col_gole=db['datos goleadores']


cuenta = 0
def contador():
  global cuenta
  cuenta+=1

###listas para guardar la información recolectada
datos=[]
datos1=[]
gol_L=[]
gol_V=[]
juggol=[]
eqgol=[]
numgle=[]
asistencias=[]
nombre_gol=[]
equipo_gol=[]
equipo_clasificacion=[]
datos_clasificacion=[]
match_dates=[]

##iniciar webscraping

options =  webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')

driver_path =r'C:\Users\Victor Daniel Muñoz\Desktop\chromedriver.exe'

driver = webdriver.Chrome(driver_path, chrome_options=options)
driver.get(r"https://www.flashscore.co/futbol/inglaterra/premier-league/resultados/") ##link donde se va a extraer
i=0


#click botón resultados
button = driver.find_element_by_xpath("//*[@id='live-table']/div[1]/div/div/a")
driver.execute_script("arguments[0].click();", button)

#scroll hacia abajo
for i in range(100):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    

#click ver mas
button1 = driver.find_element_by_css_selector(".event__more.event__more--static")
driver.execute_script("arguments[0].click();", button1)

for i in range(100):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
#click ver mas
equipos= driver.find_elements_by_css_selector('.event__participant.event__participant--home')
for item in equipos:
   datos.append(item.text)
  
#recolectar datos nombre equipo visitante
visitante=driver.find_elements_by_css_selector('.event__participant.event__participant--away')
for ite in visitante:
  datos1.append(ite.text)

#recolectar datos nombre equipo local
gol_local=driver.find_elements_by_css_selector('.event__scores.fontBold > span:nth-child(1)')
for it in gol_local:
  gol_L.append(it.text)

gol_visitante=driver.find_elements_by_css_selector('.event__scores.fontBold > span:nth-child(2)')
for itt in gol_visitante:
  gol_V.append(itt.text)

fecha_partido=driver.find_elements_by_css_selector('.event__time')
for fp in fecha_partido:
  match_dates.append(fp.text)

#una vez seleccionada la información de esa pagina
#voy a ver los goleadores en el boton resumen click y luego click en goleadores

resumen = driver.find_element_by_xpath("//*[@id='li0']")
driver.execute_script("arguments[0].click();", resumen)

#click goleadores
goleadores= driver.find_element_by_xpath("//*[@id='tournament-table-tabs-and-content']/div[1]/div/a[5]")
driver.execute_script("arguments[0].click();", goleadores)

#scroll hacia abajo
for i in range(100):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#recolectar info
gole_mostrar = driver.find_element_by_css_selector(".showMore___20xQP9D")
driver.execute_script("arguments[0].click();", gole_mostrar)

equipo_goleador=driver.find_elements_by_css_selector('.rowCellParticipant___2ZhTRXj ')
for eqj in equipo_goleador:
  eqgol.append(eqj.text)


#como me sale informacion conjunta entonces separo en dos listas 
#el nombre del equipo y del goleador
for i in range(0,len(eqgol)):
  if i%2==0:
    nombre_gol.append(eqgol[i])
  else:
    equipo_gol.append(eqgol[i])

#recolecta los goles del goleador  
gol_gole=driver.find_elements_by_css_selector('.rowCellGoals___2U1t82E.rowCell___1lsmgjt')

for numgol in gol_gole:
  numgle.append(numgol.text)

#recolecta asistencias
asist= driver.find_elements_by_css_selector('.gray___2DCs7tj.rowCell___1lsmgjt')

for numasi in asist:
  asistencias.append(numasi.text)

# click en el botton clasificacion
clasificacion = driver.find_element_by_css_selector('.tabs__tab.selected')
driver.execute_script("arguments[0].click();", clasificacion)

eq_cla= driver.find_elements_by_css_selector('.rowCellParticipantName___38vskiN')

for pos in eq_cla:
  equipo_clasificacion.append(pos.text)

datos_clas= driver.find_elements_by_css_selector('.rowCell____vgDgoa.cell___4WLG6Yd')

for dacla in datos_clas:
  datos_clasificacion.append(dacla.text)
#infromacion recolectada pero necesito separar
#por eso separo en listas con el procedimiento de abajo
pj=[]
resto=[]
G=[]
resto1=[]
E=[]
resto2=[]
P=[]
Pts=[]

for i in range(0,len(datos_clasificacion)):
  if i%5==0:
    pj.append(datos_clasificacion[i])
  else:
    resto.append(datos_clasificacion[i])

for i in range(0,len(resto)):
  if i%4==0:
    G.append(resto[i])
  else:
    resto1.append(resto[i])

for i in range (0,len(resto1)):
  if i%3==0:
    E.append(resto1[i])
  else:
    resto2.append(resto1[i])

for i in range(0,len(resto2)):
  if i%2==0:
    P.append(resto2[i])
  else:
    Pts.append(resto2[i])

ult_part=[]
ult_part_fix=[]

#recolecto info de ultimos partidos 
ultimos_partidos=driver.find_elements_by_css_selector('.rowCellForm___34WvlzC')

for g in ultimos_partidos:
  ult_part.append(g.text)

#teniendo en cuenta toda la info recolectada
#se procede a subir a Mongo la forma deberá ser tal cual como la mostrada a continuación

for i in range(0,len(equipo_clasificacion)):
  df_clasificacion=[{'Equipo': equipo_clasificacion[i],'PJ': pj[i],'PG':G[i],'PE':E[i],'PP':P[i],'Pts':Pts[i],'ult_partidos':ult_part[i]}]
  col.insert_many(df_clasificacion)

for i in range(0,len(nombre_gol)):
  df_goleadores=[{'Goleador': nombre_gol[i],'Equipo': equipo_gol[i],'goles':numgle[i],'asistencias':asistencias[i]}]
  col_gole.insert_many(df_goleadores)

for i in range(0,len(datos)):
  df_resultados=[{'local': datos[i],'visitante':datos1[i],'goles local':gol_L[i],'goles visitante':gol_V[i],'fecha':match_dates[i]}]
  col_part.insert_many(df_resultados)


print(df_resultados)
print(df_clasificacion)

