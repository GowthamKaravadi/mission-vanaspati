"""
Add product recommendations to remedies.json
"""
import json

# Product recommendations based on disease types
PRODUCT_RECOMMENDATIONS = {
    "fungal": [
        {"name": "Copper Fungicide Spray", "type": "Fungicide", "link": "https://www.amazon.com/s?k=copper+fungicide+spray"},
        {"name": "Neem Oil Organic Fungicide", "type": "Organic Treatment", "link": "https://www.amazon.com/s?k=neem+oil+fungicide"},
        {"name": "Sulfur Fungicide Powder", "type": "Preventive", "link": "https://www.amazon.com/s?k=sulfur+fungicide"}
    ],
    "bacterial": [
        {"name": "Copper Bactericide", "type": "Bactericide", "link": "https://www.amazon.com/s?k=copper+bactericide"},
        {"name": "Plant Antibiotic Spray", "type": "Treatment", "link": "https://www.amazon.com/s?k=plant+bactericide"},
        {"name": "Pruning Shears (Sterilized)", "type": "Tool", "link": "https://www.amazon.com/s?k=pruning+shears"}
    ],
    "virus": [
        {"name": "Insecticide for Vector Control", "type": "Preventive", "link": "https://www.amazon.com/s?k=insecticide+spray"},
        {"name": "Neem Oil (Pest Control)", "type": "Organic", "link": "https://www.amazon.com/s?k=neem+oil"},
        {"name": "Row Covers", "type": "Protection", "link": "https://www.amazon.com/s?k=plant+row+covers"}
    ],
    "healthy": [
        {"name": "Balanced NPK Fertilizer", "type": "Nutrition", "link": "https://www.amazon.com/s?k=npk+fertilizer"},
        {"name": "Organic Compost", "type": "Soil Health", "link": "https://www.amazon.com/s?k=organic+compost"},
        {"name": "Plant Vitamin Supplement", "type": "Health", "link": "https://www.amazon.com/s?k=plant+vitamins"}
    ],
    "pest": [
        {"name": "Insecticidal Soap", "type": "Pest Control", "link": "https://www.amazon.com/s?k=insecticidal+soap"},
        {"name": "Neem Oil Spray", "type": "Organic Pesticide", "link": "https://www.amazon.com/s?k=neem+oil+spray"},
        {"name": "Diatomaceous Earth", "type": "Natural Pest Control", "link": "https://www.amazon.com/s?k=diatomaceous+earth"}
    ]
}

# Keywords to identify disease types
FUNGAL_KEYWORDS = ['scab', 'rust', 'mildew', 'blight', 'rot', 'spot', 'leaf_spot', 'cercospora', 'anthracnose']
BACTERIAL_KEYWORDS = ['bacterial', 'bacteria', 'canker']
VIRUS_KEYWORDS = ['virus', 'mosaic', 'curl', 'yellow']
PEST_KEYWORDS = ['mite', 'spider', 'insect', 'pest']
HEALTHY_KEYWORDS = ['healthy']

def categorize_disease(disease_name):
    """Categorize disease based on name"""
    disease_lower = disease_name.lower()
    
    if any(kw in disease_lower for kw in HEALTHY_KEYWORDS):
        return 'healthy'
    elif any(kw in disease_lower for kw in VIRUS_KEYWORDS):
        return 'virus'
    elif any(kw in disease_lower for kw in BACTERIAL_KEYWORDS):
        return 'bacterial'
    elif any(kw in disease_lower for kw in PEST_KEYWORDS):
        return 'pest'
    elif any(kw in disease_lower for kw in FUNGAL_KEYWORDS):
        return 'fungal'
    else:
        return 'fungal'  # Default to fungal

def add_products_to_remedies():
    """Add product recommendations to all diseases"""
    try:
        # Read existing remedies
        with open('remedies.json', 'r', encoding='utf-8') as f:
            remedies = json.load(f)
        
        # Add products to each disease
        count = 0
        for disease_name, disease_info in remedies.items():
            if 'products' not in disease_info:
                category = categorize_disease(disease_name)
                disease_info['products'] = PRODUCT_RECOMMENDATIONS[category]
                count += 1
        
        # Write back to file
        with open('remedies.json', 'w', encoding='utf-8') as f:
            json.dump(remedies, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully added products to {count} diseases")
        print(f"✓ Total diseases: {len(remedies)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_products_to_remedies()
