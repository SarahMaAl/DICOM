"""
DICOM Scoutview Modulation Visualization Script

Author: Sarah MARTIN-ALONSO
License: MIT
Date: 2024-11-27

Description:
This script processes DICOM files to identify scout views and extract intensity
modulation data (mAs) for CT slices. It visualizes the scout view alongside
the intensity modulation curve to provide insight into scanning parameters.

Features:
- Identifies scout view DICOM files based on their metadata.
- Extracts Z positions and mAs values from DICOM slice files.
- Plots scout views with intensity modulation profiles.

Requirements:
- pydicom
- matplotlib
- numpy
- tkinter
"""

import os
import tkinter as tk
from tkinter import filedialog
from typing import List, Tuple
import pydicom
import matplotlib.pyplot as plt
import numpy as np


def is_scout(ds: pydicom.dataset.FileDataset) -> bool:
    """
    Checks if the DICOM file corresponds to a scout view based on Series Description.

    Args:
        ds (pydicom.dataset.FileDataset): The DICOM dataset.

    Returns:
        bool: True if the file is identified as a scout view, False otherwise.
    """
    try:
        series_description = ds.SeriesDescription.lower()
        return "scout face" in series_description or "profil" in series_description
    except AttributeError:
        return False


def load_scoutview(file_path: str) -> Tuple[np.ndarray, pydicom.dataset.FileDataset]:
    """
    Loads the scout view image and metadata from a DICOM file.

    Args:
        file_path (str): Path to the DICOM file.

    Returns:
        Tuple[np.ndarray, pydicom.dataset.FileDataset]: The image array and DICOM dataset.

    Raises:
        ValueError: If the file is not identified as a scout view.
    """
    ds = pydicom.dcmread(file_path)
    if not is_scout(ds):
        raise ValueError(f"The file {file_path} is not identified as a scout view.")
    return ds.pixel_array, ds


def extract_dicom_data(dicom_files: List[str]) -> List[Tuple[float, float]]:
    """
    Extracts Z positions and mAs values from DICOM slice files.

    Args:
        dicom_files (List[str]): List of DICOM file paths.

    Returns:
        List[Tuple[float, float]]: Sorted list of (Z position, mAs value).
    """
    data = []
    current_position = None

    for file in dicom_files:
        ds = pydicom.dcmread(file)

        if is_scout(ds):
            continue

        slice_thickness = float(ds.SliceThickness)
        spacing_between_slices = float(getattr(ds, "SpacingBetweenSlices", slice_thickness))

        if current_position is None:
            current_position = float(ds.ImagePositionPatient[2])
        else:
            current_position -= slice_thickness

        mAs = float(ds.XRayTubeCurrent * ds.RevolutionTime)
        data.append((current_position, mAs))

    return sorted(data, key=lambda x: x[0])[::-1]


def calculate_scout_positions(scout_ds: pydicom.dataset.FileDataset) -> Tuple[float, float, float]:
    """
    Calculates the Z positions and corrected spacing for the scout view.

    Args:
        scout_ds (pydicom.dataset.FileDataset): The scout view DICOM dataset.

    Returns:
        Tuple[float, float, float]: (Start Z, End Z, Corrected spacing).
    """
    scout_length = float(scout_ds.SliceThickness)
    z_start = float(scout_ds.ImagePositionPatient[2])
    z_end = z_start - scout_length
    rows = scout_ds.Rows
    z_spacing_corrected = scout_length / rows
    return z_start, z_end, z_spacing_corrected


def plot_scoutview_with_modulation(scoutview: np.ndarray, scout_ds: pydicom.dataset.FileDataset,
                                   intensity_data: List[Tuple[float, float]]) -> None:
    """
    Plots the scout view with intensity modulation (mAs) curve.

    Args:
        scoutview (np.ndarray): The scout view image array.
        scout_ds (pydicom.dataset.FileDataset): The scout view DICOM dataset.
        intensity_data (List[Tuple[float, float]]): Intensity modulation data as (Z position, mAs).
    """
    z_start, z_end, z_spacing = calculate_scout_positions(scout_ds)
    cols = scoutview.shape[1]
    x_spacing = float(scout_ds.PixelSpacing[1])

    scoutview_rotated = np.rot90(scoutview)
    extent = [z_start, z_end, 0, cols * x_spacing]

    positions, intensities = zip(*intensity_data)

    plt.figure(figsize=(12, 8))
    plt.imshow(scoutview_rotated, cmap='gray', aspect='auto', extent=extent)
    plt.plot(positions, intensities, color='red', linewidth=2, label="Intensity Modulation (mAs)")
    plt.xlabel("Z Position (mm)")
    plt.ylabel("Intensity (mAs)")
    plt.title("Scout View with Intensity Modulation Curve")
    plt.legend()
    plt.grid()
    plt.show()


def main() -> None:
    """
    Main function to execute the script logic.
    """
    root = tk.Tk()
    root.withdraw()
    dicom_folder = filedialog.askdirectory(title="Select the folder containing DICOM files")

    if not dicom_folder:
        raise FileNotFoundError("No folder selected.")

    dicom_files = [os.path.join(dicom_folder, f) for f in os.listdir(dicom_folder) if f.endswith(".dcm")]

    scout_files = [file for file in dicom_files if is_scout(pydicom.dcmread(file))]

    if not scout_files:
        raise FileNotFoundError("No scout files found in the folder.")

    scoutviews = []
    scout_dses = []
    for scout_file in scout_files:
        scoutview, scout_ds = load_scoutview(scout_file)
        scoutviews.append(scoutview)
        scout_dses.append(scout_ds)

    intensity_data = extract_dicom_data(dicom_files)

    for scoutview, scout_ds in zip(scoutviews, scout_dses):
        plot_scoutview_with_modulation(scoutview, scout_ds, intensity_data)


if __name__ == "__main__":
    main()
