import google.generativeai as genai

# Test API key
genai.configure(api_key="AIzaSyCqFcdFkAXS49SWQHtU0iWmGBqzbb-hOCs")
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)