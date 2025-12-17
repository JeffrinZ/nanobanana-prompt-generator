import os
import streamlit as st
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Ideally, store this in an environment variable or a secrets file.
# For now, you can paste your key here to test.
os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI()

# ==========================================
# 2. DATA STRUCTURES (The Schema)
# ==========================================
# These classes force the AI to output the exact JSON format you want.

class Metadata(BaseModel):
    confidence_score: str
    image_type: str
    primary_purpose: str

class Composition(BaseModel):
    rule_applied: str
    aspect_ratio: str
    layout: str
    focal_points: List[str]
    visual_hierarchy: str
    balance: str

class ColorItem(BaseModel):
    color: str
    hex: str
    percentage: str
    role: str

class ColorProfile(BaseModel):
    dominant_colors: List[ColorItem]
    color_palette: str
    temperature: str
    saturation: str
    contrast: str

class Shadows(BaseModel):
    type: str
    density: str
    placement: str
    length: str

class Highlights(BaseModel):
    treatment: str
    placement: str

class Lighting(BaseModel):
    type: str
    source_count: str
    direction: str
    directionality: str
    quality: str
    intensity: str
    contrast_ratio: str
    mood: str
    shadows: Shadows
    highlights: Highlights
    ambient_fill: str
    light_temperature: str

class TechnicalSpecs(BaseModel):
    medium: str
    style: str
    texture: str
    sharpness: str
    grain: str
    depth_of_field: str
    perspective: str

class ArtisticElements(BaseModel):
    genre: str
    influences: List[str]
    mood: str
    atmosphere: str
    visual_style: str

class FacialExpression(BaseModel):
    mouth: str
    smile_intensity: str
    eyes: str
    eyebrows: str
    overall_emotion: str
    authenticity: str

class Hair(BaseModel):
    length: str
    cut: str
    texture: str
    texture_quality: str
    natural_imperfections: str
    styling: str
    part: str
    volume: str
    details: str

class HandsAndGestures(BaseModel):
    left_hand: str
    right_hand: str
    finger_positions: str
    finger_interlacing: str
    hand_tension: str
    interaction: str
    naturalness: str

class BodyPositioning(BaseModel):
    posture: str
    angle: str
    shoulders: str

class SubjectAnalysis(BaseModel):
    primary_subject: str
    positioning: str
    scale: str
    facial_expression: FacialExpression
    hair: Hair
    hands_and_gestures: HandsAndGestures
    body_positioning: BodyPositioning

class BackgroundElement(BaseModel):
    item: str
    position: str
    distance: str
    condition: str

class Surface(BaseModel):
    material: str
    surface_treatment: str = Field(description="If applicable")
    texture: str = Field(description="If applicable")
    finish: str = Field(description="If applicable")
    features: str = Field(description="If applicable")
    wear_indicators: str = Field(description="If applicable")
    # For floor/other surfaces that might be empty
    color: Optional[str] = None
    pattern: Optional[str] = None

class Background(BaseModel):
    setting_type: str
    spatial_depth: str
    elements_detailed: List[BackgroundElement]
    wall_surface: Optional[Surface]
    floor_surface: Optional[Surface]
    objects_catalog: str
    background_treatment: str

class GenerationParameters(BaseModel):
    prompts: List[str]
    keywords: List[str]
    technical_settings: str
    post_processing: str

class Typography(BaseModel):
    present: bool
    fonts: List[str]
    placement: str
    integration: str

# MAIN CONTAINER
class ImagePromptSchema(BaseModel):
    metadata: Metadata
    composition: Composition
    color_profile: ColorProfile
    lighting: Lighting
    technical_specs: TechnicalSpecs
    artistic_elements: ArtisticElements
    typography: Typography
    subject_analysis: SubjectAnalysis
    background: Background
    generation_parameters: GenerationParameters

# ==========================================
# 3. GENERATION LOGIC
# ==========================================
def generate_json_prompt(base_idea: str, lighting_override: str, style_override: str):
    
    # Construct the instruction
    system_instruction = (
        "You are an expert Photography Director and Prompt Engineer. "
        "Your goal is to take a simple user concept and expand it into a highly detailed "
        "JSON specification for image generation. "
        "You must fill EVERY field in the schema. Use creative license to invent details "
        "that match the mood."
    )

    # Combine user inputs
    user_content = f"The main concept is: '{base_idea}'."
    
    if lighting_override:
        user_content += f" NOTE: The lighting must be: {lighting_override}."
    if style_override:
        user_content += f" NOTE: The artistic style must be: {style_override}."

    # Call OpenAI with Structured Outputs
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", # Requires a recent model for structured outputs
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content},
        ],
        response_format=ImagePromptSchema,
    )

    return completion.choices[0].message.parsed

# ==========================================
# 4. THE APP UI (Streamlit)
# ==========================================
def main():
    st.set_page_config(page_title="JSON Prompt Architect", layout="wide")
    
    st.title("🎨 JSON Prompt Architect")
    st.markdown("Turn a simple idea into a **production-ready JSON spec**.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. Input")
        base_prompt = st.text_area("What do you want to see?", height=150, placeholder="e.g. A cyberpunk street food vendor in rain...")
        
        st.markdown("---")
        st.subheader("2. Overrides (Optional)")
        lighting = st.text_input("Lighting Override", placeholder="e.g. Neon, Golden Hour, Studio Flash")
        style = st.text_input("Style Override", placeholder="e.g. Photorealistic, Anime, Oil Painting")
        
        generate_btn = st.button("✨ Generate JSON", type="primary", use_container_width=True)

    with col2:
        st.subheader("3. Result")
        
        if generate_btn and base_prompt:
            try:
                with st.spinner("Expanding your imagination into data..."):
                    # Generate the data
                    result_obj = generate_json_prompt(base_prompt, lighting, style)
                    
                    # Convert to dictionary for display
                    result_json = result_obj.model_dump()
                    
                    # Display JSON with a copy button
                    st.json(result_json, expanded=True)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
        elif generate_btn and not base_prompt:
            st.warning("Please enter a prompt first!")
        else:
            st.info("Enter a prompt on the left to generate the JSON spec.")

if __name__ == "__main__":
    main()