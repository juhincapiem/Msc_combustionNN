from postProcesingScalars import readProbeScalar
from postProcessingVectors import readOpenVector
import numpy as np
import pandas as pd
from scipy import integrate
import cantera as ct
import os
import sys


# Indico los valores de temeperatura y flujo másico de combustible
temperatures = np.arange(700, 1275, 25)      # Temperatura, [K] 
massFlowRates = np.arange(0.04, 0.12, 0.01)  # flujo másico de combustible, [kg/s]

probes_dir = os.path.join('probes','0')
information_files = ["CH4Mean","CO2Mean","COMean","H2OMean","N2Mean","O2Mean","TMean"]
vector_files = ["UMean"]
numProbes = 9
positionY = np.array([2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0])

# Creamos los títulos de la base de datos
titles = ["T_inlet", "MFR_inlet"] + information_files + vector_files + ["MFR_outlet", "fuelEfficiency","EI_CH4","EI_CO2","EI_CO"]

# Calculamos el tamaño de la base de datos
rows = len(temperatures) * len(massFlowRates)
cols = len(titles)

data = np.zeros((rows,cols))

# Mixture
# Define gas mixture
gas1 = ct.Solution('gri30.yaml')
gas2 = ct.Solution('gri30.yaml')
gas = ct.Solution('gri30.yaml')

#gas.Y = {'O2': 0.050053744, 'N2': 0.6768730341472677, 'CH4': 0.006456563062257956, 'CO': 0.0004, 'CO2':0.19059414630775642, 'H2O':0.07562251242652673}  # Example mass fractions
gas.Y = np.zeros(53)
gas1.Y = np.zeros(53)
gas2.Y = np.zeros(53)

# Área a la salida del incinerador
areaOutlet = 0.8*1 # m2

# Con estos ciclos se puede obtener los nombres de todos los archivos
for countTemp, temp in enumerate(temperatures):
    for countMFR, mfr in enumerate(massFlowRates):
            # Creamos el nombre del directorio
            case_name = f"experiment_T{temp:.2f}_mfr{mfr:.2f}"
            case_name = os.path.join(".",case_name)
            # Juntamos la dirección del directorio madres, con los directorios
            # donde se encuentra la información de las probetas
            source_path = os.path.join(case_name, probes_dir)

            # Nos inventamos un mapeo para llenar la base de datos
            rowIndex = countTemp*5 + countMFR
            # Ingreso los valores de temperatura y flujo másico de combustible a la entrada
            data[rowIndex][0] = temp
            data[rowIndex][1] = mfr

            # Set reactants state
            gas1.TPX = temp, 76000, "CH4:1, O2:1.5"
            gas2.TPX = temp, 76000, "CO:1, O2:0.5"

            h1_gas1 = gas1.enthalpy_mass
            h1_gas2 = gas2.enthalpy_mass

            Y_CH4_gas1 = gas1["CH4"].Y[0]  # returns an array, of which we only want the first element
            Y_CO_gas2 = gas2["CO"].Y[0]  # returns an array, of which we only want the first element

            gas1.TPX = None, None, "CO:1, H2O:2"
            gas2.TPX = None, None, "CO2:1"


            h2_gas1 = gas1.enthalpy_mass
            h2_gas2 = gas2.enthalpy_mass

            LHV_gas1 = -(h2_gas1 - h1_gas1) / Y_CH4_gas1
            LHV_gas2 = -(h2_gas2 - h1_gas2) / Y_CO_gas2 

            LHV_total = LHV_gas1 + LHV_gas2 # J/kg

            # Ciclo for para recorrer cada uno de los archivos, y llevar a cabo
            # una integración numérica con respecto al espacio
            for countInfo, information in enumerate(information_files):
                  # Re-acomodamos el source path
                  information_path = os.path.join(source_path, information)
                  # Usamos la función "readProbeScalar" para obtener los datos 
                  # registrados por Probes
                  quantityProbeDF = readProbeScalar(information_path)
                  # Guardamos el último tiempo
                  tiempo = np.float64(quantityProbeDF.iloc[-1]['Time'])
                  # Iteramos sobre toda las probetas que estaban ubicadas al 
                  # final del incinerador
                  quantityExit = np.array([np.float64(quantityProbeDF.iloc[-1][str(i)]) for i in range(numProbes)])
                  # Tenemos que usar algún algorítmo de integración numérica
                  quantityAverageExit = integrate.simps(quantityExit, x=positionY)/(positionY[-1] - positionY[0])
                  # Ahora se debe guardar esta información en la base de datos
                  #       Tinlet| MFinlet | CH4Mean | COMean | ... 
                  # Exp1
                  # Exp2
                  data[rowIndex][2 + countInfo] = quantityAverageExit

            # Ahora hacemos lo mismo, pero sólo para velocidad
            information_path = os.path.join(source_path, "UMean")
            velocity = readOpenVector(information_path)
            # Iteramos sobre toda las probetas que estaban ubicadas al 
            # final del incinerador
            velocityExit = np.array([np.float64(velocity.iloc[-1]["Ux_" + str(i)]) for i in range(numProbes)])
            velocityAverageExit = integrate.simps(velocityExit, x=positionY)/(positionY[-1] - positionY[0])
            velocityAverageExit = -1*velocityAverageExit   # Le cambiamos el signos. Ya sabemos que está saliendo
            data[rowIndex][9] = velocityAverageExit

            # Con los valores promediados a la salida, hacemos otra mezcla de gases y calculamos la densidad
            gas.Y = {'O2': data[rowIndex][7], 'N2': data[rowIndex][6], 'CH4': data[rowIndex][2], 'CO': data[rowIndex][4], 'CO2':data[rowIndex][3], 'H2O':data[rowIndex][5]}  # Example mass fractions
            gas.TP = data[rowIndex][8], 76000  # Temperature (K) and Pressure (Pa)

            # Se calcula el flujo másico a la salida del incinerador y se guarda en la base de datos
            massFROutlet = gas.density * areaOutlet * velocityAverageExit
            data[rowIndex][10] = massFROutlet

            # Calculemos la eficiencia de la combustión
            #gas.Y = {'CH4': data[rowIndex][2], 'CO': data[rowIndex][4]}  # Example mass fractions
            hGasOutlet = abs(gas.enthalpy_mass)

            eficiency = 1 - massFROutlet*hGasOutlet/(mfr*LHV_total)


            # Llenamos los espacios reservados para las métricas de eficiencia y de emisiones
            denominador = data[rowIndex][2] + data[rowIndex][4] + data[rowIndex][3]
            data[rowIndex][-4] = eficiency   # Eficiencia de combustible
            data[rowIndex][-3] = data[rowIndex][2]/denominador    # EI CH4
            data[rowIndex][-2] = data[rowIndex][3]/denominador   # EI CO2
            data[rowIndex][-1] = data[rowIndex][4]/denominador   # EI CO
        
df = pd.DataFrame(data, columns=titles)
df.to_csv('baseDeDatos.csv', index=False)


                  







