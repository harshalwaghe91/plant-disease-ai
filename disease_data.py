# disease_data.py
# Central knowledge base for all plant diseases
# Add new diseases here without changing any other file

DISEASE_DATABASE = {
    "Healthy": {
        "display_name": "Healthy Plant",
        "plant": "General",
        "description": "The plant appears healthy with no visible signs of disease or infection.",
        "symptoms": ["Green, vibrant leaves", "No spots or lesions", "Normal growth pattern"],
        "causes": ["Good growing conditions", "Proper nutrition", "Adequate watering"],
        "severity": "None",
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular care: proper watering, fertilization, and sunlight.",
        "prevention": [
            "Maintain proper soil nutrition",
            "Water at the base of the plant",
            "Ensure good air circulation",
            "Rotate crops annually"
        ],
        "color": "#28a745"
    },

    "Tomato_Early_Blight": {
        "display_name": "Tomato Early Blight",
        "plant": "Tomato",
        "description": "Early blight is a common fungal disease of tomatoes caused by Alternaria solani. It affects leaves, stems, and fruits, reducing yield significantly.",
        "symptoms": [
            "Dark brown to black spots with concentric rings (target-board pattern)",
            "Yellow halo surrounding the spots",
            "Spots appear first on older lower leaves",
            "Premature defoliation in severe cases",
            "Dark lesions on stems near soil line"
        ],
        "causes": [
            "Fungus: Alternaria solani",
            "Warm temperatures (24–29°C)",
            "High humidity and wet conditions",
            "Poor air circulation",
            "Plant stress from drought or nutrient deficiency"
        ],
        "severity": "Moderate",
        "chemical_treatment": "Apply Chlorothalonil (Daconil) or Mancozeb fungicide every 7–10 days. Use Copper-based fungicides as an alternative. Follow label instructions carefully.",
        "organic_treatment": "Spray Neem Oil (2%) solution every 7 days. Apply Copper Soap Fungicide. Use Bacillus subtilis biofungicide. Remove and destroy infected leaves immediately.",
        "prevention": [
            "Practice crop rotation (3-year cycle)",
            "Use certified disease-free seeds",
            "Stake plants for better air circulation",
            "Mulch soil to prevent spore splash",
            "Water at the base, avoid wetting foliage",
            "Remove plant debris after harvest"
        ],
        "color": "#fd7e14"
    },

    "Tomato_Late_Blight": {
        "display_name": "Tomato Late Blight",
        "plant": "Tomato",
        "description": "Late blight is a devastating disease caused by Phytophthora infestans — the same pathogen that caused the Irish Potato Famine. It can destroy entire crops within days under favorable conditions.",
        "symptoms": [
            "Water-soaked, pale green or olive-green spots on leaves",
            "White fuzzy mold on leaf undersides",
            "Brown-black lesions on stems",
            "Firm brown rot on green or ripe fruits",
            "Rapid wilting and crop collapse in humid conditions"
        ],
        "causes": [
            "Oomycete: Phytophthora infestans",
            "Cool temperatures (10–20°C) with high humidity",
            "Prolonged leaf wetness",
            "Infected seed potatoes or transplants",
            "Wind-borne spores from nearby infected crops"
        ],
        "severity": "High",
        "chemical_treatment": "Apply Ridomil Gold (Metalaxyl + Mancozeb) or Cymoxanil fungicide. Preventive sprays with Chlorothalonil every 5–7 days during wet weather. Systemic fungicides like Dimethomorph are also effective.",
        "organic_treatment": "Copper hydroxide (Kocide) sprays preventively. Bordeaux Mixture (Copper sulfate + Lime). Remove all infected plants immediately and destroy them. Avoid composting infected material.",
        "prevention": [
            "Plant resistant tomato varieties",
            "Avoid overhead irrigation",
            "Space plants for maximum air flow",
            "Apply preventive fungicide sprays before wet weather",
            "Inspect fields regularly during cool, wet periods",
            "Destroy all crop debris after harvest"
        ],
        "color": "#dc3545"
    },

    "Tomato_Leaf_Mold": {
        "display_name": "Tomato Leaf Mold",
        "plant": "Tomato",
        "description": "Leaf mold is a fungal disease caused by Passalora fulva, primarily affecting greenhouse or high-humidity tomato crops. It reduces photosynthesis and can cause significant yield loss.",
        "symptoms": [
            "Pale green or yellow patches on upper leaf surface",
            "Olive-green to brown velvety mold on lower leaf surface",
            "Leaves curl upward and eventually brown and drop",
            "Severely infected plants show widespread defoliation"
        ],
        "causes": [
            "Fungus: Passalora fulva (formerly Fulvia fulva)",
            "High relative humidity (above 85%)",
            "Poor ventilation in greenhouses",
            "Temperatures between 21–24°C",
            "Infected plant debris in soil"
        ],
        "severity": "Moderate",
        "chemical_treatment": "Apply Chlorothalonil, Maneb, or Thiram fungicides. Azoxystrobin (Quadris) is also effective. Rotate fungicides to prevent resistance.",
        "organic_treatment": "Improve greenhouse ventilation to reduce humidity. Apply Bacillus amyloliquefaciens biofungicide. Neem oil sprays provide some control. Remove affected leaves promptly.",
        "prevention": [
            "Maintain greenhouse humidity below 85%",
            "Ensure good air circulation and ventilation",
            "Use resistant tomato varieties",
            "Avoid wetting foliage when irrigating",
            "Sanitize greenhouse equipment between seasons",
            "Remove infected plant material promptly"
        ],
        "color": "#6f42c1"
    },

    "Potato_Early_Blight": {
        "display_name": "Potato Early Blight",
        "plant": "Potato",
        "description": "Early blight of potato is caused by Alternaria solani. While rarely fatal, it reduces photosynthesis and can lead to premature defoliation, reducing tuber yield.",
        "symptoms": [
            "Small, dark brown circular to oval spots on older leaves",
            "Spots have concentric rings giving a target-board appearance",
            "Yellow chlorotic halo around lesions",
            "Spots may merge to cover large leaf areas",
            "Lower leaves affected first, progressing upward"
        ],
        "causes": [
            "Fungus: Alternaria solani",
            "Warm, dry weather with intermittent rain",
            "Temperatures of 24–29°C",
            "Nutrient-stressed plants are more susceptible",
            "Infected seed tubers or plant debris"
        ],
        "severity": "Low to Moderate",
        "chemical_treatment": "Apply Mancozeb, Chlorothalonil, or Azoxystrobin fungicides. Begin spraying when plants are 15 cm tall. Repeat every 7–14 days during high-risk periods.",
        "organic_treatment": "Neem oil spray (3%) weekly. Copper-based organic fungicides. Ensure adequate potassium fertilization to strengthen plants. Remove lower infected leaves.",
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Rotate crops with non-solanaceous plants",
            "Avoid excessive nitrogen fertilization",
            "Ensure adequate potassium and phosphorus",
            "Remove and destroy infected plant material",
            "Apply mulch to reduce soil splash"
        ],
        "color": "#fd7e14"
    },

    "Potato_Late_Blight": {
        "display_name": "Potato Late Blight",
        "plant": "Potato",
        "description": "Potato late blight, caused by Phytophthora infestans, is the most devastating potato disease in the world. It can destroy an entire field within a week under favorable conditions.",
        "symptoms": [
            "Water-soaked, dark lesions on leaf margins and tips",
            "White cottony mold on underside of leaves in wet conditions",
            "Dark brown-black lesions on stems",
            "Brownish-purple dry rot on tubers",
            "Reddish-brown granular rot inside tubers"
        ],
        "causes": [
            "Oomycete: Phytophthora infestans",
            "Cool temperatures (10–20°C) and high humidity",
            "Extended periods of leaf wetness",
            "Infected seed tubers",
            "Wind and rain spread of spores"
        ],
        "severity": "Very High",
        "chemical_treatment": "Metalaxyl-M + Mancozeb (Ridomil Gold MZ) is the primary treatment. Dimethomorph, Cymoxanil, or Propamocarb are alternatives. Apply preventively and continue on 5–7 day intervals during wet weather.",
        "organic_treatment": "Bordeaux Mixture (1%) applied preventively. Copper hydroxide sprays. Destroy infected plants immediately. Never compost infected material. Use blight-resistant varieties.",
        "prevention": [
            "Plant certified blight-free seed potatoes",
            "Use resistant potato varieties",
            "Hill up soil around plants",
            "Apply preventive fungicides before wet periods",
            "Harvest tubers in dry conditions",
            "Store tubers in cool, dry, ventilated spaces",
            "Destroy all crop debris after harvest"
        ],
        "color": "#dc3545"
    },

    "Pepper_Bacterial_Spot": {
        "display_name": "Pepper Bacterial Spot",
        "plant": "Pepper",
        "description": "Bacterial spot of pepper is caused by Xanthomonas campestris pv. vesicatoria. It is one of the most serious diseases of pepper in warm, humid regions, causing leaf loss and fruit damage.",
        "symptoms": [
            "Small, water-soaked spots on leaves that turn brown",
            "Spots surrounded by yellow halo",
            "Lesions may drop out giving a shot-hole appearance",
            "Raised, scab-like lesions on fruit",
            "Premature defoliation in severe infections"
        ],
        "causes": [
            "Bacterium: Xanthomonas campestris pv. vesicatoria",
            "Warm temperatures (24–30°C)",
            "High humidity and rain splash",
            "Infected seeds or transplants",
            "Poor field sanitation"
        ],
        "severity": "Moderate to High",
        "chemical_treatment": "Copper-based bactericides (Copper hydroxide or Copper oxychloride) applied every 5–7 days. Combination of Copper + Mancozeb improves effectiveness. Streptomycin sulfate may be used where permitted.",
        "organic_treatment": "Copper soap (Bordeaux Mixture) applied preventively. Remove and destroy infected plant material. Use disease-free transplants. Avoid working in fields when plants are wet.",
        "prevention": [
            "Use certified pathogen-free seeds",
            "Treat seeds with hot water (52°C for 30 minutes)",
            "Plant resistant pepper varieties",
            "Avoid overhead irrigation",
            "Rotate crops for at least 2 years",
            "Sanitize tools and equipment",
            "Remove crop debris after harvest"
        ],
        "color": "#e83e8c"
    },

    "Pepper_Healthy": {
        "display_name": "Healthy Pepper",
        "plant": "Pepper",
        "description": "The pepper plant appears healthy with no signs of disease. Healthy pepper plants produce high yields when provided with proper nutrients, water, and sunlight.",
        "symptoms": ["Deep green, unblemished leaves", "Strong upright stems", "Normal fruit development"],
        "causes": ["Optimal growing conditions", "Balanced soil nutrition", "Adequate moisture"],
        "severity": "None",
        "chemical_treatment": "No treatment needed. Maintain regular fertilization schedule.",
        "organic_treatment": "Continue good practices: compost application, proper irrigation, and crop monitoring.",
        "prevention": [
            "Maintain soil pH between 6.0–6.8",
            "Practice crop rotation",
            "Use drip irrigation to keep foliage dry",
            "Monitor for pests and diseases weekly",
            "Apply balanced organic fertilizer"
        ],
        "color": "#28a745"
    }
}

# Class names matching the trained model output order
CLASS_NAMES = [
    "Healthy",
    "Tomato_Early_Blight",
    "Tomato_Late_Blight",
    "Tomato_Leaf_Mold",
    "Potato_Early_Blight",
    "Potato_Late_Blight",
    "Pepper_Bacterial_Spot",
    "Pepper_Healthy"
]

def get_disease_info(class_name):
    """Retrieve disease info. Returns a default if not found."""
    return DISEASE_DATABASE.get(class_name, {
        "display_name": class_name.replace("_", " "),
        "plant": "Unknown",
        "description": "Disease information not available in database.",
        "symptoms": ["Please update disease_data.py with information for this disease."],
        "causes": ["Unknown"],
        "severity": "Unknown",
        "chemical_treatment": "Consult a local agricultural expert.",
        "organic_treatment": "Consult a local agricultural expert.",
        "prevention": ["Consult a local agricultural expert."],
        "color": "#6c757d"
    })

def get_all_diseases():
    """Return all disease names."""
    return list(DISEASE_DATABASE.keys())

def add_disease(key, data):
    """Dynamically add a new disease to the database."""
    DISEASE_DATABASE[key] = data
    if key not in CLASS_NAMES:
        CLASS_NAMES.append(key)
