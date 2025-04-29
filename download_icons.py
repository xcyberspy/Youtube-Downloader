import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Define the app's blue color
BLUE_COLOR = (34, 170, 253)  # #22AAFD in RGB

def create_enhanced_icons():
    # Ensure assets directory exists
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create YouTube logo with blue theme
    size = 200  # Larger size for better quality icons
    youtube_logo = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(youtube_logo)
    
    # Draw rounded rectangle background (blue instead of red)
    draw.rectangle([(20, 20), (size-20, size-20)], fill=BLUE_COLOR)
    
    # Add a play button (triangle) in white
    center_x, center_y = size//2, size//2
    triangle_size = size//3
    draw.polygon([
        (center_x - triangle_size//2, center_y - triangle_size//2),
        (center_x - triangle_size//2, center_y + triangle_size//2),
        (center_x + triangle_size//2, center_y)
    ], fill=(255, 255, 255))
    
    # Apply some blur for a softer effect
    youtube_logo = youtube_logo.filter(ImageFilter.GaussianBlur(1))
    
    # Save YouTube logo
    youtube_logo = youtube_logo.resize((100, 100), Image.LANCZOS)
    youtube_logo.save(os.path.join(assets_dir, "youtube_logo.png"))
    print("Created enhanced youtube_logo.png")
    
    # Create download icon with blue effect
    download_icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(download_icon)
    
    # Draw a circle background
    circle_radius = size//2 - 20
    circle_center = (size//2, size//2)
    draw.ellipse([
        (circle_center[0] - circle_radius, circle_center[1] - circle_radius),
        (circle_center[0] + circle_radius, circle_center[1] + circle_radius)
    ], fill=BLUE_COLOR)
    
    # Draw download arrow
    arrow_width = 12
    arrow_height = size//2 - 30
    # Vertical line
    draw.rectangle([
        (circle_center[0] - arrow_width//2, circle_center[1] - arrow_height//2), 
        (circle_center[0] + arrow_width//2, circle_center[1] + arrow_height//3)
    ], fill=(255, 255, 255))
    
    # Arrow head
    head_size = arrow_width * 3
    draw.polygon([
        (circle_center[0] - head_size, circle_center[1] + arrow_height//4),
        (circle_center[0] + head_size, circle_center[1] + arrow_height//4),
        (circle_center[0], circle_center[1] + arrow_height//2 + 10)
    ], fill=(255, 255, 255))
    
    # Apply blur for a softer effect
    download_icon = download_icon.filter(ImageFilter.GaussianBlur(1))
    
    # Save download icon
    download_icon = download_icon.resize((100, 100), Image.LANCZOS)
    download_icon.save(os.path.join(assets_dir, "download_icon.png"))
    print("Created enhanced download_icon.png")
    
    # Create search icon with blue accent
    search_icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(search_icon)
    
    # Draw magnifying glass circle
    glass_radius = size//3
    glass_center = (size//2 - 10, size//2 - 10)
    line_width = 12
    
    # Draw circle outline
    draw.ellipse([
        (glass_center[0] - glass_radius, glass_center[1] - glass_radius),
        (glass_center[0] + glass_radius, glass_center[1] + glass_radius)
    ], outline=BLUE_COLOR, width=line_width)
    
    # Draw the handle
    handle_length = glass_radius - 5
    handle_angle = 45  # degrees
    import math
    end_x = glass_center[0] + (glass_radius + handle_length) * math.cos(math.radians(handle_angle))
    end_y = glass_center[1] + (glass_radius + handle_length) * math.sin(math.radians(handle_angle))
    
    draw.line([
        (glass_center[0] + glass_radius * math.cos(math.radians(handle_angle)), 
         glass_center[1] + glass_radius * math.sin(math.radians(handle_angle))),
        (end_x, end_y)
    ], fill=BLUE_COLOR, width=line_width)
    
    # Apply blur for a softer effect
    search_icon = search_icon.filter(ImageFilter.GaussianBlur(1))
    
    # Save search icon
    search_icon = search_icon.resize((100, 100), Image.LANCZOS)
    search_icon.save(os.path.join(assets_dir, "search_icon.png"))
    print("Created enhanced search_icon.png")
    
    # Create folder icon
    folder_icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(folder_icon)
    
    # Draw folder body
    folder_color = BLUE_COLOR
    
    # Draw folder tab
    draw.rectangle([
        (size//4, size//4),
        (size//2, size//3)
    ], fill=folder_color)
    
    # Draw main folder
    draw.rectangle([
        (size//6, size//3),
        (size - size//6, size - size//4)
    ], fill=folder_color)
    
    # Apply some shadow
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle([
        (size//6 + 5, size//3 + 5),
        (size - size//6 + 5, size - size//4 + 5)
    ], fill=(0, 0, 0, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    
    # Composite the shadow and the folder
    folder_with_shadow = Image.alpha_composite(shadow, folder_icon)
    
    # Save folder icon
    folder_with_shadow = folder_with_shadow.resize((100, 100), Image.LANCZOS)
    folder_with_shadow.save(os.path.join(assets_dir, "folder_icon.png"))
    print("Created enhanced folder_icon.png")
    
    # Save YouTube logo as app icon
    youtube_logo.save(os.path.join(assets_dir, "app_icon.ico"))
    print("Created enhanced app_icon.ico")

if __name__ == "__main__":
    create_enhanced_icons() 