import gmsh
import sys
import os
import pandas as pd
import numpy as np


# Read information from .txt file ---------------------------------------
numPoints = 29
surface = 14 + 1
fileName = "mallaCalderaPaperV01"


simData = pd.read_csv("mallaCalderaPaper.dat")
simData.to_numpy()
simData.columns = simData.columns.str.strip()
simData.set_index('Variable',inplace=True)
print(simData)

front  = np.float64(simData.loc["front"]['Value'])
back  = np.float64(simData.loc["back"]['Value'])

sizeX  = np.float64(simData.loc["sizeX"]['Value'])
sizeY  = np.float64(simData.loc["sizeY"]['Value'])
sizeZ  = np.float64(simData.loc["sizeZ"]['Value'])


# Create vectors with x and y coordintates ---------------------------------------
posX = np.zeros(numPoints, dtype=np.float64)
posY = np.zeros(numPoints, dtype=np.float64)

for i in range(len(posX)):
    posX[i]  = np.float64(simData.loc['p{:.0f}x'.format(i+1)]['Value'])
    posY[i]  = np.float64(simData.loc['p{:.0f}y'.format(i+1)]['Value'])
print(posX)

# Initial configuration of gmsh ---------------------------------------------------
gmsh.initialize()
gmsh.option.setNumber("General.Terminal",1)
gmsh.model.add("calcinador")


# Creo la entidad punto para los n puntos de la geometríá ------------------------
for i in range(0, len(posX)):
    #Definir puntos
    gmsh.model.geo.addPoint(posX[i], posY[i], front, 1, i+1)


# Creo las líneas a partir de los puntos ------------------------------------------
# Primero creo las líneas con los puntos enumerados desde el 1 hasta el 28
for i in range(1,28): # ---> tengo hasta el tag 27
    gmsh.model.geo.addLine(i, i+1, i)  


# Las siguientes línes se deben crear de manera manual. Casi todas son líneas internas
gmsh.model.geo.addLine(28, 1, 28)
gmsh.model.geo.addLine(2, 27, 29)
gmsh.model.geo.addLine(3, 8, 30)
gmsh.model.geo.addLine(8, 27, 31)
gmsh.model.geo.addLine(4, 7, 32)
gmsh.model.geo.addLine(26, 9, 33)
gmsh.model.geo.addLine(9, 24, 34)
gmsh.model.geo.addLine(10, 23, 35)
gmsh.model.geo.addLine(23, 12, 36)
gmsh.model.geo.addLine(13, 22, 37)
gmsh.model.geo.addLine(14, 29, 38)
gmsh.model.geo.addLine(29, 22, 39)
gmsh.model.geo.addLine(16, 29, 40)
gmsh.model.geo.addLine(20, 29, 41)
gmsh.model.geo.addLine(17, 20, 42)


# Creo los bucles de líneas anti-horario a partir de las líneas ------------------------------------------
gmsh.model.geo.addCurveLoop([1, 29, 27, 28], 1)
gmsh.model.geo.addCurveLoop([2, 30, 31, -29], 2)
gmsh.model.geo.addCurveLoop([3, 32, 7, -30], 3)
gmsh.model.geo.addCurveLoop([4, 5, 6, -32], 4)
gmsh.model.geo.addCurveLoop([-31, 8, -33, 26], 5)
gmsh.model.geo.addCurveLoop([33, 34, 24, 25], 6)
gmsh.model.geo.addCurveLoop([9, 35, 23, -34], 7)
gmsh.model.geo.addCurveLoop([10, 11, -36, -35], 8)
gmsh.model.geo.addCurveLoop([36, 12, 37, 22], 9)
gmsh.model.geo.addCurveLoop([-37, 13, 38, 39], 10)
gmsh.model.geo.addCurveLoop([21, -39, -41, 20], 11)
gmsh.model.geo.addCurveLoop([-38, 14, 15, 40], 12)
gmsh.model.geo.addCurveLoop([41, -40, 16, 42], 13)
gmsh.model.geo.addCurveLoop([19, -42, 17, 18], 14)

gmsh.model.geo.synchronize()

# Es necesario hacer unos cálculos para saber el número de elementos -------------------------------------
# Primero se calcula el número de nodos en dirección Y
pared1 = int(round( (posY[27] - posY[0]) /(sizeY) + 1))
pared2 = int(round( (posY[25] - posY[26]) /(sizeY) + 1))
pared3 = int(round( (posY[24] - posY[25]) /(sizeY) + 1))
pared4 = int(round( (posY[21] - posY[22]) /(sizeY) + 1))
pared5 = int(round( (posY[19] - posY[20]) /(sizeY) + 1))
pared6 = int(round( (posY[17] - posY[18]) /(sizeY) + 1))

