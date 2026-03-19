import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
from fpdf import FPDF
from datetime import datetime


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

def descriptive_stats(df):
    return df.describe()


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
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

def add_cover(pdf):
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "Reporte de Análisis Exploratorio de Datos", 0, 1, "C")

    pdf.ln(10)
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "Registro Nacional de Cáncer", 0, 1, "C")

    pdf.ln(20)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Autor: Roxana Pérez", 0, 1, "C")
    pdf.cell(0, 10, f"Fecha: {datetime.today().strftime('%Y-%m-%d')}", 0, 1, "C")

def add_section_title(pdf, title):
    pdf.set_font("Arial", "B", 14)
    pdf.ln(5)
    pdf.cell(0, 10, title, 0, 1)

def add_text_block(pdf, text):
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, text)

def add_table(pdf, data, col1="Columna", col2="Valor"):
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, col1, 1)
    pdf.cell(90, 8, col2, 1)
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for key, value in data.items():
        pdf.cell(90, 8, str(key), 1)
        pdf.cell(90, 8, str(value), 1)
        pdf.ln()

def add_image_section(pdf, title, image_paths):
    if not image_paths:
        return

    pdf.add_page()
    add_section_title(pdf, title)

    for img in image_paths:
        pdf.add_page()
        pdf.image(img, x=10, y=30, w=180)


def generate_pdf(df, types, missing):
    pdf = PDF()


    add_cover(pdf)

    pdf.add_page()

    add_section_title(pdf, "Resumen General")
    add_text_block(pdf, f"El dataset contiene {df.shape[0]} filas y {df.shape[1]} columnas.")

    # Data tyypes
    add_section_title(pdf, "Tipos de Datos")
    add_table(pdf, types)

    # Missing
    add_section_title(pdf, "Datos Faltantes")
    missing_percent = (missing / len(df)) * 100
    missing_info = {
        col: f"{missing[col]} ({missing_percent[col]:.2f}%)"
        for col in missing.index
    }
    add_table(pdf, missing_info)


    add_section_title(pdf, "Estadísticas Descriptivas")
    desc = df.describe().to_dict()

    for col, stats in desc.items():
        add_text_block(pdf, f"\n{col}")
        for k, v in stats.items():
            pdf.cell(0, 8, f"{k}: {v:.2f}", 0, 1)



    images = os.listdir("out/images")

    dist_imgs = [f"out/images/{f}" for f in images if f.startswith("dist")]
    box_imgs = [f"out/images/{f}" for f in images if f.startswith("box")]
    corr_imgs = [f"out/images/corr.png"] if "corr.png" in images else []

    add_image_section(pdf, "Distribuciones", dist_imgs)
    add_image_section(pdf, "Outliers", box_imgs)
    add_image_section(pdf, "Correlaciones", corr_imgs)

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