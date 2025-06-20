import re
import tldextract
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
from openai import OpenAI

def send_ai_generate_whatsapp_msg(text, lead_name):

    # using deekseek api to get msg, maybe OpenAI can be used
    client = OpenAI(api_key="sk-6139e4dce53545c5b8ccbf04eeae1f23", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        # packaging prompt words
        messages=[
            {"role": "system", "content": """
                You are a WhatsApp pre meeting bot name xmpu. Our sales team regularly communicates with potential customers from various industries. Before any meeting, we hope to provide sales representatives with a customized WhatsApp message that feels informative, relevant, and relevant to the business.
                I will provide you with a description of the website's keywords that I crawled from the website. Please help me generate a meeting message and send it to the client"""+ lead_name +""",which should not exceed 450 words. The example output is as follows:
                WhatsApp Message:
                Hi, xmpu(this is custom’s name),I had a look at your work with ExampleCompany and I love how you’re blending sustainability with tech in your logistics model. We’ve built custom AI tools for scaling that kind of workflow — would love to share ideas.
                Internal Summary:
                ExampleCompany is a London-based logistics startup focused on eco-friendly delivery. Their latest partnership with DHL signals strong expansion. They use a playful, modern brand tone. Strong alignment with our sustainable automation toolkit."""},
            {"role": "user", "content": text},
        ],
        stream=False
    )

    return response.choices[0].message.content

# scrape website content
def scrape_xiaomi_ev(company_url):
    with sync_playwright() as p:
        # startup browser
        browser = p.chromium.launch(headless=True)  # headless=True - do not open website
        page = browser.new_page()
        
        try:
            # go website
            page.goto(company_url, timeout=60000)
            print(f"successfull: {page.title()}")
            
            page.wait_for_selector("body", timeout=30000)
            time.sleep(3)  

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # del script and style
            for script in soup(["script", "style"]):
                script.extract()
                
            # get text 
            text = soup.get_text()
            # clean script
            text = re.sub(r'\s+', ' ', text).strip()

            return text
        except Exception as e:
            print(f"Error during crawling process: {e}")
        finally:
            browser.close()

# main function
def main(input_data):
    company_url = input_data.get("company_url", "")
    lead_name = input_data.get("lead_name", "customer")
    
    if not company_url:
        print("Please provide the company URL")
        return
    
    # website domain name
    extracted = tldextract.extract(company_url)
    company_name = extracted.domain
    # get website text content
    text = scrape_xiaomi_ev(company_url)
    # send to deepseek ai model, get whatsapp msg
    msg = send_ai_generate_whatsapp_msg(text, lead_name)

    print("\nGenerated WhatsApp messages:")
    print(msg)

    return {
        "whatsapp_message": company_name,
        "internal_summary": lead_name
    }

# main demo 
if __name__ == "__main__":
    example_input = {
        "company_url": "https://www.xiaomiev.com/",
        "lead_name": "Ayesha"
    }
    main(example_input)
