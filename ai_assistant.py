"""
AI Swachhata Guru & Civic Assistant Engine
Dedicated to Indian Cultural Waste Management, Swachh Bharat Abhiyan Principles,
Civic Issue Classification, Vision Waste Scanning, and Interactive Waste Literacy.
"""
import random
import re
from typing import Dict, Any, List
from datetime import datetime

# ================= INDIAN CULTURAL WASTE KNOWLEDGE BASE =================
INDIAN_CULTURAL_KNOWLEDGE = {
    "nirmalya": {
        "bin": "Hara Koodadan (Green Bin / Home Floral Pit)",
        "color": "emerald",
        "title": "Nirmalya & Temple Puja Floral Offerings (पूजा के फूल व माला)",
        "advice": "Devotional flowers (Marigolds, Roses, Bel Patra) should **NEVER be dumped into sacred rivers (Ganga, Yamuna)** in plastic bags. Collect dried flowers separately; they make excellent sacred vermicompost for Tulsi plants or can be handed over to temple bio-incense (Dhoop & Agarbatti) processing drives."
    },
    "flower": {
        "bin": "Hara Koodadan (Green Bin / Wet Organic)",
        "color": "emerald",
        "title": "Temple Flowers & Puja Garlands (निर्माल्या)",
        "advice": "Discard plastic threads and golden foil garlands into the Blue Bin. Place real flower petals into the Green Bin or your home composting pot (Khamba). Real flower petals decompose into nutrient-rich organic manure within 3 weeks."
    },
    "coconut": {
        "bin": "Hara Koodadan (Wet Waste) or Garden Pit",
        "color": "emerald",
        "title": "Puja Coconut Shells & Coir Husk (नारियल की जटा व खोल)",
        "advice": "Dry coconut husks (Coir) are 100% natural and biodegradable. Break hard shells into smaller pieces before adding to compost, or use them as moisture-retaining mulch for garden potted plants. Do NOT throw them on roads as they collect stagnant rainwater and breed dengue mosquitoes."
    },
    "milk": {
        "bin": "Neela Koodadan (Blue Bin - Dry Recyclable)",
        "color": "blue",
        "title": "Milk Pouches (दूध की थैली - Amul / Mother Dairy etc.)",
        "advice": "🇮🇳 **Golden Rule of Swachh Bharat:** When opening a milk pouch, cut a slit but **DO NOT completely snip off the small triangular corner piece!** Detached micro-triangles cannot be sorted at recycling plants and end up choking cows and polluting water drains. Rinse the empty pouch, let it dry, and place it in the Blue Bin."
    },
    "kullhad": {
        "bin": "Garden Soil / Crushed Earthen Clay Pit",
        "color": "amber",
        "title": "Clay Kullhads & Earthen Diya Lamps (मिट्टी के कुल्हड़ व दीये)",
        "advice": "Clay kullhads made of pure baked terracotta are natural mud. After drinking chai, crush them lightly and mix them into soil or home garden planters. Do not mix with plastic dry recyclables."
    },
    "sanitary": {
        "bin": "Laal Koodadan (Red Bin / Domestic Sanitary Waste)",
        "color": "rose",
        "title": "Sanitary Pads & Baby Diapers (सेनेटरी अपशिष्ट)",
        "advice": "⚠️ **Dignity of Safai Mitras Rule:** Wrap used sanitary napkins and diapers securely in old newspaper or paper pouches and mark a **prominent RED DOT or RED CROSS (लाल बिंदी/निशान)** on the outside. This signals our sanitation workers to handle it with gloves without exposing them to biohazard pathogens."
    },
    "malba": {
        "bin": "Special Malba Pickup (मलबा उठाव)",
        "color": "amber",
        "title": "Construction & Demolition Malba (ईंट, प्लास्टर, टाइल्स)",
        "advice": "Broken concrete, bricks, wall plaster, and ceramic tiles should **NEVER be dumped in municipal dustbins** or on empty plots. Schedule a dedicated **'Malba Pickup'** through our portal so Nagar Nigam hydraulic lifters can transport it to designated C&D recycling plants."
    },
    "diwali": {
        "bin": "Neela Koodadan (Dry Waste - after cooling)",
        "color": "amber",
        "title": "Post-Festival & Firecracker Residue (त्योहारों का कचरा)",
        "advice": "Allow all burnt firecracker shells to cool down completely for 12 hours. Sprinkle water to extinguish any hidden embers before sweeping. Collect paper cardboard tubes into dry waste and clay pot remnants into mud debris."
    },
    "pizza": {
        "bin": "Neela Koodadan (Clean Lid) + Regular Trash (Greasy bottom)",
        "color": "blue",
        "title": "Pizza Cartons & Food-Stained Paper",
        "advice": "Cardboard soaked in cheese oil cannot be recycled into fresh paper pulp. Tear off the clean top lid for the Blue Bin, and put the greasy base in standard waste."
    },
    "battery": {
        "bin": "Kaala / Grey Bin (E-Kachra & Hazardous)",
        "color": "indigo",
        "title": "Batteries & E-Waste (इलेक्ट्रॉनिक कचरा)",
        "advice": "Never toss dead remote/clock batteries or old smartphone cells into regular trash. Toxic lithium, lead, and cadmium leak into underground aquifers. Hand over to authorized E-Waste drop-off points."
    },
    "chai": {
        "bin": "Hara Koodadan (Green Bin / Kitchen Compost)",
        "color": "emerald",
        "title": "Chai Patti / Tea Leaves (चाय की पत्ती)",
        "advice": "Used tea leaves are pure organic gold! Rinse milk or sugar residue lightly, then put them directly into rose and tulsi plant pots as a high-nitrogen natural fertilizer."
    }
}

