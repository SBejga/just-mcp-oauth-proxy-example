from fastmcp import FastMCP
import random

# "Just a mcp example server with oauth"
mcp = FastMCP(name="Jameson")

@mcp.tool
def relativator(size: float, typ: str) -> str:
    """Gibt eine witzige Vergleichsbeschreibung für eine Größe zurück. Unterstützte Typen: m2 (m² / Quadratmeter), m (Meter), kg (Kilogramm), GB (Gigabyte), m3 (m³ / Kubikmeter)."""
    typ = typ.lower()

    if typ in ["m2", "m²", "meter²", "quadratmeter", "fläche", "flaeche"]:
        vergleich = size / 7140  # ca. Fläche eines Fußballfelds in m²
        return f"≈ {vergleich:.2f} Fußballfelder groß ⚽"
    
    elif typ in ["m", "meter", "länge", "laenge"]:
        vergleich = size / 1.8  # durchschnittliche Körpergröße
        objekte = ["Menschen", "Kühlschränke", "Hunde übereinander"]
        return f"≈ {vergleich:.1f} {random.choice(objekte)} übereinander 🧍"
    
    elif typ in ["kg", "kilogramm", "gewicht"]:
        vergleich = size / 5  # durchschnittliche Hauskatze ~5 kg
        objekte = ["Hauskatzen", "Waschbären", "Hühner"]
        return f"≈ {vergleich:.1f} {random.choice(objekte)} schwer 🐈"
    
    elif typ in ["daten", "datenmenge"]:
        vergleich = size * 220  # 1 GB ≈ 220 MP3-Dateien
        objekte = ["MP3-Dateien", "Urlaubsfotos", "PowerPoint-Präsentationen"]
        return f"≈ {vergleich:.0f} {random.choice(objekte)} 💾"
    
    elif typ in ["m3", "m³", "kubikmeter", "volumen"]:
        vergleich = size / 0.065  # 1 Waschmaschine ≈ 65 l = 0.065 m³
        return f"≈ {vergleich:.1f} Waschmaschinen voll 🧺"
    
    else:
        return f"🤷 Typ '{typ}' wird noch nicht unterstützt – vielleicht bald!"

if __name__ == "__main__":
    mcp.run(transport="http", port=4242)