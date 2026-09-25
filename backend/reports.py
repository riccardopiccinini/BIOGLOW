from fpdf import FPDF
from datetime import datetime
from db import get_stats, get_observations
import asyncio

class BiodiversityReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(45, 106, 79) # Verde primario
        self.cell(0, 10, "Monitor Secchia - Report Biodiversità", ln=True, align="C")
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

async def generate_summary_pdf(station_id=None):
    # 1. Raccolta Dati
    stats = await get_stats(station_id=station_id)
    observations = await get_observations(station_id=station_id, limit=1000)
    
    pdf = BiodiversityReport()
    pdf.add_page()
    
    # Titolo Sezione
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Riepilogo Generale", ln=True)
    pdf.ln(5)
    
    # Stats Box
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Stazione: {station_id if station_id else 'Tutte le stazioni'}", ln=True)
    pdf.cell(0, 8, f"Osservazioni Totali: {stats['total']}", ln=True)
    pdf.cell(0, 8, f"Specie Individuate: {stats['species_count']}", ln=True)
    pdf.cell(0, 8, f"Indice di Biodiversità (Shannon): {stats['shannon_index']:.2f}", ln=True)
    pdf.ln(10)
    
    # Tabella Osservazioni
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Dettaglio Osservazioni", ln=True)
    pdf.ln(2)
    
    # Header Tabella
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(60, 8, "Specie", border=1, fill=True)
    pdf.cell(30, 8, "Metodo", border=1, fill=True)
    pdf.cell(30, 8, "Confidenza", border=1, fill=True)
    pdf.cell(40, 8, "Data", border=1, fill=True)
    pdf.ln()
    
    # Righe Tabella
    pdf.set_font("helvetica", "", 10)
    for obs in observations:
        pdf.cell(60, 8, str(obs.get("species", "N/A")), border=1)
        pdf.cell(30, 8, str(obs.get("method", "N/A")), border=1)
        pdf.cell(30, 8, f"{float(obs.get('confidence', 0)*100):.1f}%", border=1)
        pdf.cell(40, 8, str(obs.get("date_time", "N/A")[:10]), border=1)
        pdf.ln()
        
    return pdf.output()
