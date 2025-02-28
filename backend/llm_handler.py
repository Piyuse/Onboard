import google.generativeai as genai

# Set your Gemini API Key
GEMINI_API_KEY = "AIzaSyDTrB6VrFWeT6TlyFkAa50sh35TZau_TyY"
genai.configure(api_key=GEMINI_API_KEY)

def generate_text(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    title_prompt = f"Generate a compelling, attention-grabbing, and relevant title for an advertisement based on the description. Ensure it is concise, engaging, and aligns with the target audience: {prompt}"

    
    # Generate the title using the model
    response = model.generate_content(title_prompt)
    return response.text.strip()  

