# Automatically find and print email addresses for automobile insurance providers in Ontario

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# Initialize Chrome WebDriver with options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # Navigate to the Ontario website
    driver.get("http://licensingcomplaintofficers.fsco.gov.on.ca/LicClass/eng/lic_companies_class.aspx")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '[+]')]"))
    )

    # Find all [+] buttons and click them to expand all sections
    expand_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), '[+]')]")
    print(f"Found {len(expand_buttons)} expandable sections")
    
    for i, button in enumerate(expand_buttons, 1):
        try:
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            print(f"Expanded section {i}/{len(expand_buttons)}")
            time.sleep(0.3)  # Small delay to allow expansion
        except Exception as e:
            print(f"Couldn't expand section {i}: {str(e)}")
            continue

    # Wait for all sections to load
    time.sleep(2)
    
    # Find all company sections (they appear as tables after expansion)
    company_tables = driver.find_elements(By.XPATH, "//table[.//td[contains(text(), 'Licence Class')]]")
    print(f"Found {len(company_tables)} company tables")

    automobile_providers = []

    for table in company_tables:
        try:
            # Get company name (text before the table)
            company_name = table.find_element(By.XPATH, "./preceding::a[1]").text
            
            # Get license classes text
            license_classes = table.find_element(By.XPATH, ".//td[contains(text(), 'Licence Class')]/following-sibling::td").text
            
            if "Automobile" in license_classes:
                # Try to find email
                try:
                    email = table.find_element(By.XPATH, ".//td[contains(text(), 'E-Mail')]/following-sibling::td").text
                except NoSuchElementException:
                    email = "Not available"
                
                automobile_providers.append({
                    "Company": company_name,
                    "Email": email,
                    "License Classes": license_classes
                })
        except Exception as e:
            print(f"Error processing table: {str(e)}")
            continue

    # Print results
    print(f"\nFound {len(automobile_providers)} automobile insurance providers:")
    for provider in automobile_providers:
        print(f"\nCompany: {provider['Company']}")
        print(f"Email: {provider['Email']}")
        # print(f"License Classes: {provider['License Classes']}")
        print("-" * 50)

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # Close the browser
    driver.quit()
