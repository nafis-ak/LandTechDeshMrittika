"""
Generates 6 distinct, professional, demo avatar SVGs for synthetic land officials.
Each portrait contains a clean vector person illustration with a subtle 'DEMO OFFICIAL' watermark.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_DIR = BASE_DIR / "frontend" / "assets" / "portraits"
PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)

AVATARS = [
    # Male 1 - Forest theme (AC Land)
    ("portrait_male_1.svg", "#1b4332", "#2d6a4f", "#e8f5e9", "#1e293b", "short", "#0f172a"),
    # Female 1 - Rose/Teal theme (Kanungo / AC Land)
    ("portrait_female_1.svg", "#0f766e", "#14b8a6", "#ccfbf1", "#334155", "long", "#042f2e"),
    # Male 2 - Blue theme (Sub-Registrar)
    ("portrait_male_2.svg", "#1e3a8a", "#3b82f6", "#dbeafe", "#1e293b", "side", "#172554"),
    # Female 2 - Gold theme (ULAO)
    ("portrait_female_2.svg", "#b45309", "#f59e0b", "#fef3c7", "#451a03", "hijab", "#78350f"),
    # Male 3 - Slate theme (Surveyor)
    ("portrait_male_3.svg", "#334155", "#64748b", "#f1f5f9", "#0f172a", "bald", "#1e293b"),
    # Female 3 - Purple theme (ULSAO / Peshkar)
    ("portrait_female_3.svg", "#6b21a8", "#a855f7", "#f3e8ff", "#3b0764", "bun", "#581c87"),
]

def make_svg(filename, bg_dark, primary, light_bg, hair_color, hair_style, suit_color):
    # Hair path variations
    if hair_style == "long":
        hair_markup = f'''
        <path d="M50 45 C35 45 35 110 38 120 C42 120 48 100 48 70 C48 70 52 70 52 70 C52 100 58 120 62 120 C65 110 65 45 50 45 Z" fill="{hair_color}"/>
        <circle cx="50" cy="55" r="22" fill="#fed7aa"/>
        <path d="M30 55 C30 35 70 35 70 55 C65 42 35 42 30 55 Z" fill="{hair_color}"/>
        '''
    elif hair_style == "hijab":
        hair_markup = f'''
        <path d="M50 30 C30 30 26 50 26 75 C26 100 35 125 50 125 C65 125 74 100 74 75 C74 50 70 30 50 30 Z" fill="{primary}"/>
        <circle cx="50" cy="58" r="18" fill="#fed7aa"/>
        <path d="M32 58 C32 46 68 46 68 58 C65 52 35 52 32 58 Z" fill="{primary}"/>
        '''
    elif hair_style == "bun":
        hair_markup = f'''
        <circle cx="50" cy="30" r="10" fill="{hair_color}"/>
        <circle cx="50" cy="55" r="22" fill="#fed7aa"/>
        <path d="M30 50 C32 35 68 35 70 50 C65 40 35 40 30 50 Z" fill="{hair_color}"/>
        '''
    elif hair_style == "bald":
        hair_markup = f'''
        <circle cx="50" cy="55" r="22" fill="#fed7aa"/>
        <path d="M28 55 C27 65 31 70 33 70 C31 65 30 58 28 55 Z" fill="{hair_color}"/>
        <path d="M72 55 C73 65 69 70 67 70 C69 65 70 58 72 55 Z" fill="{hair_color}"/>
        '''
    elif hair_style == "side":
        hair_markup = f'''
        <circle cx="50" cy="55" r="22" fill="#fed7aa"/>
        <path d="M28 52 C28 32 72 32 72 45 C65 36 40 38 30 52 Z" fill="{hair_color}"/>
        '''
    else: # short
        hair_markup = f'''
        <circle cx="50" cy="55" r="22" fill="#fed7aa"/>
        <path d="M28 50 C28 34 72 34 72 50 C66 40 34 40 28 50 Z" fill="{hair_color}"/>
        '''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 130" width="100%" height="100%">
  <defs>
    <linearGradient id="bg-{filename[:5]}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{light_bg}"/>
      <stop offset="100%" stop-color="{light_bg}" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <rect width="100" height="130" rx="12" fill="url(#bg-{filename[:5]})"/>
  
  <!-- Subtle Badge Background -->
  <circle cx="50" cy="55" r="38" fill="#ffffff" opacity="0.6"/>
  
  <!-- Body / Formal Suit -->
  <path d="M15 130 C15 95 32 85 50 85 C68 85 85 95 85 130 Z" fill="{suit_color}"/>
  <!-- Shirt & Tie/Scarf -->
  <path d="M42 85 L50 98 L58 85 Z" fill="#ffffff"/>
  <path d="M48 88 L52 88 L50 108 Z" fill="{primary}"/>
  
  <!-- Head & Hair -->
  {hair_markup}
  
  <!-- Eyes & Eyebrows -->
  <circle cx="43" cy="56" r="2" fill="#334155"/>
  <circle cx="57" cy="56" r="2" fill="#334155"/>
  <path d="M40 51 Q43 49 46 51" stroke="#334155" stroke-width="1.2" fill="none"/>
  <path d="M54 51 Q57 49 60 51" stroke="#334155" stroke-width="1.2" fill="none"/>
  
  <!-- Nose & Gentle Smile -->
  <path d="M50 56 L49 62 L52 62" stroke="#ea580c" stroke-width="0.8" fill="none" opacity="0.6"/>
  <path d="M46 67 Q50 70 54 67" stroke="#334155" stroke-width="1.2" fill="none"/>

  <!-- Official Demo Watermark Banner -->
  <rect x="10" y="112" width="80" height="13" rx="3" fill="#0f172a" opacity="0.8"/>
  <text x="50" y="121" fill="#f8fafc" font-size="6" font-family="Arial, sans-serif" font-weight="bold" text-anchor="middle" letter-spacing="0.5">DEMO OFFICIAL</text>
</svg>'''
    
    with open(PORTRAIT_DIR / filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {filename}")

def generate_all():
    for row in AVATARS:
        make_svg(*row)

if __name__ == "__main__":
    generate_all()
