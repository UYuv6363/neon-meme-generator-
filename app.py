import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import os
import numpy as np
from io import BytesIO

# ========== SETTINGS ==========
TEMPLATE_FOLDER = "templates"
FONT_FOLDER = "Fonts"
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
os.makedirs(FONT_FOLDER, exist_ok=True)

# ====== VIBRANT NEON UI SETUP ======
st.set_page_config(
    page_title="NEON MEME GENERATOR", 
    layout="centered",
    page_icon="🤖",
    initial_sidebar_state="collapsed"
)

# Custom CSS for vibrant neon theme with improved background
st.markdown("""
<style>
:root {
    --primary: #00aaff;
    --secondary: #ffff00;
    --accent: #ff00ff;
    --dark: #000000;
    --light: #ffffff;
    --card-bg: rgba(0, 0, 0, 0.8);
    --neon-glow: 0 0 10px var(--primary), 0 0 20px var(--secondary), 0 0 30px var(--accent);
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: var(--light);
}

.stButton>button {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    color: var(--dark) !important;
    border: none;
    border-radius: 30px;
    padding: 0.8rem 1.8rem;
    font-weight: bold;
    font-size: 1.1rem;
    box-shadow: var(--neon-glow);
    margin: 15px 0;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ====== SESSION STATE ======
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'meme_img' not in st.session_state:
    st.session_state.meme_img = None
if 'base_image' not in st.session_state:
    st.session_state.base_image = None
if 'top_text' not in st.session_state:
    st.session_state.top_text = "NEON MEME"
if 'bottom_text' not in st.session_state:
    st.session_state.bottom_text = "GENERATOR"
if 'font_size' not in st.session_state:
    st.session_state.font_size = 48
if 'font_color' not in st.session_state:
    st.session_state.font_color = "#00FFFF"
if 'outline_color' not in st.session_state:
    st.session_state.outline_color = "#FFFF00"
if 'outline_size' not in st.session_state:
    st.session_state.outline_size = 2
if 'font_file' not in st.session_state:
    st.session_state.font_file = "impact.ttf"
if 'show_templates' not in st.session_state:
    st.session_state.show_templates = False
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'meme_history' not in st.session_state:
    st.session_state.meme_history = []

# ====== HEADER ======
st.title("✨ NEON MEME GENERATOR")
st.subheader("Create Futuristic Memes in Seconds - No Design Skills Needed")

# ====== FUNCTION TO APPLY FUTURISTIC EFFECTS ======
def apply_futuristic_effects(image):
    """Apply futuristic effects to an image"""
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.5)
    blurred = image.filter(ImageFilter.GaussianBlur(radius=1.5))
    image = Image.blend(image, blurred, 0.3)
    r, g, b = image.split()
    r = r.point(lambda i: min(i * 1.3, 255))
    g = g.point(lambda i: min(i * 0.95, 255))
    b = b.point(lambda i: min(i * 1.5, 255))
    return Image.merge("RGB", (r, g, b))

# ====== IMAGE SELECTION SECTION ======
if not st.session_state.edit_mode:
    st.header("🚀 Step 1: Select Your Base Image")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Upload Your Own Image", use_container_width=True):
            st.session_state.show_templates = False
    with col2:
        if st.button("🌟 Explore Templates", use_container_width=True):
            st.session_state.show_templates = True

    if st.session_state.show_templates:
        st.subheader("🌟 Template Gallery")
        all_templates = [f for f in os.listdir(TEMPLATE_FOLDER) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
        
        if not all_templates:
            st.warning("No templates found. Please add some images to the templates folder.")
            st.stop()
        
        cols = st.columns(3)
        for idx, template in enumerate(all_templates[:9]):
            template_path = os.path.join(TEMPLATE_FOLDER, template)
            with cols[idx % 3]:
                if st.button(f"Select {template.split('.')[0]}", key=f"select_{template}"):
                    st.session_state.selected_template = template_path
                    st.session_state.base_image = Image.open(template_path)
                    st.session_state.meme_img = st.session_state.base_image.copy()
                    st.session_state.edit_mode = True
                    st.rerun()
                st.image(Image.open(template_path), use_column_width=True)
    else:
        st.subheader("📤 Upload Your Image")
        uploaded_file = st.file_uploader("Upload your image (JPG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.base_image = Image.open(uploaded_file)
            st.session_state.meme_img = st.session_state.base_image.copy()
            st.session_state.edit_mode = True
            st.rerun()

# ====== EDITING SECTION ======
if st.session_state.edit_mode and st.session_state.meme_img:
    if len(st.session_state.meme_history) == 0:
        st.session_state.meme_history.append(st.session_state.meme_img.copy())
    
    st.header("✏️ Edit Your Meme")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(st.session_state.meme_img, use_container_width=True)
    
    with col2:
        st.subheader("Text Settings")
        st.session_state.top_text = st.text_input("Top Text", st.session_state.top_text)
        st.session_state.bottom_text = st.text_input("Bottom Text", st.session_state.bottom_text)
        
        font_files = [f for f in os.listdir(FONT_FOLDER) if f.lower().endswith('.ttf')]
        if not font_files:
            st.warning("No fonts found. Using default system font.")
            default_font = "arial"
        else:
            st.session_state.font_file = st.selectbox(
                "Select Font", 
                font_files, 
                index=font_files.index(st.session_state.font_file) if st.session_state.font_file in font_files else 0
            )
        
        st.session_state.font_size = st.slider("Font Size", 20, 120, st.session_state.font_size)
        st.session_state.font_color = st.color_picker("Text Color", st.session_state.font_color)
        
        st.subheader("Outline Settings")
        st.session_state.outline_color = st.color_picker("Outline Color", st.session_state.outline_color)
        st.session_state.outline_size = st.slider("Outline Thickness", 1, 10, st.session_state.outline_size)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Regenerate Meme", use_container_width=True):
            pass
    with col2:
        if st.button("⏪ Undo", use_container_width=True) and len(st.session_state.meme_history) > 1:
            st.session_state.meme_history.pop()
            st.session_state.meme_img = st.session_state.meme_history[-1].copy()
            st.rerun()
    with col3:
        if st.button("💾 Save & Download", use_container_width=True):
            pass

# ====== MEME GENERATION ======
def generate_meme():
    """Generate meme with all selected settings"""
    if st.session_state.base_image:
        img = st.session_state.base_image.copy().convert("RGB")
    else:
        img = st.session_state.meme_img.copy().convert("RGB")
        
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(os.path.join(FONT_FOLDER, st.session_state.font_file), st.session_state.font_size)
    except:
        st.error(f"Error loading font: {st.session_state.font_file}. Using default font.")
        font = ImageFont.load_default()
    
    w, h = img.size
    
    # Function to calculate text size
    def get_text_size(text, font):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    
    # Draw top text with outline
    if st.session_state.top_text:
        text_width, text_height = get_text_size(st.session_state.top_text, font)
        
        for dx in range(-st.session_state.outline_size, st.session_state.outline_size + 1):
            for dy in range(-st.session_state.outline_size, st.session_state.outline_size + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        ((w - text_width) / 2 + dx, 20 + dy), 
                        st.session_state.top_text, 
                        font=font, 
                        fill=st.session_state.outline_color
                    )
        
        draw.text(
            ((w - text_width) / 2, 20), 
            st.session_state.top_text, 
            font=font, 
            fill=st.session_state.font_color
        )
    
    # Draw bottom text with outline
    if st.session_state.bottom_text:
        text_width, text_height = get_text_size(st.session_state.bottom_text, font)
        
        for dx in range(-st.session_state.outline_size, st.session_state.outline_size + 1):
            for dy in range(-st.session_state.outline_size, st.session_state.outline_size + 1):
                if dx != 0 or dy != 0:
                    draw.text(
                        ((w - text_width) / 2 + dx, h - text_height - 20 + dy), 
                        st.session_state.bottom_text, 
                        font=font, 
                        fill=st.session_state.outline_color
                    )
        
        draw.text(
            ((w - text_width) / 2, h - text_height - 20), 
            st.session_state.bottom_text, 
            font=font, 
            fill=st.session_state.font_color
        )
    
    img = apply_futuristic_effects(img)
    st.session_state.meme_history.append(img.copy())
    return img

# ====== GENERATE AND DOWNLOAD ======
if st.session_state.edit_mode and st.session_state.meme_img:
    if st.button("🚀 Generate Futuristic Meme", use_container_width=True, key="generate_btn"):
        with st.spinner("Creating your masterpiece..."):
            result_img = generate_meme()
            st.session_state.meme_img = result_img
            st.rerun()
    
    if st.session_state.meme_history:
        buf = BytesIO()
        st.session_state.meme_img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="📥 Download Meme",
            data=byte_im,
            file_name="neon_meme.png",
            mime="image/png",
            use_container_width=True
        )

# ====== FOOTER ======
st.markdown("---")
st.markdown("""
<footer>
    <div>
        <h4>NEON MEME GENERATOR</h4>
        <p>Create • Share • Go Viral</p>
        <p>Made with ❤️ by MINI MEDIA | #MemeMagic</p>
    </div>
</footer>
""", unsafe_allow_html=True)
