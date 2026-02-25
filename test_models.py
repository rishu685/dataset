"""
Simple script to test available Gemini models
"""
import os

def test_gemini_models():
    """Test what models are available."""
    try:
        import google.generativeai as genai
        
        # Get API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY environment variable not set")
            print("   Please set your API key: export GEMINI_API_KEY='your-key'")
            return False
            
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
            return True
        except:
            try:
                model = genai.GenerativeModel('models/gemini-pro')
                response = model.generate_content("Say hello")
                print(f"✅ gemini-pro works: {response.text}")
                return True
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Say hello")
                    print(f"✅ gemini-1.5-flash works: {response.text}")
                    return True
                except Exception as e:
                    print(f"❌ All models failed: {e}")
                    return False
                    
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini Models...")
    success = test_gemini_models()
    if success:
        print("🎉 Model testing completed successfully!")
    else:
        print("⚠️ Model testing failed. Check your setup.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini_models()