"""
Simple script to test available Gemini models
"""
import os

def test_gemini_models():
    """Test what models are available."""
    try:
        import google.generativeai as genai
        
        api_key = "AIzaSyA5_WY-wpsa45mv5PmfvHz_iZaaSuP2SsE"
        genai.configure(api_key=api_key)
        
        # List available models
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Test the most basic model
        try:
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            response = model.generate_content("Say hello")
            print(f"✅ gemini-1.5-pro-latest works: {response.text}")
        except:
            try:
                model = genai.GenerativeModel('models/gemini-pro')
                response = model.generate_content("Say hello")
                print(f"✅ gemini-pro works: {response.text}")
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Say hello")
                    print(f"✅ gemini-1.5-flash works: {response.text}")
                except Exception as e:
                    print(f"❌ All models failed: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini_models()