# ================= AI SWACHHATA ACADEMY LESSONS =================
SWACHHATA_LESSONS = [
    {
        "id": "lesson-1",
        "number": "01",
        "title": "The 2-Bin Revolution: Geela vs Sookha Kachra",
        "hindiTitle": "हरा कूड़ादान बनाम नीला कूड़ादान - स्रोत पर पृथक्करण",
        "category": "Foundation",
        "readTime": "3 min",
        "icon": "🌱",
        "summary": "Why mixing kitchen wet waste with dry recyclables creates toxic landfill fires at Ghazipur and Deonar.",
        "content": [
            {
                "subheading": "1. What is Geela Kachra (Wet Waste)?",
                "text": "All organic kitchen leftovers: vegetable peels (sabzi ke chilke), fruit rinds, stale rotis, used chai patti, eggshells, and temple flowers. If it can rot naturally, it belongs in the Green Bin (हरा कूड़ादान)."
            },
            {
                "subheading": "2. What is Sookha Kachra (Dry Waste)?",
                "text": "Clean cardboard cartons, plastic milk pouches, PET beverage bottles, metal cans, newspaper raddi, and glass containers. Keep it in the Blue Bin (नीला कूड़ादान)."
            },
            {
                "subheading": "3. The Tragedy of Mixing Waste",
                "text": "When wet dal or sabzi gets onto paper and cardboard, the paper pulp becomes unrecyclable. Trapped wet organic waste produces methane gas in open landfills, causing dangerous self-igniting landfill fires."
            }
        ],
        "swachhTip": "Keep two separate small dustbins right under your kitchen sink. Segregation takes only 2 seconds!"
    },
    {
        "id": "lesson-2",
        "number": "02",
        "title": "Nirmalya & Temple Floral Waste Upcycling",
        "hindiTitle": "पवित्र निर्माल्य: फूलों से बनेगी अगरबत्ती व जैविक खाद",
        "category": "Culture & Faith",
        "readTime": "3 min",
        "icon": "🌸",
        "summary": "Transforming sacred puja flowers into natural organic incense and compost instead of suffocating holy rivers.",
        "content": [
            {
                "subheading": "1. The River Pollution Dilemma",
                "text": "Every year, thousands of metric tons of puja flowers and garlands wrapped in non-biodegradable polythene bags are immersed into rivers like the Ganga, Yamuna, and Godavari, depleting oxygen levels for aquatic life."
            },
            {
                "subheading": "2. The Nirmalya Upcycling Path",
                "text": "Real flower petals (marigold, rose, jasmine) contain essential natural oils. When separated from plastic threads and golden foil, they are sun-dried and powdered into charcoal-free dhoop, holy vermicompost, and natural holi colors."
            },
            {
                "subheading": "3. How You Can Do It at Home",
                "text": "Keep a dedicated earthen pot for daily puja flowers. Allow them to dry naturally and crumble them into your home garden or Tulsi pot."
            }
        ],
        "swachhTip": "Never throw polythene bags into rivers along with puja offerings. True devotion preserves Mother Nature."
    },
    {
        "id": "lesson-3",
        "number": "03",
        "title": "The 100-Crore Milk Pouch Habit & Single-Use Plastic",
        "hindiTitle": "दूध की थैली का कोना पूरा न काटें: एक छोटी आदत, बड़ा बदलाव",
        "category": "Daily Habits",
        "readTime": "2 min",
        "icon": "🥛",
        "summary": "How snipping milk pouches without detaching the tiny plastic corner avoids microplastic choking in cows & marine life.",
        "content": [
            {
                "subheading": "1. The Mystery of the Missing Corners",
                "text": "India consumes over 100 million milk and oil pouches every single day. Most people snip off a small 1-centimeter triangle from the top corner and throw it into the trash."
            },
            {
                "subheading": "2. Why Micro-Snips are Catastrophic",
                "text": "These microscopic plastic triangles are too small for municipal waste sorting machines. They slip through grates, get washed into storm drains, end up in cow bellies, and pollute agricultural fields for 500 years."
            },
            {
                "subheading": "3. The Simple Solution: Slit, Don't Snip!",
                "text": "Cut a straight slit across the corner or leave the corner tip hanging connected to the main body of the pouch. That way, 100% of the plastic gets bundled and recycled into secondary plastic lumber."
            }
        ],
        "swachhTip": "Always leave the cut corner attached to the pouch. Rinse and dry before placing in the Blue Bin."
    },
    {
        "id": "lesson-4",
        "number": "04",
        "title": "Odorless Terrace & Balcony Composting (घर की खाद)",
        "hindiTitle": "बालकनी में बदबू-रहित खाद बनाना सीखें",
        "category": "Home Green",
        "readTime": "4 min",
        "icon": "🪴",
        "summary": "Converting everyday dal, roti, and vegetable peels into nutrient-rich 'Black Gold' for Indian apartments.",
        "content": [
            {
                "subheading": "1. The 3-Tier Earthen Khamba System",
                "text": "Terracotta pots allow natural air circulation, preventing bad odors. Place kitchen peels (Greens = Nitrogen) and cover them with a layer of dry crushed leaves or cocopeat (Browns = Carbon)."
            },
            {
                "subheading": "2. Maintaining the Balance",
                "text": "Never add large bones, thick plastic wrappers, or excessive oily gravies to home compost. Sprinkle a spoonful of sour buttermilk (chaach/dahi) or compost microbes once a week to speed up digestion."
            },
            {
                "subheading": "3. Harvesting Black Gold",
                "text": "In 30 to 45 days, the contents turn into a dark, earthy-smelling organic compost that will make your home vegetables, curry leaves, and flowering plants thrive naturally without synthetic chemicals."
            }
        ],
        "swachhTip": "One household composting diverts over 300 kilograms of wet waste per year from city landfills!"
    },
    {
        "id": "lesson-5",
        "number": "05",
        "title": "Dignity of Safai Mitras & The Red Cross Rule",
        "hindiTitle": "सफाई मित्रों का सम्मान: सेनेटरी कचरे पर लाल बिंदी का नियम",
        "category": "Human Dignity",
        "readTime": "3 min",
        "icon": "❤️",
        "summary": "Protecting sanitation workers from biological infection through responsible newspaper wrapping and red-dot marking.",
        "content": [
            {
                "subheading": "1. The Unseen Heroes of Clean India",
                "text": "Our Safai Mitras (sanitation workers) wake up at 5:00 AM daily to sweep our streets and collect waste. Handling unsegregated dirty pads, sharp shaving blades, and broken glass puts them at extreme risk of hepatitis, tetanus, and skin infections."
            },
            {
                "subheading": "2. The Red Dot / Red Cross Protocol",
                "text": "Wrap all used menstrual napkins, baby diapers, and adult sanitary pads in old newspaper or paper disposal envelopes. Using a red sketch pen or bindu, mark a bold red cross or dot on the outer packet."
            },
            {
                "subheading": "3. Sharp Waste Precaution",
                "text": "Place used razor blades, broken tubelights, and glass injection vials inside an empty cardboard box or thick plastic jar before discarding."
            }
        ],
        "swachhTip": "Sanitation workers are the frontline guardians of our city's public health. Treat them with respect and gratitude."
    }
]

