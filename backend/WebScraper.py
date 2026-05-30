import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from io import StringIO

# from dotenv import load_dotenv
from dotenv import dotenv_values
import os

old_price = []
diff = []
old_html = ""
(
    username,
    password,
    login_url,
    cookie_file,
    refresh_interval,
    data_output,
    screenshot_ouput,
    screenshot_resolution,
    screenshot_url,
) = [""] * 9
credentials = ()
username_key = {}


def main():
    unpack_python_config()
    loggedout = True

    print("SCRAPER STARTED")
    print("Writing to:", data_output)

    while True:

        if loggedout:
            login(cookie_file, credentials, login_url)
            loggedout = False

        try:
            cookies = get_cookies(cookie_file)
            # for some reason when downloading the html and if a room is overbooked, the price for the overbooked room become NaN, this should be fixed when match_room_price
            r = requests.get(login_url, cookies=cookies)
            html_content = r.text
            # with open("oldhtml.html", "r", encoding="utf-8") as f:
            #     html_content = f.read()
            global old_html
            if old_html != html_content:  # Only update if change is detected
                parsed_html, pass_on_dict = parse_html(html_content)
                all_data_json = data_to_json(parsed_html)
                all_data_json.append(pass_on_dict)

                with open(data_output, "w") as f:
                    json.dump(all_data_json, f, indent=4)

                formatted_time = datetime.now().strftime("%H:%M:%S")
                print("Last Updated " + formatted_time)
                # Example output: 12:10:00
                old_html = html_content

                try:
                    driver = run_headless(screenshot_resolution)
                    shot_width = int(
                        screenshot_resolution[14 : screenshot_resolution.find(",")]
                    )
                    shot_height = int(
                        screenshot_resolution[screenshot_resolution.find(",") + 1 :]
                    )
                    # print(shot_width, shot_height)
                    driver.execute_cdp_cmd(
                        "Emulation.setDeviceMetricsOverride",
                        {
                            "width": shot_width,
                            "height": shot_height,
                            "deviceScaleFactor": 1,
                            "mobile": False,
                        },
                    )
                    driver.get(screenshot_url)
                    time.sleep(2)
                    driver.save_screenshot(screenshot_ouput)

                except Exception as e:
                    print(f"An error occurred: {e}")

                finally:
                    # Always close the browser
                    driver.quit()

            time.sleep(refresh_interval)

        except AttributeError as ae:
            print(f"Error: {ae}")
            print("Logged out, cookies expired. Cookies need to be updated")
            loggedout = True

        except json.decoder.JSONDecodeError as jd:
            print(f"Error: {jd}")
            print("Cookies.env file is empty or wrong format")
            loggedout = True

        except requests.exceptions.ConnectTimeout as ct:
            print(f"Error: {ct}")
            print("Too many request, Attempting to relog")
            loggedout = True

        except IndexError as ie:
            print(f"Error: {ie}")
            print(
                "NO DATA. Failed to import old data to preserve difference data EEPROM, continuing as a fresh installation with no old data"
            )
            print("Relogging in to fetch data")
            loggedout = True
            
        except KeyError as ke:
            print(f"Error: {ie}")
            print(
                "INCOMPLETE DATA. Failed to import old data to preserve difference data EEPROM, continuing as a fresh installation with no old data"
            )
            print("Relogging in to fetch data")
            loggedout = True


        # except Exception as ex:
        #     print(f"Error: {ex}")
        #     print("New error, idk what this is yet.")
        #     loggedout = True


def unpack_python_config():
    global username, password, login_url, cookie_file, refresh_interval, data_output, screenshot_ouput, screenshot_resolution, screenshot_url, credentials, username_key
    with open("./config/python_settings.json") as f:
        settings = json.load(f)

    credentials_dot = dotenv_values(settings["credentials_file_path"])
    username = credentials_dot["USER"]
    password = credentials_dot["PASSWORD"]
    login_url = credentials_dot["LOGIN_URL"]
    credentials = (username, password)

    cookie_file = settings["cookies_file_path"]
    refresh_interval = settings["scraper_refresh_interval"]
    data_output = settings["data_output_path"]
    screenshot_ouput = settings["screenshot_save_path"]
    screenshot_resolution = settings["screenshot_resolution"]
    screenshot_url = settings["screenshot_URL"]

    username_key = dotenv_values(settings["usernames_file_path"])


def run_headless(resolution):
    options = Options()
    options.add_argument("--headless=new")  # modern headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(resolution)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options)

    return driver


