from playwright.sync_api import sync_playwright
from playwright._impl._api_types import TimeoutError as PlaywrightTimeoutError

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

import json
import jsonlines

user_agent_rotator = UserAgent(limit=1000)

def run(playwright, urls):
    chromium = playwright.chromium
    browser = chromium.launch(headless=True)
    
    for url in urls:
        
        print(f'Scraping {url} ...')
        
        context = browser.new_context(user_agent=user_agent_rotator.get_random_user_agent())
        page = context.new_page()
        page.goto(url)
        
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
        
        print(f'\033[1;32mScraped\033[1;0m: {url}')
        
        data = json.dumps({
            'title': title,
            'answers': [best_answer] + answers
        })
        
        with jsonlines.open('data.jsonl', mode='a') as writer:
            writer.write(data)
        
        context.close()
    
    browser.close()

with sync_playwright() as playwright:
    urls = ['https://www.answers.com/finance/What_did_managers_and_owners_want_for_their',
            'https://www.answers.com/general-science/What_part_of_the_red_blood_cell_gives_it_the_color_red',
            'https://math.answers.com/general-science/What_the_formula_for_caculating_density',
            'https://www.answers.com/general-science/Inquiry_is_a_process_prompted_by_a']
    run(playwright, urls)