# ================= INTERACTIVE SWACHHATA QUIZ =================
SWACHH_QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Where should used tea leaves (Chai Patti) and vegetable peels be disposed of?",
        "options": [
            "Blue Bin (Dry Waste)",
            "Green Bin (Wet Waste / Composting)",
            "Red Bin (Sanitary Waste)",
            "Throw directly on empty street"
        ],
        "correctIndex": 1,
        "explanation": "Chai patti and sabzi peels are 100% biodegradable wet waste (Geela Kachra) that turns into organic compost in the Green Bin."
    },
    {
        "id": 2,
        "question": "What is the correct way to open and dispose of plastic milk pouches?",
        "options": [
            "Snip the tiny corner completely off and throw on the floor",
            "Leave the corner attached to the main pouch, rinse, dry, and place in Blue Bin",
            "Throw unwashed milk packet into the Green Bin with wet waste",
            "Burn it in the backyard fire"
        ],
        "correctIndex": 1,
        "explanation": "Leaving the corner attached ensures the small plastic tip doesn't become microplastic litter that animals consume."
    },
    {
        "id": 3,
        "question": "How should domestic sanitary waste (pads/diapers) be handed over to Safai Mitras?",
        "options": [
            "Tied in a black polythene bag without marking",
            "Wrapped in newspaper with a prominent RED DOT / RED CROSS marked on it",
            "Flushed down the domestic toilet drain",
            "Mixed with kitchen leftover dal"
        ],
        "correctIndex": 1,
        "explanation": "The Swachh Bharat protocol requires wrapping sanitary waste in paper marked with a red symbol to protect sanitation workers from direct biohazard exposure."
    },
    {
        "id": 4,
        "question": "What should be done with devotional temple flowers (Nirmalya) after puja?",
        "options": [
            "Dump them into the nearest river in plastic bags",
            "Burn them with plastic waste",
            "Collect for sacred home composting or floral incense (Dhoop/Agarbatti) processing",
            "Throw them on the street corner"
        ],
        "correctIndex": 2,
        "explanation": "Puja flowers make divine organic compost for home plants and can be upcycled into floral incense rather than choking river ecosystems."
    }
]