def login(cookie_file, credentials, login_url):
    driver = run_headless("--window-size=1920,1080")
    driver.get(login_url)
    print("Opened new chrome window")
    time.sleep(2)

    cookie_accept = driver.find_element(By.CLASS_NAME, "prominent-btn")
    cookie_accept.click()
    print("Clicked Continue")
    time.sleep(2)

    user_field = driver.find_element(By.ID, "input28")
    print("Selected username field")
    user_field.send_keys(credentials[0])
    print("Entered username")
    time.sleep(2)

    user_btn = driver.find_element(By.CLASS_NAME, "button-primary")
    user_btn.click()
    print("Hit Next")
    time.sleep(2)

    pass_field = driver.find_element(By.ID, "input62")
    print("Selected password field")
    pass_field.send_keys(credentials[1])
    print("Entered password")
    time.sleep(2)

    pass_btn = driver.find_element(By.CLASS_NAME, "button-primary")
    pass_btn.click()
    print("Hit Verify")
    time.sleep(5)

    cookies_json = driver.get_cookies()
    print("Grabbed Cookies")
    with open(cookie_file, "w") as outfile:
        json.dump(cookies_json, outfile, indent=4)
    print("Dumped Cookies")

    driver.quit()


def get_cookies(cookie_file):
    with open(cookie_file, "r") as json_file:
        cookies_dict = json.load(json_file)

    cookies = {
        cookies_dict[0]["name"]: cookies_dict[0]["value"],
        cookies_dict[2]["name"]: cookies_dict[2]["value"],
        cookies_dict[1]["name"]: cookies_dict[1]["value"],
    }
    return cookies


def parse_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for a in soup.find_all("a"):
        a.unwrap()

    for form in soup.find_all("form"):
        form.decompose()

    for button in soup.find_all("button"):
        button.decompose()

    summ_data = soup.find("div", "col-summary")
    # if summ_data == None:
    #     loggedout = True
    for tr in summ_data.find_all("tr"):
        tr["class"] = ["summary-card"]

    avail_data = soup.find("div", "col-availability")
    for tr in avail_data.find_all("tr"):
        tr["class"] = ["avail-card"]

    pass_data = soup.find("div", "col-pass-on-log")

    groups_data = soup.find("div", "col-groups")
    for tr in groups_data.find_all("tr"):
        tr["class"] = ["group-card"]

    header = "<!doctype html>\
    <html>\
    \
    <head></head>\
    <body>"

    footer = "</body>\
        </html>"

    all_data_html = (
        header
        + str(summ_data)
        + str(avail_data)
        + str(groups_data)
        + str(pass_data)
        + footer
    )

    pass_on_dict = []

    for i in range(len(pass_data.find_all("i"))):
        pass_on_dict.append(
            {
                "title": pass_data.find_all("span", "col-title")[i].contents[0],
                "timestamp": pass_data.find_all("i")[i]
                .contents[0]
                .replace("\n", "")
                .replace("\t", "")
                .replace("    ", " ")
                .strip(),
                "message": pass_data.find_all("span", "col-text-system-message")[
                    i
                ].contents[0],
            }
        )

    add_employee_names(pass_on_dict)

    return all_data_html, pass_on_dict


def add_employee_names(pass_on_dict):
    for pass_on in pass_on_dict:
        user_code = pass_on["timestamp"].split()[0]
        if (
            user_code in username_key
        ):  # Check if the username has been mapped in Employee_username file, pass if not
            employee = username_key[user_code]
            pass_on["timestamp"] = pass_on["timestamp"].replace(user_code, employee)
        # print(pass_on)

    # print(pass_on_dict)


def data_to_json(parsed_html):
    extract_data = pd.read_html(StringIO(parsed_html))
    all_data_json = []

    extract_data = fix_avail_dataset(None, extract_data, True)

    for i, df in enumerate(extract_data):

        if i == 0:
            # summary dataset
            df.columns = ["value", "label"]
            df = df[["label", "value"]]
            df = df[:-2]

        # availability dataset
        elif i == 1:
            df = fix_avail_dataset(df, None, False)
            df.columns = ["count", "room", "price"]
            df = match_room_price(df)
            df = save_old_price(df)

        elif i == 2:
            # group dataset (header row issue)
            df.columns = df.iloc[0]  # set first row as header
            df = df[1:]  # remove header row

        all_data_json.append(df.to_dict(orient="records"))

    return all_data_json


def format_currency(amount):
    """Formats a float as a currency string (e.g., -$1,234.56)."""
    # Format the absolute value with commas and two decimal places
    formatted_amount = f"$ {abs(amount):,.2f}"
    # Prepend a minus sign if the original amount was negative
    if amount < 0:
        return f"-{formatted_amount}"
    return formatted_amount


# Makes sure the avail dataset always has 4 rows and will add default values if rows are missing
def fix_avail_dataset(df, extract_data, stepOne):
    avail_dummy = [
        {0: 0, 1: "KNS", 2: "$ 0.00"},
        {0: 0, 1: "QQNS", 2: "$ 0.00"},
        {0: 0, 1: "KHC", 2: "$ 0.00"},
        {0: 0, 1: "QQHC", 2: "$ 0.00"},
    ]
    if stepOne:
        if len(extract_data[1].columns) != 3:
            extract_data.insert(1, pd.DataFrame(avail_dummy))

        return extract_data

    avail_dict = df.to_dict(orient="records")
    for i, d in enumerate(avail_dummy):
        if len(avail_dict) <= i:
            avail_dict = avail_dict + avail_dummy[i:]
            # print("reached!")
            break
        elif len(avail_dict) == 4:
            break
        # print(len(avail_dict), i)
        # print(d[1], avail_dict[k][1])
        if avail_dict[i][1] != d[1]:
            avail_dict.insert(i, d)
    # print("old df:", df)
    df = pd.DataFrame(avail_dict)
    # print("new df:", df)
    return df


