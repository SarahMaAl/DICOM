import os
import pydicom
import csv

def is_dicom_file(filename):
    """Check if the file is a DICOM file based on its extension."""
    return filename.lower().endswith('.dcm')

def extract_dicom_info(directory, output_csv):
    """
    Extracts DICOM information from all DICOM files in the given directory
    and saves the required parameters for CT-Expo calculations to a CSV file.

    Parameters:
    directory (str): Path to the directory containing DICOM files.
    output_csv (str): Path to the output CSV file.
    """
    dicom_info_list = []

    # Traverse through all files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            # Only process files with .dcm extension
            if not is_dicom_file(file):
                continue

            # Construct the full file path
            file_path = os.path.join(root, file)

            # Try to read the DICOM file
            try:
                dicom_data = pydicom.dcmread(file_path)

                # Extract relevant information from the DICOM header
                dicom_info = {
                    'PatientID': dicom_data.get('PatientID', 'Unknown'),
                    'StudyDate': dicom_data.get('StudyDate', 'Unknown'),
                    'Modality': dicom_data.get('Modality', 'Unknown'),
                    'KVP': dicom_data.get('KVP', 'Unknown'),
                    'XRayTubeCurrent': dicom_data.get('XRayTubeCurrent', 'Unknown'),
                    'ExposureTime': dicom_data.get('ExposureTime', 'Unknown'),
                    'SliceThickness': dicom_data.get('SliceThickness', 'Unknown'),
                    'Manufacturer': dicom_data.get('Manufacturer', 'Unknown')
                }

                # Add the extracted information to the list
                dicom_info_list.append(dicom_info)
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    # Save the extracted information to a CSV file if any valid DICOM files were found
    if dicom_info_list:
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=dicom_info_list[0].keys())
            writer.writeheader()
            writer.writerows(dicom_info_list)
        print(f"Extracted DICOM data has been saved to {output_csv}")
    else:
        print("No valid DICOM files were found. CSV file not created.")

def main():
    # Directory containing DICOM files
    dicom_directory = 'D:/DQPRM_TD_PROMO_24_26/Defez_TD/E'
    # Path to save the output CSV file
    output_csv = 'D:/DQPRM_TD_PROMO_24_26/Defez_TD/E/dicom_parameters_for_ct_expo.csv'

    # Extract DICOM information and save to CSV
    extract_dicom_info(dicom_directory, output_csv)

if __name__ == '__main__':
    main()
