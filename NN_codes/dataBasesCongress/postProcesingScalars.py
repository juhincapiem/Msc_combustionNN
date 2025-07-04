import numpy as np
import pandas as pd


def readProbeScalar(filePath):
    with open(filePath,"r") as probeFile:
        
        probe_lines = []
        data_start = 0  # Line index where numerical data starts

        # Step 1: Count probe lines and extract probe numbers
        for i, line in enumerate(probeFile):
            if line.startswith("#"):
                probe_lines.append(line.strip())
            else:
                data_start = i  # First non-# line (numerical data starts here)
                break  # Stop reading once we reach data

    # Extract probe numbers from comments
    probes = [line.split()[2] for line in probe_lines[:-1]]

    # Define column names (first column is "time")
    column_names = probe_lines[-1].split()[1:]

    # Read numerical data using Pandas
    df = pd.read_csv(
        filePath, 
        comment="#",  # Ignore lines starting with #
        delim_whitespace=True,  # Handle space-separated values
        names=column_names,
        skiprows=len(probe_lines)  # Skip probe info lines
    )

    # Replace invalid values
    df.replace(-1e+300, float("nan"), inplace=True)
    df.to_numpy()

    return df
