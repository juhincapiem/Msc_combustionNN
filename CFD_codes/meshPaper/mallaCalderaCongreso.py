import gmsh
import sys
import os
import pandas as pd
import numpy as np



# Read information from .txt file ---------------------------------------
numPoints = 21
surface = 10 + 1


simData = pd.read_csv("meshInfo.dat")
simData.to_numpy()
simData.columns = simData.columns.str.strip()
simData.set_index('Variable',inplace=True)
print(simData)

front  = np.float64(simData.loc["front"]['Value'])
back  = np.float64(simData.loc["back"]['Value'])

sizeX  = np.float64(simData.loc["sizeX"]['Value'])
sizeY  = np.float64(simData.loc["sizeY"]['Value'])


fileName = simData.loc["fileName"]['Value']

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


# Creo la entidad punto para los 21 puntos de la geometríá ------------------------
for i in range(0, len(posX)):
    #Definir puntos
    gmsh.model.geo.addPoint(posX[i], posY[i], front, 1, i+1)


# Creo las líneas a partir de los puntos ------------------------------------------
# Primero creo las líneas con los puntos enumerados desde el 1 hasta el 20
for i in range(1,20): # ---> tengo hasta el tag 19
    gmsh.model.geo.addLine(i, i+1, i)  


# Las siguientes línes se deben crear de manera manual. Casi todas son líneas internas
gmsh.model.geo.addLine(20, 1, 20)
gmsh.model.geo.addLine(3, 20, 21)
gmsh.model.geo.addLine(3, 18, 22)
gmsh.model.geo.addLine(4, 17, 23)
gmsh.model.geo.addLine(17, 6, 24)
gmsh.model.geo.addLine(16, 7, 25)
gmsh.model.geo.addLine(16, 21, 26)
gmsh.model.geo.addLine(21, 8, 27)
gmsh.model.geo.addLine(10, 21, 28)
gmsh.model.geo.addLine(14, 21, 29)
gmsh.model.geo.addLine(14, 11, 30)


# Creo los bucles de líneas anti-horario a partir de las líneas ------------------------------------------
gmsh.model.geo.addCurveLoop([1, 2, 21, 20], 1)
gmsh.model.geo.addCurveLoop([-21, 22, 18, 19], 2)
gmsh.model.geo.addCurveLoop([3, 23, 17, -22], 3)
gmsh.model.geo.addCurveLoop([4, 5, -24, -23], 4)
gmsh.model.geo.addCurveLoop([24, 6, -25, 16], 5)
gmsh.model.geo.addCurveLoop([25, 7, -27, -26], 6)
gmsh.model.geo.addCurveLoop([14, 15, 26, -29], 7)
gmsh.model.geo.addCurveLoop([27, 8, 9, 28], 8)
gmsh.model.geo.addCurveLoop([-28, 10, -30, 29], 9)
gmsh.model.geo.addCurveLoop([11, 12, 13, 30], 10)

gmsh.model.geo.synchronize()

# Es necesario hacer unos cálculos para saber el número de elementos -------------------------------------
# Primero se calcula el número de nodos en dirección Y
pared1 = int(round( (posY[19] - posY[1]) /(sizeY) + 1))
pared2 = int(round( (posY[18] - posY[19]) /(sizeY) + 1))
pared3 = int(round( (posY[15] - posY[16]) /(sizeY) + 1))
pared4 = int(round( (posY[13] - posY[14]) /(sizeY) + 1))
pared5 = int(round( (posY[11] - posY[12]) /(sizeY) + 1))

# Luego se calcula el número de nodos en dirección X
piso1 = int(round( (posX[1] - posX[0]) /(sizeY) + 1))
piso2 = int(round( (posX[3] - posX[2]) /(sizeY) + 1))
piso3 = int(round( (posX[4] - posX[3]) /(sizeY) + 1))
piso4 = int(round( (posX[15] - posX[14]) /(sizeY) + 1))
piso5 = int(round( (posX[13] - posX[12]) /(sizeY) + 1))


# Se definen las líneas que deben tener el mismo número de elementos en dirección Y ----------------------
for tag in [20, -2]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared1)

for tag in [19, -22, -23, -5]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared2)

for tag in [16, -6]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared3)

for tag in [14, -26, -7]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared4)

for tag in [12, -30, 28, -8]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, pared5)

gmsh.model.geo.synchronize()


# Se definen las líneas que deben tener el mismo número de elementos en dirección X ----------------------
for tag in [1, -21, -18]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso1)

for tag in [3, -17]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso2)

for tag in [4, 24, 25, 27, -9]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso3)

for tag in [15, 29, -10]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso4)

for tag in [13, -11]:
    gmsh.model.geo.mesh.setTransfiniteCurve(tag, piso5)


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

for i in range(1,surface): # ----> 10 superficies
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
gmsh.model.addPhysicalGroup(2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1)
gmsh.model.setPhysicalName(2, 1, "front")

gmsh.model.addPhysicalGroup(2, [52, 74, 96, 118, 140, 162, 184, 206, 228, 250], 2)
gmsh.model.setPhysicalName(2, 2, "back")

gmsh.model.addPhysicalGroup(2, [39], 3)
gmsh.model.setPhysicalName(2, 3, "inlet")

gmsh.model.addPhysicalGroup(2, [241], 4)
gmsh.model.setPhysicalName(2, 4, "outlet")

gmsh.model.addPhysicalGroup(2, [43, 51, 69, 73, 83, 91, 105, 109, 131, 139, 153, 171, 175, 197, 201, 219, 237, 245], 5)
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
