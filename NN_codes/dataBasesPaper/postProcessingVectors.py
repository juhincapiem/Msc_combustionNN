import pandas as pd
import re

def readOpenVector(filePath):
    with open(filePath, "r") as probeFile:
        probe_lines = []
        data_start = 0  # Line index where numerical data starts

        # Step 1: Read file, capture comments and find data start
        for i, line in enumerate(probeFile):
            if line.startswith("#"):
                probe_lines.append(line.strip())
            else:
                data_start = i  # First non-# line (numerical data starts here)
                break  # Stop once we reach data

    # Step 2: Extract probe numbers (Optional, based on '# Probe' lines)
    probes = [line.split()[2] for line in probe_lines[:-1]]

    # Step 3: Define column names
    raw_column_names = probe_lines[-1].split()[1:]  # Skip '#'
    num_probes = len(raw_column_names) - 1  # subtract 'Time'
    
    # Define column names explicitly
    column_names = ['Time']
    for i in range(num_probes):
        column_names.extend([f'Ux_{i}', f'Uy_{i}', f'Uz_{i}'])

    # Step 4: Now load the actual data
    data = []

    with open(filePath, "r") as probeFile:
        lines = probeFile.readlines()[data_start:]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Split the line into Time and the vector part
            tokens = re.split(r'\s+', line, maxsplit=1)
            time = float(tokens[0])
            vectors = re.findall(r'\(([^)]+)\)', tokens[1])

            if len(vectors) != num_probes:
                raise ValueError(f"Expected {num_probes} vectors, found {len(vectors)}.")

            flat_values = []
            for v in vectors:
                ux, uy, uz = map(float, v.split())
                flat_values.extend([ux, uy, uz])

            row = [time] + flat_values
            data.append(row)

    # Step 5: Create DataFrame
    df = pd.DataFrame(data, columns=column_names)
    
    return df
