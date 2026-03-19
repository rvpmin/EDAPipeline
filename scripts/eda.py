import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
from fpdf import FPDF

def load_data(path):
    if path.endswith('.xlsx'):
        return pd.read_excel(path)
    elif path.endswith('.csv'):
        return pd.read_csv(path)
    else:
        raise ValueError("Formato no soportado")

def create_dirs():
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/images", exist_ok=True)

def data_types(df):
    return df.dtypes.astype(str)

def missing_data(df):
    return df.isnull().sum()

def plot_distributions(df):
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    for col in num_cols:
        plt.figure()
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f"Distribución de {col}")
        plt.savefig(f"out/images/dist_{col}.png")
        plt.close()

def plot_correlations(df):
    num_df = df.select_dtypes(include=['int64', 'float64'])
    if len(num_df.columns) > 1:
        plt.figure(figsize=(8,6))
        sns.heatmap(num_df.corr(), annot=True, cmap="coolwarm")
        plt.title("Matriz de correlación")
        plt.savefig("out/images/corr.png")
        plt.close()

def plot_outliers(df):
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    for col in num_cols:
        plt.figure()
        sns.boxplot(x=df[col])
        plt.title(f"Outliers en {col}")
        plt.savefig(f"out/images/box_{col}.png")
        plt.close()

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte EDA", 0, 1, "C")

def generate_pdf(df, types, missing):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 10, "Tipos de datos:", 0, 1)
    for col, t in types.items():
        pdf.cell(0, 8, f"{col}: {t}", 0, 1)

    pdf.ln(5)
    pdf.cell(0, 10, "Datos faltantes:", 0, 1)
    for col, m in missing.items():
        pdf.cell(0, 8, f"{col}: {m}", 0, 1)

    # Imágenes
    for img in os.listdir("out/images"):
        pdf.add_page()
        pdf.image(f"out/images/{img}", x=10, y=20, w=180)

    pdf.output("out/Reporte.pdf")

def main(input_path):
    create_dirs()
    df = load_data(input_path)

    types = data_types(df)
    missing = missing_data(df)

    plot_distributions(df)
    plot_correlations(df)
    plot_outliers(df)

    generate_pdf(df, types, missing)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Ruta del archivo")
    args = parser.parse_args()

    main(args.input)