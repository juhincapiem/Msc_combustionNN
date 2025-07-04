# -*- coding: utf-8 -*-
"""
@author: davdl
"""

import os
import glob
import pandas as pd
import numpy as np
from solvers.tools import df2Xy, trainStats, plotLossStats, plot_stride, plot_error, model_prediction, plot_pareto

# Obtener el directorio actual
path = os.getcwd()
study_folder = 'epochs_1000-trials_100'

# Usando glob para obtener todos los archivos .parquet en el directorio actual
parquet_files = glob.glob(os.path.join(path,study_folder, "*.parquet"))

name, activation, nLayers, nNeurons, epochList, lossList, lossICList, lossBCList, lossPhysicsList, loss, lossIC, lossBC, lossPhysics, time_optimizer, time_profiler, flops  = trainStats(parquet_files)

plotLossStats(epochList,lossList)

index = np.argsort(loss)

plot_pareto(loss,time_optimizer,activation)

print(f'La arquitectura escogida es {name[index][0]} con un loss = {loss[index][0]}')
#------------------------------------------
df_analytical = pd.read_parquet('Numerical/solutions/Analytical_nx57_dt0.001_t5.000_Pe40.000.parquet')

X, y_analytical = df2Xy(df_analytical)

y_analytical = y_analytical[X[:,0]<=1.0]
X = X[X[:,0]<=1.0,:]

modelPath = os.path.join(path, study_folder,name[index][0]+'.pth')

y_pred = model_prediction(X, modelPath)

plot_stride(X, [y_analytical,y_pred], ['Analytical', 'NN'], nPlotStride=5)

plot_error(X, [y_analytical,y_pred], ['NN'])

# index_best_activation = activation[index] == activation[index][0]
# neurons_best_activation = nNeurons[index][index_best_activation]
# layers_best_activation = nLayers[index][index_best_activation]
# total_neurons_best_activation = neurons_best_activation*layers_best_activation
# loss_best_activation = loss[index][index_best_activation]
# layers_unique = np.unique(layers_best_activation)

# plt.figure()
# plt.scatter(neurons_best_activation,loss_best_activation)
# plt.xlabel(r'$Neurons$')
# plt.ylabel(r'$Loss$')

# plt.figure()
# plt.scatter(layers_best_activation,loss_best_activation)
# plt.xlabel(r'$Layers$')
# plt.ylabel(r'$Loss$')

# plt.figure()
# markers = ['o', 's', '^', 'D', 'v', 'P', '*', 'X']
# for i in range(len(layers_unique)):
#     plt.scatter(total_neurons_best_activation[layers_best_activation==layers_unique[i]],loss_best_activation[layers_best_activation==layers_unique[i]],label=f'Layers = {layers_unique[i]:.0f}',marker=markers[i])
# plt.xlabel(r'$Total$ $Neurons$')
# plt.ylabel(r'$Loss$')
# plt.legend(loc='upper left', bbox_to_anchor=(1, 1))