def is_json_file_empty(file_path):
    # 1. Check if file is physically empty (0 bytes)
    if os.path.getsize(file_path) == 0:
        return True

    # 2. Check if the file contains empty JSON structures (like {} or [])
    with open(file_path, "r") as file:
        try:
            data = json.load(file)
            # Returns True if data evaluates to an empty dict/list/string
            return not data
        except json.JSONDecodeError:
            # Handles files that have broken JSON or whitespace only
            return True


# Saves the previous price for rooms and calulcates the difference.
# Also adds 2 new columns for old price and difference in price to the dataset
def save_old_price(df):
    global old_price
    global diff

    # if os.path.isfile(data_output):
    #     print(data_output, )

    # If script has restarted and there is old data present (in data.json), recalculate the the old price and inject it into old_price
    if (
        old_price == []
        and os.path.isfile(data_output)
        and not is_json_file_empty(data_output)
    ):
        with open(data_output) as f:
            old_json_data = json.load(f)

        # Calculate the old price from old data and reinsert it into global old_price to preserve difference data
        for room_type in old_json_data[1]:
            # print(room_type)
            temp_old_price = float(room_type["old price"][2:])
            temp_diff = float(room_type["diff"][1:])
            real_old_price = format_currency(temp_old_price - temp_diff)
            # print(real_old_price)
            old_price.append(real_old_price)

        diff = [
            format_currency(float(p[2:]) - float(old_price[j][2:]))
            for j, p in enumerate(df["price"].tolist())
        ]

        df["old price"] = old_price

    elif old_price == []:
        old_price = df["price"].tolist()
        diff = [
            format_currency(float(p[2:]) - float(old_price[j][2:]))
            for j, p in enumerate(df["price"].tolist())
        ]
        df["old price"] = old_price

    if old_price != df["price"].tolist():
        # print("new price", df["price"].tolist())
        # print("old_price", old_price)
        # print("displayed_old_price1", displayed_old_price)
        # temp_list = df["price"].tolist()
        df["old price"] = old_price
        for i, newPrice in enumerate(df["price"].tolist()):
            newPriceFloat = float(newPrice[2:])
            old_priceFloat = float(old_price[i][2:])
            if newPriceFloat == 0:
                pass
                # temp_list[i] = old_price[i]
                # print("newPrice", newPrice)
                # print(df["price"].tolist()[i])
            elif newPriceFloat != old_priceFloat:
                # print(old_priceFloat, newPriceFloat, i)
                if old_priceFloat != 0:
                    diff[i] = format_currency(newPriceFloat - old_priceFloat)
                old_price[i] = newPrice
            else:
                old_price[i] = newPrice

        # df["price"] = temp_list
    else:
        df["old price"] = old_price

    df["diff"] = diff
    # print("displayed_old_price2", displayed_old_price)

    return df


def match_room_price(df):

    global old_price

    curr_count = df["count"].tolist()
    curr_price = df["price"].tolist()
    # print(curr_count, curr_price)

    # pair maps regular room and hadicap room together
    pair_map = {0: 2, 2: 0, 1: 3, 3: 1}

    for i in range(len(curr_count)):
        getPairIndex = pair_map.get(i)
        # print("i=", i, "\ncurr_count[i]=", curr_count[i], "\ngetpairindex=", getPairIndex, "\n", curr_count[getPairIndex])
        """check if both handicap and regular rooms are fully/OVER booked, if so take the old price"""
        if curr_count[i] <= 0 and curr_count[getPairIndex] <= 0 and old_price:
            curr_price[i] = old_price[i]
            curr_price[getPairIndex] = old_price[getPairIndex]
        # the current room is fully/OVER booked and its pair isnt, take the current price from the pair
        elif curr_count[i] <= 0:
            curr_price[i] = curr_price[getPairIndex]
        # if (float(curr_old[i][2:]) != float(curr_old[getPairIndex][2:])) and float(
        #     curr_price[i][2:]
        # ) == 0:
        #     curr_price[i] = curr_price[getPairIndex]
        #     curr_diff[i] = curr_diff[getPairIndex]
        #     curr_old[i] = curr_old[getPairIndex]
        # # elif float(curr_price[i][2:]) == float(curr_price[getPairIndex][2:]):
        # elif float(curr_price[i][2:]) == 0 and float(curr_price[getPairIndex][2:]) == 0:
        #     curr_price[i] = old_price[i]
        #     curr_price[getPairIndex] = old_price[getPairIndex]

        df["price"] = curr_price
    return df


if __name__ == "__main__":
    main()
