import optuna
import torch
import os
import pandas as pd
from PINN_Class import PINN
from solvers.tools import df2Xy, Xy2tensor

max_epochs = 1000
n_trials = 100

study_name = f"epochs_{max_epochs}-trials_{n_trials}"
os.makedirs(study_name, exist_ok=True)

# Cargar datos una sola vez
df = pd.read_parquet("solutions/Analytical_nx57_dt0.001.parquet")
# df = pd.read_parquet('/home/dldiazl/Congreso/solutions/Analytical_nx57_dt0.001.parquet')

X_np, y_np = df2Xy(df)

X, y = Xy2tensor(X_np, y_np)


def objective(trial):
    # Definir espacio de búsqueda
    num_layers = trial.suggest_int("num_layers", 3, 10)
    neurons_per_layer = trial.suggest_int("neurons_per_layer", 10, 100, step=5)
    # neurons_per_layer = [trial.suggest_int(f"neurons_l{i}", 10, 100, step=10) for i in range(num_layers)]
    activation = trial.suggest_categorical("activation", ["relu", "tanh", "sigmoid"])
    
    # Construcción de la arquitectura
    layers = [2] + [neurons_per_layer] * num_layers + [1]
    # layers = [2] + neurons_per_layer + [1]
    print(layers, activation)
    # Instanciar y entrenar el modelo
    model = PINN(layers, activation, max_epochs=max_epochs).double()
    model.train(X, y)
    
    total_time_optimizer = float(model.history['Time_optimizer'].sum())
    total_time_cpu = float(model.history['Time_cpu'].sum())
    flops = int(model.history['Flops'].sum())
    name = f'{num_layers}x{neurons_per_layer}_{activation}'
    # name = f'{"x".join(map(str, neurons_per_layer))}_{activation}'
    model.history.to_parquet(f'./{study_name}/{name}.parquet', index=False)
    torch.save(model,f'./{study_name}/{name}.pth')
    print(f'Loss: {model.loss}, FLOPS:{flops}, Tiempo optimizador = {total_time_optimizer}, Tiempo CPU = {total_time_cpu}')
    
    return model.loss, total_time_optimizer  # Optuna intenta minimizar esta pérdida

# Crear/cargar estudio y optimizar
study = optuna.create_study(directions=["minimize", "minimize"], study_name=study_name)
study.optimize(objective, n_trials=n_trials)

print("Mejores configuraciones encontradas:")
for trial in study.best_trials:
    print(trial.params)