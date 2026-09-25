from fpdf import FPDF
from datetime import datetime
from db import get_stats, get_observations, get_station_detail
from biodiversity import shannon_index, compute_shannon_time_series
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
    # 1. Raccolta Dati Completa
    try:
        if station_id:
            detail = await get_station_detail(station_id)
            if not detail:
                raise Exception(f"Stazione {station_id} non trovata")
            
            stats = detail["stats"]
            species_list = detail["species"]
            observations = await get_observations(station_id=station_id, limit=1000)
            station_name = detail["station"].get("name", station_id)
            filters = {"station_id": station_id, "method": None, "start": None, "end": None}
        else:
            stats = await get_stats()
            observations = await get_observations(limit=1000)
            station_name = "Tutte le stazioni"
            
            species_counts = {}
            for obs in observations:
                sp = obs.get("species")
                if sp:
                    species_counts[sp] = species_counts.get(sp, 0) + 1
            species_list = [{"species": sp, "count": cnt} for sp, cnt in species_counts.items()]
            filters = {"station_id": None, "method": None, "start": None, "end": None}

    except Exception as e:
        raise Exception(f"Errore nel recupero dati: {str(e)}")

    if not stats:
        raise Exception("Impossibile recuperare le statistiche dal database")

    # Indice di Shannon globale
    shannon_val = stats.get("shannon_index", 0.0) if station_id else shannon_index(stats.get("observations", []))
    
    # Dati Time Series (Andamento Shannon)
    time_series = await compute_shannon_time_series(interval="month", filters=filters)
    
    pdf = BiodiversityReport()
    pdf.add_page()
    
    # --- SEZIONE 1: Riepilogo Generale (Stats Card) ---
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Riepilogo Generale", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, f"Stazione: {station_name}", ln=True)
    pdf.cell(0, 8, f"Osservazioni Totali: {stats.get('total_observations', stats.get('total', 0))}", ln=True)
    pdf.cell(0, 8, f"Specie Individuate: {stats.get('species_count', 0)}", ln=True)
    pdf.cell(0, 8, f"Indice di Biodiversità (Shannon): {shannon_val:.2f}", ln=True)
    pdf.ln(10)
    
    # --- SEZIONE 2: Andamento Temporale (Sostituisce il grafico Shannon Line Chart) ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Andamento Indice di Shannon (Mensile)", ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(60, 8, "Mese", border=1, fill=True)
    pdf.cell(40, 8, "Valore Shannon", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    if time_series:
        for entry in time_series[-12:]: # Ultimi 12 mesi
            pdf.cell(60, 8, entry.get("date", "N/A"), border=1)
            pdf.cell(40, 8, f"{entry.get('value', 0.0):.2f}", border=1)
            pdf.ln()
    else:
        pdf.cell(0, 10, "Nessun dato temporale disponibile.", ln=True)
    pdf.ln(10)
    
    # --- SEZIONE 3: Distribuzione Specie (Species Distribution Chart) ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Distribuzione Specie", ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(120, 8, "Specie", border=1, fill=True)
    pdf.cell(40, 8, "Conteggio", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    sorted_species = sorted(species_list, key=lambda x: x["count"], reverse=True)
    for sp in sorted_species[:20]:
        if pdf.get_y() > 270:
            pdf.add_page()
        pdf.cell(120, 8, str(sp.get("species", "N/A")), border=1)
        pdf.cell(40, 8, str(sp.get("count", 0)), border=1)
        pdf.ln()
    
    if len(sorted_species) > 20:
        pdf.set_font("helvetica", "I", 8)
        pdf.cell(0, 8, f"... e altre {len(sorted_species)-20} specie.", ln=True)
    
    pdf.ln(10)
    
    # --- SEZIONE 4: Dettaglio Osservazioni (Observation List) ---
    if pdf.get_y() > 200:
        pdf.add_page()

    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Dettaglio Osservazioni Recenti", ln=True)
    pdf.ln(2)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(60, 8, "Specie", border=1, fill=True)
    pdf.cell(30, 8, "Metodo", border=1, fill=True)
    pdf.cell(30, 8, "Confidenza", border=1, fill=True)
    pdf.cell(40, 8, "Data", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    if observations:
        for obs in observations[:50]:
            species = str(obs.get("species", "N/A"))
            method = str(obs.get("method", "N/A"))
            confidence = obs.get('confidence', 0)
            dt = obs.get("date_time")
            date_str = dt[:10] if dt and isinstance(dt, str) else "N/A"
            
            if pdf.get_y() > 270:
                pdf.add_page()
                pdf.set_fill_color(230, 230, 230)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(60, 8, "Specie", border=1, fill=True)
                pdf.cell(30, 8, "Metodo", border=1, fill=True)
                pdf.cell(30, 8, "Confidenza", border=1, fill=True)
                pdf.cell(40, 8, "Data", border=1, fill=True)
                pdf.ln()
                pdf.set_font("helvetica", "", 10)

            pdf.cell(60, 8, species, border=1)
            pdf.cell(30, 8, method, border=1)
            pdf.cell(30, 8, f"{float(confidence*100):.1f}%", border=1)
            pdf.cell(40, 8, date_str, border=1)
            pdf.ln()
    else:
        pdf.cell(0, 10, "Nessuna osservazione trovata.", ln=True)
        
    return pdf.output()