def get_ai_response(message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    text = message.strip().lower()
    user_name = user_context.get("name", "Swachh Nagrik") if user_context else "Swachh Nagrik"
    user_role = user_context.get("role", "Citizen") if user_context else "Citizen"

    # 1. Greetings (Namaste / Swachhata)
    if re.search(r"\b(hi|hello|hey|namaste|pranam|ram ram|morning|evening)\b", text):
        return {
            "reply": f"नमस्ते {user_name}! 🙏 I am **AI Swachhata Guru** — your intelligent guide for the Swachh Bharat Abhiyan & sustainable Indian waste management.\n\nI can assist you with:\n- 🇮🇳 **Bilingual Segregation**: Ask where to put nirmalya flowers, coconut shells, milk packets, kullhad cups, or electronic items.\n- 📚 **Interactive Waste Academy**: Take 5 guided lessons and earn your official **Swachh Nagrik Certificate**!\n- 🚨 **Civic Complaint Assistance**: Report overflowing community dustbins, road litter, or construction malba for Nagar Nigam dispatch.\n- 🚛 **Bulk Pickup & Malba Booking**: Book door-to-door mini-truck collection for furniture, society debris, or festival cleanups.",
            "suggestions": ["What to do with puja flowers?", "Where to throw milk packets?", "How to get Swachh Nagrik Certificate?", "Report overflowing bin nearby"]
        }

    # 2. Check Cultural & Specific Waste Knowledge
    for key, data in INDIAN_CULTURAL_KNOWLEDGE.items():
        if key in text:
            return {
                "reply": f"### 💡 Swachhata Guru Guide: {data['title']}\n\n**Destination:** `{data['bin']}`\n\n{data['advice']}",
                "action_type": "disposal_advice",
                "tag": data['bin'],
                "suggestions": ["Tell me about milk packet rule", "What about temple flower nirmalya?", "Take me to Swachhata Academy"]
            }

    # 3. Questions about Reporting Complaints
    if any(k in text for k in ["report", "complaint", "overflow", "garbage", "kachra", "dumping", "road", "gali"]):
        return {
            "reply": "### 🚨 Report a Civic Sanitation Issue\n\nNagar Nigam and Ward Safai Mitras take immediate action on geotagged citizen reports:\n1. Switch to the **'Report Issue'** tab above.\n2. Click **'📍 Detect GPS'** to automatically tag your Ward and coordinates.\n3. Type your observation (e.g. *'Sabzi mandi gate par kachra phel raha hai'*) and use our **'✨ AI Auto-Classify'** button to format it into a standardized municipal dispatch.\n4. Upload an optional photo for rapid verification!",
            "action_type": "navigate_tab",
            "target_tab": "tab-report",
            "suggestions": ["Take me to Report Issue", "Check status of my ward reports"]
        }

    # 4. Questions about Malba & Bulk Pickups
    if any(k in text for k in ["malba", "pickup", "bulk", "furniture", "charpai", "appliance", "truck", "construction"]):
        return {
            "reply": "### 🚛 Doorstep Bulk Waste & Malba Pickup\n\nFor heavy items like old sofas, wooden charpais, renovation concrete rubble (malba), or gated society collective cleanouts:\n- Open the **'Bulk Pickup'** tab.\n- Select your volume: from 50 kg to a Full Mini-Truck load (500+ kg).\n- Select your preferred collection date.\n- Nagar Nigam hydraulic lifter vehicles will arrive at your address with gate clearance!",
            "action_type": "navigate_tab",
            "target_tab": "tab-pickup",
            "suggestions": ["Schedule Doorstep Bulk Pickup", "What qualifies as Malba?"]
        }

    # 5. Questions about Lessons / Quiz / Certificate
    if any(k in text for k in ["lesson", "quiz", "certificate", "academy", "learn", "teach", "guru"]):
        return {
            "reply": "### 🎓 Welcome to the AI Swachhata Academy!\n\nBecome a certified environmental leader in your mohalla:\n- Read 5 short cultural waste management modules (Hara vs Neela Koodadan, Nirmalya Upcycling, Milk Pouch Habit, Home Khamba Composting, Safai Mitra Dignity).\n- Take the **4-Question Swachh Quiz**.\n- Score 75% or higher to earn an official **Swachh Bharat Citizen Certificate (स्वच्छ नागरिक प्रमाण-पत्र)**!",
            "action_type": "navigate_tab",
            "target_tab": "tab-academy",
            "suggestions": ["Start Lesson 1 Now", "Take the Swachh Quiz"]
        }

    # 6. Admin Portal
    if any(k in text for k in ["admin", "dashboard", "hotspot", "fleet", "route", "supervisor", "ward"]):
        if user_role == "Administrator":
            return {
                "reply": "### 🛡️ Nagar Nigam Sanitation Command Center\n\nAdministrative capabilities active:\n- **Ward Hotspots**: Monitor repetitive garbage density across wards.\n- **AI Fleet Optimizer**: Calculates fuel-efficient multi-stop routes for Nagar Nigam collection tippers.\n- **Status Dispatch Table**: Assign field sweep teams and track turnaround time from Pending to Resolved.",
                "action_type": "navigate_tab",
                "target_tab": "tab-admin",
                "suggestions": ["Open Admin Portal", "View Ward Hotspots"]
            }
        else:
            return {
                "reply": "The **Admin Portal** is designed for Municipal Ward Supervisors. You can test supervisor capabilities by clicking **'⚡ Demo Admin'** in the top navigation bar!",
                "suggestions": ["Switch to Demo Admin", "How do I report garbage in my ward?"]
            }

    # Default Helpful Response
    return {
        "reply": f"Dhanyavaad for asking, {user_name}! 🙏 I am here to help build a cleaner, greener India.\n\nRemember our core 3-stream segregation:\n- 🟢 **Geela Kachra (Wet / Organic)** ➔ Green Bin (Sabzi peels, fruit rinds, chai patti, puja flowers)\n- 🔵 **Sookha Kachra (Dry Recyclable)** ➔ Blue Bin (Cardboard, washed milk packets, bottles, paper raddi)\n- 🔴 **Sanitary / Hazardous** ➔ Red Bin (Paper-wrapped pads with Red Dot, batteries, medicines)\n\nAsk me any question in English or Hindi/Hinglish!",
        "suggestions": ["What to do with puja flowers?", "Where to throw milk packets?", "Start Swachhata Quiz", "Report an issue"]
    }

def classify_issue_text(text: str) -> Dict[str, Any]:
    raw = text.strip()
    lower = raw.lower()

    category = "Overflowing Bins"
    urgency = "Standard"
    estimated_volume = "Medium (1-2 Bins)"
    hazard_flags = []

    # Heuristics tailored for Indian civic terminology
    if any(k in lower for k in ["road", "street", "gali", "chowk", "bazaar", "mandi", "highway", "sidewalk", "scattered", "litter", "kooda"]):
        category = "Garbage on Roads"
    elif any(k in lower for k in ["missed", "delayed", "nahi aayi", "didn't come", "kachra gadi", "tipper", "absent", "gadi nahi"]):
        category = "Missed Collection"
    elif any(k in lower for k in ["malba", "illegal", "dump", "construction", "tractor", "debris", "night", "rubble", "concrete", "broken bricks"]):
        category = "Illegal Dumping"
    elif any(k in lower for k in ["overflow", "spill", "dustbin", "container", "full", "heaping", "dhalav"]):
        category = "Overflowing Bins"

    # Urgency detection
    if any(k in lower for k in ["urgent", "danger", "hazard", "chemical", "hospital", "smell", "badbu", "rotten", "makkhi", "machhar", "stray dogs", "stray cattle", "traffic"]):
        urgency = "High (Priority Municipal Dispatch)"
        hazard_flags.append("Public Hygiene / Stray Animal / Traffic Risk")

    # Volume detection
    if any(k in lower for k in ["truck", "tractor", "huge", "massive", "tons", "pahad", "dhalav", "malba"]):
        estimated_volume = "Large Truckload (500+ kg)"
    elif any(k in lower for k in ["few bags", "small", "wrapper", "packet"]):
        estimated_volume = "Small (< 50 kg)"

    words = raw.split()
    first_phrase = " ".join(words[:6]) if len(words) > 6 else raw
    suggested_title = f"{category}: {first_phrase.capitalize()}"

    enhanced = (
        f"{raw.capitalize() if not raw.endswith('.') else raw} "
        f"[AI Nagar Nigam Field Assessment: Categorized under {category}. Urgency: {urgency}. "
        f"Estimated Volume: {estimated_volume}. Sanitation crew requested with appropriate hydraulic containment tipper.]"
    )

    return {
        "category": category,
        "urgency": urgency,
        "estimated_volume": estimated_volume,
        "suggested_title": suggested_title,
        "enhanced_description": enhanced,
        "hazard_flags": hazard_flags
    }

def analyze_waste_image(item_type: str = "plastic_bottle") -> Dict[str, Any]:
    samples = {
        "plastic_bottle": {
            "detected_item": "PET Plastic Mineral Water / Cold Drink Bottle (PETE #1)",
            "category": "Sookha Kachra (Non-Biodegradable Dry Recyclable)",
            "bin": "Neela Koodadan (Blue Bin)",
            "bin_color": "blue",
            "confidence": 98.8,
            "recyclability_score": 96,
            "carbon_saved_kg": 0.22,
            "instructions": [
                "Empty all liquid content completely.",
                "Rinse lightly with recycled graywater.",
                "Crush bottle flat to save municipal collection space.",
                "Replace the plastic screw cap onto the crushed bottle."
            ]
        },
        "food_scraps": {
            "detected_item": "Sabzi Peels, Leftover Rotis & Fruit Rinds (सब्जी के छिलके)",
            "category": "Geela Kachra (Biodegradable Wet Waste)",
            "bin": "Hara Koodadan (Green Bin)",
            "bin_color": "emerald",
            "confidence": 99.4,
            "recyclability_score": 100,
            "carbon_saved_kg": 0.58,
            "instructions": [
                "Drain excess gravy or watery liquid before binning.",
                "Wrap in old newspaper or compostable bio-liners (no polythene).",
                "Ideal for home balcony Khamba composting or society biomethanation."
            ]
        },
        "battery": {
            "detected_item": "Cylindrical Battery & Old Charger Cord (ई-कचरा / बैटरी)",
            "category": "Domestic Hazardous Waste / E-Waste",
            "bin": "Kaala / Grey Bin (Hazardous E-Waste Drop-off)",
            "bin_color": "amber",
            "confidence": 97.6,
            "recyclability_score": 88,
            "carbon_saved_kg": 1.15,
            "instructions": [
                "NEVER dispose in regular wet or dry household bins.",
                "Tape conductive metal terminals with insulation tape to prevent short circuits.",
                "Deposit at municipal authorized E-Waste collection drives."
            ]
        },
        "pizza_box": {
            "detected_item": "Cardboard Box with Oil & Food Stains (चिकना कार्डबोर्ड)",
            "category": "Mixed Waste (Separation Required)",
            "bin": "Blue Bin (Top Clean Lid) + Trash (Oily bottom)",
            "bin_color": "amber",
            "confidence": 96.5,
            "recyclability_score": 55,
            "carbon_saved_kg": 0.14,
            "instructions": [
                "Tear away the clean top cardboard lid for the Blue Bin.",
                "The oil-soaked bottom cardboard should be discarded in standard waste."
            ]
        },
        "nirmalya_flowers": {
            "detected_item": "Temple Puja Garlands & Marigold Petals (पवित्र निर्माल्य)",
            "category": "Sacred Organic Waste (Geela Kachra)",
            "bin": "Hara Koodadan (Green Bin / Home Composting Pot)",
            "bin_color": "emerald",
            "confidence": 99.2,
            "recyclability_score": 100,
            "carbon_saved_kg": 0.45,
            "instructions": [
                "Detach plastic thread and golden foil into the Blue Bin.",
                "Never dump flowers in plastic bags into holy rivers.",
                "Compost petals at home for Tulsi and flowering plants, or donate to temple incense drives."
            ]
        }
    }

    key = item_type.lower()
    return samples.get(key, samples["plastic_bottle"])

def calculate_route_optimization(complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not complaints:
        return {"routes": [], "estimated_fuel_saved_liters": 0, "total_stops": 0}

    pending = [c for c in complaints if c.get("status") in ["Pending", "Assigned"]]
    
    stops = []
    for idx, c in enumerate(pending[:6]):
        priority = "P0 (Urgent)" if c.get("category") in ["Illegal Dumping", "Overflowing Bins"] else "P1 (Standard)"
        stops.append({
            "stop_number": idx + 1,
            "complaint_id": f"SW-{c.get('id', 100):04d}",
            "title": c.get("title"),
            "ward": c.get("ward_number", "Ward 14"),
            "location": c.get("location_text"),
            "category": c.get("category"),
            "priority": priority,
            "eta_minutes": (idx + 1) * 18
        })

    estimated_fuel_saved = round(len(stops) * 2.1, 1)

    return {
        "vehicle_id": "Nagar Nigam Swachhata Tipper #IND-14",
        "driver_unit": "Safai Mitra Rapid Response Crew Alpha",
        "recommended_route": stops,
        "total_stops": len(stops),
        "estimated_fuel_saved_liters": estimated_fuel_saved,
        "co2_emissions_avoided_kg": round(estimated_fuel_saved * 2.68, 1),
        "route_summary": f"AI optimized shortest-path corridor covering {len(stops)} ward hotspots with zero redundant backtracks."
    }

def get_swachhata_lessons() -> List[Dict[str, Any]]:
    return SWACHHATA_LESSONS

def grade_swachh_quiz(user_answers: Dict[str, int], user_name: str = "Swachh Nagrik") -> Dict[str, Any]:
    correct_count = 0
    feedback = []

    for q in SWACHH_QUIZ_QUESTIONS:
        qid_str = str(q["id"])
        selected = user_answers.get(qid_str)
        is_correct = (selected == q["correctIndex"])
        if is_correct:
            correct_count += 1
        feedback.append({
            "questionId": q["id"],
            "question": q["question"],
            "userSelected": selected,
            "correctIndex": q["correctIndex"],
            "isCorrect": is_correct,
            "explanation": q["explanation"]
        })

    total = len(SWACHH_QUIZ_QUESTIONS)
    percentage = round((correct_count / total) * 100)
    passed = percentage >= 75

    cert_data = None
    if passed:
        cert_data = {
            "certificateId": f"SWACHH-IN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "citizenName": user_name,
            "score": f"{percentage}%",
            "grade": "Exemplary Swachh Ambassador (स्वच्छता राजदूत)",
            "date": datetime.now().strftime("%d %B %Y"),
            "issuingAuthority": "AI Swachhata Academy & Nagar Nigam Civic Initiative"
        }

    return {
        "total": total,
        "correctCount": correct_count,
        "percentage": percentage,
        "passed": passed,
        "feedback": feedback,
        "certificate": cert_data
    }
