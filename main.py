from fastmcp import FastMCP
import random

# "Just a mcp example server with oauth"
mcp = FastMCP(name="Jameson")

@mcp.tool
def relativator(size: float, typ: str) -> str:
    """Returns a funny comparative description for a size. Supported types: m2 (m² / square meters), m (meters), kg (kilograms), GB (gigabytes), m3 (m³ / cubic meters). Default language is German, but accepts English inputs as well."""
    typ = typ.lower()

    if typ in ["m2", "m²", "meter²", "quadratmeter", "fläche", "flaeche", "square meters", "area"]:
        comparison = size / 7140  # approx. area of a soccer field in m²
        return f"≈ {comparison:.2f} soccer fields large ⚽"
    
    elif typ in ["m", "meter", "länge", "laenge", "length"]:
        comparison = size / 1.8  # average human height
        objects = ["people", "refrigerators", "dogs stacked on top of each other"]
        return f"≈ {comparison:.1f} {random.choice(objects)} stacked on top of each other 🧍"
    
    elif typ in ["kg", "kilogramm", "gewicht", "weight"]:
        comparison = size / 5  # average house cat ~5 kg
        objects = ["house cats", "raccoons", "chickens"]
        return f"≈ {comparison:.1f} {random.choice(objects)} heavy 🐈"
    
    elif typ in ["gb", "gigabyte", "daten", "datenmenge", "data"]:
        comparison = size * 220  # 1 GB ≈ 220 MP3 files
        objects = ["MP3 files"]
        return f"≈ {comparison:.0f} {random.choice(objects)} 💾"
    
    elif typ in ["m3", "m³", "kubikmeter", "volumen", "cubic meters", "volume"]:
        comparison = size / 0.065  # 1 washing machine ≈ 65 l = 0.065 m³
        return f"≈ {comparison:.1f} washing machines full 🧺"
    
    else:
        return f"🤷 Type '{typ}' is not yet supported – maybe soon!"

if __name__ == "__main__":
    mcp.run(transport="http", port=4242)