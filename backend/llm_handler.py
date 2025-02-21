import google.generativeai as genai

# Set your Gemini API Key
GEMINI_API_KEY = "AIzaSyDTrB6VrFWeT6TlyFkAa50sh35TZau_TyY"
genai.configure(api_key=GEMINI_API_KEY)

def generate_text(prompt):
    # Use the appropriate Gemini model
    model = genai.GenerativeModel("gemini-pro")
    
    # Craft a prompt that explicitly asks for a good title
    title_prompt = f"Generate a concise and catchy title for an advertisement based on this description: {prompt}"
    
    # Generate the title using the model
    response = model.generate_content(title_prompt)
    return response.text.strip()  # Strip whitespace for cleaner output

