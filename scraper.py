from playwright.sync_api import sync_playwright
from playwright._impl._api_types import TimeoutError as PlaywrightTimeoutError

def run(playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.answers.com/finance/What_factors_would_be_most_likely_to_lead_to_an_unsuccessful_IPO')
    
    '''
    Rejeita os cookies. Necessário apenas na primeira página da lista de URLs.
    '''
    page.click('#onetrust-reject-all-handler', timeout=15000)
    
    '''
    Scraping the title.
    '''
    title = page.locator('xpath=//*[@id="root"]/div/div[2]/div/div[2]/div[1]/h1/a')
    title = title.text_content()
    
    while True:
        try:
            page.locator('xpath=/html/body/div[1]/div[1]/div[2]/div/div/div[2]/div/div[5]/div/button').click(timeout=10000)
        except PlaywrightTimeoutError:
            break
    
    '''
    Scraping the best answer.
    '''
    best_answer = page.locator('xpath=//*[@id="top-answer"]/div[2]/div[1]/div')
    best_answer = best_answer.text_content()
    
    '''
    Scraping all the other answers.
    '''
    answers = []
    for answer in page.locator('xpath=//*[@id="other-answers"]//*[contains(@class, "markdownStyles undefined")]').all():
        answers.append(answer.text_content())
    
    print('************')
    print('* Scraped. *')
    print('************')
    
    print(title)
    print('\n\n' + best_answer)
    for a in answers:
        print('\n\n' + a)
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
