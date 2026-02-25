"""
Test script to verify Gemini AI integration
Run this to check if your setup is working correctly
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_setup():
    """Test if Gemini API is properly configured."""
    print("🧪 Testing Gemini AI Setup...")
    
    try:
        import google.generativeai as genai
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ Gemini libraries installed successfully")
        
        # Check API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY not found in environment variables")
            print("   You can still enter it in the Streamlit app")
            return False
        
        # Test API connection
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        response = model.generate_content("Hello, this is a test. Respond with 'AI test successful!'")
        print("✅ Gemini API connection successful!")
        print(f"   Response: {response.text}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("   Check your API key at https://ai.google.dev/")
        return False

def test_data_loading():
    """Test if dataset loads correctly."""
    print("📊 Testing dataset loading...")
    
    try:
        from download_data import load_titanic_data
        df = load_titanic_data()
        print(f"✅ Dataset loaded successfully: {len(df)} rows")
        return True
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        return False

def test_backend_components():
    """Test if backend components work."""
    print("⚙️ Testing backend components...")
    
    try:
        from backend.data_analyzer import TitanicAnalyzer
        analyzer = TitanicAnalyzer()
        stats = analyzer.get_basic_stats()
        print("✅ Data analyzer working")
        
        from backend.agent import TitanicAgent
        agent = TitanicAgent()
        print("✅ AI agent initialized")
        
        # Test a simple query
        result = agent.process_query("How many passengers were there?")
        print(f"✅ Query processing works: {result['answer'][:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Backend component error: {e}")
        return False

if __name__ == "__main__":
    print("🚢 Titanic Chatbot - System Test\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_data_loading():
        tests_passed += 1
    
    if test_gemini_setup():
        tests_passed += 1
    
    if test_backend_components():
        tests_passed += 1
    
    print(f"\n📈 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All systems working! You're ready to use the chatbot.")
    else:
        print("⚠️ Some issues found. Check the errors above.")
        
        if tests_passed >= 2:
            print("💡 The app should still work, but with limited AI features.")
    
    print("\n🚀 To start the app, run: ./start.sh")