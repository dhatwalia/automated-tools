import calendar
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

def create_calendar_wallpaper():
    # Get current month and year
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Create a calendar that starts with Sunday
    cal = calendar.Calendar(firstweekday=6)  # 6 = Sunday
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Wallpaper dimensions for MacBook Air M1 (2560x1600)
    width, height = 2560, 1600
    
    # Create black background
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    # Font paths for macOS
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    
    # Try to load fonts
    title_font = None
    day_font = None
    date_font = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                if title_font is None:
                    title_font = ImageFont.truetype(font_path, 100)
                if day_font is None:
                    day_font = ImageFont.truetype(font_path, 55)
                if date_font is None:
                    date_font = ImageFont.truetype(font_path, 50)
                break
            except:
                continue
    
    # Fallback to default font if no system fonts found
    if title_font is None:
        title_font = ImageFont.load_default()
        day_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # Make calendar slightly smaller
    cal_width = width * 0.75
    cal_height = height * 0.65
    cal_x = (width - cal_width) // 2
    cal_y = (height - cal_height) // 2
    
    # Draw month title (centered at top)
    title = f"{month_name} {year}"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, cal_y - 100), title, fill='white', font=title_font)
    
    # Day names starting with Sunday
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    day_width = cal_width // 7
    
    for i, day in enumerate(days):
        x = cal_x + i * day_width + day_width // 2
        day_bbox = draw.textbbox((0, 0), day, font=day_font)
        day_text_width = day_bbox[2] - day_bbox[0]
        draw.text((x - day_text_width // 2, cal_y + 15), day, fill='white', font=day_font)
    
    # Dates with smaller cells
    cell_height = (cal_height - 80) // 6
    
    for week_idx, week in enumerate(month_days):
        for day_idx, day in enumerate(week):
            if day != 0:  # 0 means day doesn't belong to this month
                x = cal_x + day_idx * day_width + day_width // 2
                y = cal_y + 80 + week_idx * cell_height + cell_height // 2
                
                date_bbox = draw.textbbox((0, 0), str(day), font=date_font)
                date_text_width = date_bbox[2] - date_bbox[0]
                date_text_height = date_bbox[3] - date_bbox[1]
                draw.text((x - date_text_width // 2, y - date_text_height // 2), 
                         str(day), fill='white', font=date_font)
    
    # Add subtle grid lines for better readability
    # Horizontal lines between weeks
    for i in range(1, 7):
        y_pos = cal_y + 80 + i * cell_height
        draw.line([(cal_x, y_pos), (cal_x + cal_width, y_pos)], fill='#333333', width=1)
    
    # Vertical lines between days
    for i in range(1, 7):
        x_pos = cal_x + i * day_width
        draw.line([(x_pos, cal_y + 80), (x_pos, cal_y + cal_height)], fill='#333333', width=1)
    
    # Outer border for the calendar
    draw.rectangle([(cal_x, cal_y + 80), (cal_x + cal_width, cal_y + cal_height)], 
                  outline='#444444', width=2)
    
    # Save the image
    filename = f"{year}-{month_name}.png"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
    image.save(desktop_path)
    print(f"Sunday-starting calendar wallpaper saved to your Desktop as: {filename}")
    print("Set it as your wallpaper through System Preferences > Desktop & Screen Saver")
    
    # Optional: Display the image
    # image.show()

if __name__ == "__main__":
    create_calendar_wallpaper()
