#!/usr/bin/env python3
"""
Generate default medicine type images for the pharmacy system.
Creates professional, color-coded placeholder images for different medicine types.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create the directory if it doesn't exist
image_dir = "static/HealthStack-System/images/medicine-types"
os.makedirs(image_dir, exist_ok=True)

def create_medicine_image(medicine_type, color, icon_shape, filename):
    """Create a professional medicine type image with specific shapes"""
    
    # Image settings
    width, height = 200, 200
    bg_color = color
    
    # Create image with white background
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    center = (width // 2, height // 2)
    
    # Draw specific shapes for each medicine type
    if icon_shape == "tablet":
        # Draw tablet shape (rounded rectangle)
        tablet_width, tablet_height = 80, 50
        left = center[0] - tablet_width // 2
        top = center[1] - tablet_height // 2
        right = left + tablet_width
        bottom = top + tablet_height
        draw.rounded_rectangle([left, top, right, bottom], radius=15, fill=bg_color, outline=(0,0,0,100), width=2)
        # Add center line
        draw.line([center[0], top + 5, center[0], bottom - 5], fill=(255,255,255,150), width=2)
        
    elif icon_shape == "bottle":
        # Draw syrup bottle shape
        # Bottle body
        bottle_width, bottle_height = 60, 90
        left = center[0] - bottle_width // 2
        top = center[1] - bottle_height // 2 + 10
        right = left + bottle_width
        bottom = top + bottle_height
        draw.rounded_rectangle([left, top, right, bottom], radius=8, fill=bg_color, outline=(0,0,0,100), width=2)
        
        # Bottle neck
        neck_width = 20
        neck_left = center[0] - neck_width // 2
        neck_right = neck_left + neck_width
        neck_top = top - 20
        draw.rectangle([neck_left, neck_top, neck_right, top], fill=bg_color, outline=(0,0,0,100), width=2)
        
        # Cap
        cap_width = 25
        cap_left = center[0] - cap_width // 2
        cap_right = cap_left + cap_width
        cap_top = neck_top - 8
        draw.rounded_rectangle([cap_left, cap_top, cap_right, neck_top], radius=3, fill=(100,100,100), outline=(0,0,0,100), width=1)
        
    elif icon_shape == "capsule":
        # Draw capsule shape
        capsule_width, capsule_height = 80, 40
        left = center[0] - capsule_width // 2
        top = center[1] - capsule_height // 2
        right = left + capsule_width
        bottom = top + capsule_height
        
        # Left half
        draw.pieslice([left, top, left + capsule_height, bottom], 90, 270, fill=bg_color, outline=(0,0,0,100), width=2)
        # Right half  
        light_color = tuple(min(255, c + 60) for c in bg_color)
        draw.pieslice([right - capsule_height, top, right, bottom], 270, 90, fill=light_color, outline=(0,0,0,100), width=2)
        # Center rectangle
        draw.rectangle([left + capsule_height//2, top, right - capsule_height//2, bottom], fill=bg_color, outline=None)
        
    elif icon_shape == "syringe":
        # Draw syringe shape
        # Barrel
        barrel_width, barrel_height = 15, 70
        barrel_left = center[0] - barrel_width // 2
        barrel_top = center[1] - barrel_height // 2
        barrel_right = barrel_left + barrel_width
        barrel_bottom = barrel_top + barrel_height
        draw.rectangle([barrel_left, barrel_top, barrel_right, barrel_bottom], fill=bg_color, outline=(0,0,0,100), width=2)
        
        # Needle
        needle_width = 3
        needle_left = center[0] - needle_width // 2
        needle_right = needle_left + needle_width
        needle_top = barrel_top - 30
        draw.rectangle([needle_left, needle_top, needle_right, barrel_top], fill=(150,150,150), outline=(0,0,0,100), width=1)
        
        # Plunger
        plunger_width = 20
        plunger_left = center[0] - plunger_width // 2
        plunger_right = plunger_left + plunger_width
        plunger_top = barrel_bottom
        plunger_bottom = plunger_top + 15
        draw.rectangle([plunger_left, plunger_top, plunger_right, plunger_bottom], fill=(100,100,100), outline=(0,0,0,100), width=2)
        
    elif icon_shape == "tube":
        # Draw ointment tube
        # Tube body
        tube_width, tube_height = 45, 80
        left = center[0] - tube_width // 2
        top = center[1] - tube_height // 2 + 10
        right = left + tube_width
        bottom = top + tube_height
        draw.rounded_rectangle([left, top, right, bottom], radius=5, fill=bg_color, outline=(0,0,0,100), width=2)
        
        # Cap
        cap_width = 30
        cap_left = center[0] - cap_width // 2
        cap_right = cap_left + cap_width
        cap_top = top - 20
        draw.rounded_rectangle([cap_left, cap_top, cap_right, top], radius=3, fill=(100,100,100), outline=(0,0,0,100), width=2)
        
    elif icon_shape == "dropper":
        # Draw dropper bottle
        # Bottle
        bottle_size = 50
        bottle_left = center[0] - bottle_size // 2
        bottle_top = center[1] - bottle_size // 2 + 10
        bottle_right = bottle_left + bottle_size
        bottle_bottom = bottle_top + bottle_size
        draw.ellipse([bottle_left, bottle_top, bottle_right, bottle_bottom], fill=bg_color, outline=(0,0,0,100), width=2)
        
        # Dropper
        dropper_width = 3
        dropper_left = center[0] - dropper_width // 2
        dropper_right = dropper_left + dropper_width
        dropper_top = bottle_top - 25
        draw.rectangle([dropper_left, dropper_top, dropper_right, bottle_top], fill=(100,100,100), outline=(0,0,0,100), width=1)
        
        # Drop
        draw.ellipse([center[0]-3, dropper_top-8, center[0]+3, dropper_top-2], fill=bg_color)
        
    else:  # general
        # Draw general medicine symbol (cross)
        cross_size = 60
        cross_width = 15
        
        # Horizontal bar
        h_left = center[0] - cross_size // 2
        h_top = center[1] - cross_width // 2
        h_right = center[0] + cross_size // 2
        h_bottom = center[1] + cross_width // 2
        draw.rounded_rectangle([h_left, h_top, h_right, h_bottom], radius=5, fill=bg_color)
        
        # Vertical bar
        v_left = center[0] - cross_width // 2
        v_top = center[1] - cross_size // 2
        v_right = center[0] + cross_width // 2
        v_bottom = center[1] + cross_size // 2
        draw.rounded_rectangle([v_left, v_top, v_right, v_bottom], radius=5, fill=bg_color)
    
    # Add label
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    label_text = medicine_type.title()
    bbox = draw.textbbox((0, 0), label_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = center[0] - text_width // 2
    text_y = height - 25
    draw.text((text_x, text_y), label_text, fill=(50,50,50), font=font)
    
    # Save image
    img.save(f"{image_dir}/{filename}")
    print(f"Created: {image_dir}\\{filename}")

# Medicine type configurations with proper shapes
medicine_types = [
    ("tablets", (52, 152, 219), "tablet", "tablets.png"),      # Blue tablets
    ("syrup", (231, 76, 60), "bottle", "syrup.png"),           # Red bottle 
    ("capsules", (230, 126, 34), "capsule", "capsules.png"),   # Orange capsules
    ("injection", (192, 57, 43), "syringe", "injection.png"),  # Dark red syringe
    ("ointment", (46, 204, 113), "tube", "ointment.png"),      # Green tube
    ("lotion", (46, 204, 113), "tube", "lotion.png"),          # Green tube (same as ointment)
    ("drops", (155, 89, 182), "dropper", "drops.png"),         # Purple dropper
    ("general", (149, 165, 166), "general", "general.png"),    # Gray cross
]

print("🎨 Generating professional medicine type images...")
print("=" * 50)

for medicine_type, color, shape, filename in medicine_types:
    create_medicine_image(medicine_type, color, shape, filename)

print(f"\n✅ Created {len(medicine_types)} medicine type images!")
print(f"� Location: {image_dir}")