# Luego se calcula el número de nodos en dirección X
piso1 = int(round( (posX[1] - posX[0]) /(sizeX) + 1))
piso2 = int(round( (posX[2] - posX[1]) /(sizeX) + 1))
piso3 = int(round( (posX[3] - posX[2]) /(sizeX) + 1))
piso4 = int(round( (posX[4] - posX[3]) /(sizeX) + 1))
piso5 = int(round( (posX[21] - posX[20]) /(sizeX) + 1))



# Se definen las líneas que deben tener el mismo número de elementos en dirección Y ----------------------
for tag in [-28, 29, 30, 32, 5]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared1)

for tag in [-26, 8]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared2)

for tag in [-25, 34, 35, 11]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared3)

for tag in [-22, 12]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared4)

for tag in [-20, -39, 13]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared5)

for tag in [-18, -42, -40, 14]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared6)



# Se definen las líneas que deben tener el mismo número de elementos en dirección X ----------------------
for tag in [1, -27, 19, -17]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso1)

for tag in [2, -31, 33, -24]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso2)

for tag in [3, -7, 9, -23]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso3)

for tag in [4, -6, 10, 36, -37, -38, -15]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso4)

for tag in [21, 41, -16]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso5)


gmsh.model.geo.synchronize()

# Superficie  a partir de los bucles. Esto indica que es macizo, y no un agujero ------------------------
for i in range(1,surface): # ----> 10 superficies
    gmsh.model.geo.addPlaneSurface([i], i)


# Definir que la superficie sea estrcuturada, al igual que las curvas ------------------------------------
for i in range(1,surface): # ----> 10 superficies
    gmsh.model.geo.mesh.setTransfiniteSurface(i)

# Recombinamos para que se usen elementos cuadriláteros en vez de triangulares ---------------------------
for i in range(1, surface): # ----> 10 superficies
    gmsh.model.geo.mesh.setRecombine(2, i)

gmsh.model.geo.synchronize()

# Extruimos las superficies [(superficie, tag)] ----------------------------------------------------------

volumeTags = []

for i in range(1,surface): # ----> 14 superficies
    volumeEntities = gmsh.model.geo.extrude([(2, i)], 0, 0, back, numElements=[1], recombine=True)

    # Extraemos el tag que identifica al volumen. Para esto hay que hacer una búsqueda
    for entity in volumeEntities:
        if entity[0] == 3: # Estamos buscando tags de volumen
            volumeTags.append(entity[1])


# Ya no es necesario acceder al diccionario, como lo solía hacer. ----------------------------------------
# Ahora tengo almacenado los tags en una lista. Defino el volumen como transfinito
for tag in volumeTags:
    gmsh.model.geo.mesh.setTransfiniteVolume(tag)


# Junto todo el domingo en un grupo Físico, con el tag 101 -----------------------------------------------
gmsh.model.addPhysicalGroup(3, volumeTags, 101)

# Le pongo nombre a las fronteras. Esto sirve para identificarles en OF ----------------------------------
gmsh.model.addPhysicalGroup(2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], 1)
gmsh.model.setPhysicalName(2, 1, "front")

gmsh.model.addPhysicalGroup(2, [64, 86, 108, 130, 152, 174, 196, 218, 240, 262, 284, 306, 328, 350], 2)
gmsh.model.setPhysicalName(2, 2, "back")

gmsh.model.addPhysicalGroup(2, [51, 73, 95, 117], 3)
gmsh.model.setPhysicalName(2, 3, "inlet")

gmsh.model.addPhysicalGroup(2, [349], 4)
gmsh.model.setPhysicalName(2, 4, "outlet")

gmsh.model.addPhysicalGroup(2, [59, 63, 103, 121, 125, 143, 151, 169, 173, 183, 191, 205, 209, 231, 239, 253, 271, 283, 297, 301, 323, 327, 337, 345], 5)
gmsh.model.setPhysicalName(2, 5, "walls")


#----
# Cuando se hacen mallas estrcturada, la sincronización se da después del recombine
#----
gmsh.model.geo.synchronize()

# Crea malla de dimensión 3
gmsh.model.mesh.generate(3)

# Ver las "caras" de los elementos finitos 2D
gmsh.option.setNumber('Mesh.SurfaceFaces', 1)

# Ver los nodos de la malla  
gmsh.option.setNumber('Mesh.Points', 1)

# Algorimto para enmallar 
#gmsh.option.setNumber("Mesh.Algorithm", 5)

# Y finalmente guardar la malla
gmsh.option.setNumber("Mesh.MshFileVersion",2.2)  
gmsh.write(fileName + ".msh")



# Podemos visualizar el resultado en la interfaz gráfica de GMSH
gmsh.fltk.run()

# Tras finalizar el proceso se recomienda usar este comando
gmsh.finalize()
