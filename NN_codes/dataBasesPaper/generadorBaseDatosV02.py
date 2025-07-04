# A diferencia de las otras versiones, lo que hace este generador de base de datos es recoger de las 
# carpetas de postProcessing: T, especies, velocidad, Presión registrados por la probeta #5. NO va a
# realizar integraciones, ni tampoco va a utilizar los valores promediados. Se usan lo valores tal y
# como salieron de la simulación. Técnicamente, se podria decir que es más sencillo que las versiones
# anteriores. Menos es más...

from postProcesingScalars import readProbeScalar
from postProcessingVectors import readOpenVector
import numpy as np
import pandas as pd
import os
import sys
import re


# Indico el directorio en donde se encuentran la base de datos
mainDirectory = './'

# Indico el directorio en donde se almacena ls info de la probetas
#pathProbes = 'probes/0'
pathProbes = 'postProcessing/probes/29.505'

# Voy a iterar por los nombre de todo lo que está contenido en el directorio y lo almaceno en el arreglo
# subdirs si efectivamente es un directorio y no un archivo.
directories = [name for name in os.listdir(mainDirectory) if os.path.isdir(os.path.join(mainDirectory, name))]

# Titulos de la base de datos
scalaFiles = ["CH4","CO2","CO","H2O","N2","O2","T","p"]
vectorFiles = ["U"]

probe = '6'

titles = ["T_inlet", "MFR_inlet"] + scalaFiles + vectorFiles

# Creamos una matriz en donde se almacenen la informació que se extraiga 
rows = len(directories)
cols = len(titles)
data = np.zeros((rows,cols))

nombreBaseDeDatos = 'baseDeDatosSinPosprocesamientoProbe6.csv'

# Empezamos el ciclo for que va a recorre todas las carpeta de simulación, y accede al
# directorio postProcessing

for rowIndex,caseName in enumerate(directories):
            
    # Creamos el nombre del caso
    pathCaseName = os.path.join(mainDirectory,caseName)

    # Extraemos información del título
    match = re.search(r'T(?P<temperature>\d+\.?\d*)_mfr(?P<mfr>\d+\.?\d*)', caseName)

    if match:
        inletTemp = float(match.group('temperature'))
        inletMFR = float(match.group('mfr'))
    else:
        print("Pattern not found.")
        continue

    # Guardamos en la fila el valor respectivo de la temperatura y flujo másico de entrada
    data[rowIndex][0] = inletTemp
    data[rowIndex][1] = inletMFR

    # Ingresamos a la carpeta donde quedó guardado todo
    for colIndex,scalar in enumerate(scalaFiles):
        pathProbesFiles = os.path.join(pathCaseName,pathProbes,scalar)

        # Llamo la función para leer información de los probes
        quantityProbe = readProbeScalar(pathProbesFiles)

        # Guardamos la información del escalar 
        probeScalarInfo = np.float64(quantityProbe.iloc[-1][probe])

        # Ahora se debe guardar esta información en la base de datos
        #       Tinlet| MFinlet | CH4Mean | COMean | ... 
        # Exp1
        # Exp2

        data[rowIndex][2 + colIndex] = probeScalarInfo

    # Ahora hacemos lo mismo, pero sólo para velocidad
    pathProbesFiles = os.path.join(pathCaseName,pathProbes,vectorFiles[0])
    # Se llama la funcin que extrae la info de cantidades vectoriales
    quantityProbe = readOpenVector(pathProbesFiles)
    # Lo guardamos directamente en la matriz
    data[rowIndex][2 + colIndex] =  np.float64( np.float64(quantityProbe.iloc[-1]["Ux_" + probe]) )


df = pd.DataFrame(data, columns=titles)
df.to_csv(nombreBaseDeDatos, index=False)
