"""
Generates authentic, high-resolution sample deed (দলিল) and porcha (খতিয়ান) documents
using official Bangladesh land administration structures and Kalpurush Bengali typography.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import pymupdf

FONT_PATH = "/Library/Fonts/kalpurush.ttf"
OUTPUT_DIR = "/Users/macbookair/Desktop/LandTechDeshMrittika/frontend/assets/samples"

def get_font(size: int):
    if os.path.exists(FONT_PATH):
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    return ImageFont.load_default()

def create_authentic_deed():
    """Creates a high-resolution authentic Saf-Kabala deed (সাফ-কবালা দলিল)."""
    width, height = 1200, 1600
    img = Image.new("RGB", (width, height), color=(253, 252, 248))
    draw = ImageDraw.Draw(img)

    # Outer and inner border
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline=(30, 60, 55), width=3)
    draw.rectangle([(35, 35), (width - 35, height - 35)], outline=(180, 150, 100), width=1)

    # Top Stamp Header Banner (Simulating Non-judicial stamp aesthetic)
    draw.rectangle([(50, 50), (width - 50, 160)], fill=(245, 240, 230), outline=(150, 120, 80), width=2)
    
    font_stamp_title = get_font(28)
    font_stamp_sub = get_font(18)
    font_h1 = get_font(32)
    font_h2 = get_font(22)
    font_body = get_font(19)
    font_body_bold = get_font(20)
    font_small = get_font(15)

    # Stamp text
    draw.text((width // 2, 75), "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — ১০০ টাকার নন-জুডিশিয়াল স্ট্যাম্প", fill=(100, 30, 20), font=font_stamp_title, anchor="mt")
    draw.text((width // 2, 118), "নিবন্ধন পরিদপ্তর, আইন ও বিচার বিভাগ | সাব-রেজিস্ট্রারের কার্যালয়, সাভার, ঢাকা", fill=(50, 50, 50), font=font_stamp_sub, anchor="mt")

    # Registration Box
    draw.rectangle([(width - 380, 180), (width - 60, 260)], outline=(180, 40, 30), width=2)
    draw.text((width - 365, 192), "দলিল নং: ৮৪৫২/২০২৪ (SAVAR-20261018-00003)", fill=(180, 20, 20), font=font_body_bold)
    draw.text((width - 365, 222), "রেজিস্ট্রেশন তারিখ: ১৫/১০/২০২৪ ইং", fill=(40, 40, 40), font=font_small)

    # Title
    draw.text((width // 2, 280), "সাফ-কবালা বিক্রয় দলিল (DEED OF SALE)", fill=(20, 45, 40), font=font_h1, anchor="mt")
    draw.line([(width // 2 - 240, 325), (width // 2 + 240, 325)], fill=(20, 45, 40), width=2)

    # Parties Section
    y = 350
    draw.text((65, y), "১ম পক্ষ (দাতা / বিক্রেতা):", fill=(15, 60, 50), font=font_h2)
    y += 35
    draw.text((80, y), "দাতার নাম: মো: রফিকুল ইসলাম, পিতা: মরহুম আব্দুল কাদের, সাং: আমিনবাজার, থানা: সাভার, জেলা: ঢাকা।", fill=(30, 30, 30), font=font_body)
    y += 30
    draw.text((80, y), "জাতীয় পরিচয়পত্র নং: ১৯৭৫২৬৯২৬৭২০১০০, পেশা: কৃষি ও ব্যবসা, ধর্ম: ইসলাম।", fill=(70, 70, 70), font=font_small)

    y += 50
    draw.text((65, y), "২য় পক্ষ (গ্রহীতা / ক্রেতা):", fill=(15, 60, 50), font=font_h2)
    y += 35
    draw.text((80, y), "গ্রহীতার নাম: মোসা: জমিলা খাতুন, স্বামী: তারেক হাসান, সাং: মিরপুর-১, থানা: মিরপুর, জেলা: ঢাকা।", fill=(30, 30, 30), font=font_body)
    y += 30
    draw.text((80, y), "জাতীয় পরিচয়পত্র নং: ১৯৮৮২৬৯২৬৭২০২০০, ধর্ম: ইসলাম।", fill=(70, 70, 70), font=font_small)

    # Property Schedule
    y += 55
    draw.rectangle([(55, y), (width - 55, y + 250)], fill=(250, 248, 242), outline=(200, 190, 170), width=1)
    draw.text((75, y + 15), "বিক্রিত ভূমির তপশিল ও পরিচিতি:", fill=(20, 50, 45), font=font_h2)
    
    props = [
        ("জেলা: ঢাকা, উপজেলা: সাভার", "সাব-রেজিস্ট্রি অফিস: সাভার সদর"),
        ("মৌজা: আমিনবাজার", "জে.এল. নম্বর: ২৬ (26)"),
        ("এস.এ. খতিয়ান নং: ১৪৫", "আর.এস. খতিয়ান নং: ৩২৮"),
        ("সাবেক দাগ নং: ৫১২", "হাল দাগ নং: ১০৪ (DAG NO: 104)"),
        ("জমির শ্রেণী: নাল (কৃষি জমি)", "বিক্রিত জমির পরিমাণ: ১২.৫০ শতাংশ (12.50 Decimals)")
    ]
    py = y + 55
    for left, right in props:
        draw.text((85, py), left, fill=(35, 35, 35), font=font_body)
        draw.text((width // 2 + 50, py), right, fill=(35, 35, 35), font=font_body)
        py += 35

    # Boundary Details
    y += 275
    draw.text((65, y), "চৌহদ্দি বর্ণনা:", fill=(15, 60, 50), font=font_h2)
    y += 35
    draw.text((80, y), "উত্তরে: হাল ১০২ দাগের জমি, দক্ষিণে: হাল ১০৬ দাগের জমি, পূর্বে: ১২ ফুট চলাচলের রাস্তা, পশ্চিমে: সরকারী খাল।", fill=(40, 40, 40), font=font_body)

    # Consideration & Declaration
    y += 55
    draw.text((65, y), "পণমূল্য ও বিবরণ:", fill=(15, 60, 50), font=font_h2)
    y += 35
    draw.text((80, y), "মোট পণমূল্য: ১৮,৫০,০০০/- (আঠারো লক্ষ পঞ্চাশ হাজার টাকা মাত্র) অত্র দলিল রেজিস্ট্রির পূর্বে নগদ বুঝিয়া পাইয়া", fill=(35, 35, 35), font=font_body)
    y += 28
    draw.text((80, y), "অদ্য হইতে ক্রেতাকে ভূমির নিরঙ্কুশ স্বত্ব ও দখল বুঝাইয়া দেওয়া হইল। অত্র সম্পত্তিতে আমার আর কোনো দাবি রহিল না।", fill=(35, 35, 35), font=font_body)

    # Signatures
    y = height - 210
    draw.line([(65, y), (width - 65, y)], fill=(200, 200, 200), width=1)
    draw.text((120, y + 40), "মো: রফিকুল ইসলাম\n(দাতার স্বাক্ষর ও টিপসহি)", fill=(50, 50, 50), font=font_body, align="center")
    draw.text((width // 2, y + 40), "সৈয়দ আহমেদ\n(মুসাবিদাকারী / দলিল লেখক)", fill=(50, 50, 50), font=font_body, align="center")
    draw.text((width - 240, y + 40), "সাব-রেজিস্ট্রার\nসাভার, ঢাকা\n(সিলমোহর ও স্বাক্ষর)", fill=(150, 30, 20), font=font_body_bold, align="center")

    out_path = os.path.join(OUTPUT_DIR, "sample_deed_authentic.png")
    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated authentic deed: {out_path}")
    return out_path

def create_authentic_porcha():
    """Creates a high-resolution authentic ROR Khatian (আর.এস. খতিয়ান / পরচা)."""
    width, height = 1200, 1500
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(40, 40, 40), width=2)
    
    font_h1 = get_font(28)
    font_h2 = get_font(22)
    font_th = get_font(18)
    font_td = get_font(17)
    font_small = get_font(15)

    # Header
    draw.text((width // 2, 50), "বাংলাদেশ ফরম নং ৫৪৬৩ (হাল খতিয়ান)", fill=(50, 50, 50), font=font_small, anchor="mt")
    draw.text((width // 2, 85), "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — ভূমি রেকর্ড ও জরিপ অধিদপ্তর", fill=(20, 20, 20), font=font_h1, anchor="mt")
    draw.text((width // 2, 125), "খতিয়ান বা স্বত্বলিপি (আর.এস. জরিপ)", fill=(20, 70, 50), font=font_h2, anchor="mt")

    # General Info Grid
    y = 175
    draw.rectangle([(50, y), (width - 50, y + 90)], outline=(100, 100, 100), width=1)
    draw.text((70, y + 15), "জেলা: ঢাকা", fill=(30, 30, 30), font=font_th)
    draw.text((320, y + 15), "থানা/উপজেলা: সাভার", fill=(30, 30, 30), font=font_th)
    draw.text((620, y + 15), "মৌজা: আমিনবাজার", fill=(30, 30, 30), font=font_th)
    draw.text((920, y + 15), "জে.এল. নং: ২৬", fill=(30, 30, 30), font=font_th)

    draw.text((70, y + 50), "আর.এস. খতিয়ান নং: ৩২৮", fill=(160, 20, 20), font=font_h2)
    draw.text((450, y + 55), "সাবেক খতিয়ান নং: ১৪৫ (এস.এ.)", fill=(50, 50, 50), font=font_th)
    draw.text((850, y + 55), "হাল তৌজি নং: ১২৪০", fill=(50, 50, 50), font=font_th)

    # Proprietor Details Box
    y += 115
    draw.rectangle([(50, y), (width - 50, y + 110)], outline=(100, 100, 100), width=1)
    draw.text((70, y + 15), "মালিকের নাম, পিতা ও ঠিকানা:", fill=(15, 60, 50), font=font_th)
    draw.text((70, y + 45), "১. মো: রফিকুল ইসলাম, পিতা: মরহুম আব্দুল কাদের, সাং: আমিনবাজার, সাভার, ঢাকা।", fill=(30, 30, 30), font=font_td)
    draw.text((70, y + 75), "অংশ (হিস্যা): ১.০০০ (সম্পূর্ণ অংশ)", fill=(40, 40, 40), font=font_td)

    # Plot Table Header
    y += 135
    cols = [
        (50, 180, "হাল দাগ নং"),
        (180, 310, "সাবেক দাগ নং"),
        (310, 510, "জমির শ্রেণী"),
        (510, 750, "দাগের মোট পরিমাণ (একর/শতক)"),
        (750, 960, "দখলীয় হিস্যা ও পরিমাণ"),
        (960, width - 50, "বাৎসরিক খাজনা ও মন্তব্য")
    ]
    draw.rectangle([(50, y), (width - 50, y + 45)], fill=(240, 240, 240), outline=(100, 100, 100), width=1)
    for x1, x2, title in cols:
        draw.line([(x1, y), (x1, y + 45)], fill=(100, 100, 100), width=1)
        draw.text(((x1 + x2) // 2, y + 12), title, fill=(30, 30, 30), font=font_th, anchor="mt")

    # Plot Table Rows
    rows = [
        ("১০৪ (104)", "৫১২", "নাল (কৃষি জমি)", "০.১২৫০ একর (১২.৫০ শতক)", "১.০০০ অংশ = ১২.৫০ শতক", "দাখিলা আদায়কৃত"),
        ("১০৫ (105)", "৫১৩", "ভিটি / বাস্তু", "০.০৮০০ একর (৮.০০ শতক)", "১.০০০ অংশ = ৮.০০ শতক", "দাখিলা আদায়কৃত")
    ]
    ry = y + 45
    for r in rows:
        draw.rectangle([(50, ry), (width - 50, ry + 50)], outline=(150, 150, 150), width=1)
        for i, (x1, x2, _) in enumerate(cols):
            draw.line([(x1, ry), (x1, ry + 50)], fill=(150, 150, 150), width=1)
            draw.text(((x1 + x2) // 2, ry + 15), r[i], fill=(30, 30, 30), font=font_td, anchor="mt")
        ry += 50

    # Total Area Summary Box
    ry += 20
    draw.rectangle([(50, ry), (width - 50, ry + 60)], fill=(248, 252, 250), outline=(100, 160, 130), width=1)
    draw.text((70, ry + 18), "খতিয়ানভুক্ত মোট দাগ সংখ্যা: ২ টি | মোট জমির পরিমাণ: ০.২০৫০ একর (২০.৫০ শতক)", fill=(15, 75, 55), font=font_h2)

    # Verification Seal
    ry = height - 200
    draw.text((100, ry), "পর্যাপ্ত তদন্তান্তে প্রস্তুতকৃত\nকানুনগো / তহশিলদার", fill=(80, 80, 80), font=font_small, align="center")
    draw.text((width - 320, ry), "সহকারী কমিশনার (ভূমি)\nসাভার উপজেলা, ঢাকা\n(ডিজিটাল ক্যাডাস্ট্রাল সার্টিফাইড)", fill=(20, 60, 50), font=font_td, align="center")

    out_path = os.path.join(OUTPUT_DIR, "sample_porcha.png")
    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated authentic porcha: {out_path}")
    return out_path

def create_authentic_pdf(deed_img_path: str):
    """Generates authentic high-res multi-page PDF using PyMuPDF."""
    doc = pymupdf.open()
    
    # Page 1: Deed rasterized at 300 DPI
    page = doc.new_page(width=595, height=842) # A4
    page.insert_image(pymupdf.Rect(20, 20, 575, 822), filename=deed_img_path)
    
    out_pdf = os.path.join(OUTPUT_DIR, "sample_khatian.pdf")
    doc.save(out_pdf)
    doc.close()
    print(f"Generated authentic PDF: {out_pdf}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    deed_path = create_authentic_deed()
    porcha_path = create_authentic_porcha()
    create_authentic_pdf(deed_path)
    print("All sample documents successfully generated!")
