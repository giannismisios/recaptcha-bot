from distutils.debug import DEBUG
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from image_downloader import load_image_from_url
from model import predict_image_label
from wordnet import get_most_similar_label, thresholds_for_label, labels_from_model
from image_splitter import split_image

from image_downloader import download_image
import logging
import time
import configparser

logging.basicConfig()
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
config = configparser.ConfigParser()
config.read('config.ini')
pathtodriver = config['SELENIUM']['pathtodriver']
logger.debug('Path to webdriver is %s',pathtodriver)
#TODO: add comments
#TODO: rerender image when it's only one left delay
#TODO: double press of skip
driver = webdriver.Chrome(pathtodriver)

'''
The verify function clicks the verification button
'''
def verify():
    try:
        button = driver.find_element_by_id('recaptcha-verify-button')
        logger.debug('%s to be clicked',button.text)
        button.click()
    except:
        button = driver.find_element_by_id('recaptcha-verify-button')
        logger.debug('%s to be clicked',button.text)
        button.click()

'''
The skip function clicks the skip button
'''
def skip():
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID,'recaptcha-reload-button')))
        logger.debug('%s to be clicked',button.text)
        button.click()
    except:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID,'recaptcha-reload-button')))
        logger.debug('%s to be clicked in catch',button.text)
        button.click()
'''
The skip function clicks the skip button
'''        
def check_for_pending_images():
    time.sleep(2)
    text = driver.find_elements(By.XPATH, "//div[starts-with(@class, 'rc-imageselect-error-') or @class='rc-imageselect-incorrect-response']")
    result = [el.text  for el in text if el.text ]
    return result[0] if len(result) != 0 else ''  

'''
Clicks the specified tile
'''
def click_tile(index):
    tile_el = driver.find_elements_by_class_name('rc-imageselect-tile')
    logger.debug("%s to be clicked",tile_el[index])
    tile_el[index].click()

'''
This function iterates through all the the images and uses the model to get the predictions. If needed 
it repeats multiple times till the riddle is solved
'''
def solve_for_tiles(tiles, active_labels, dimension, multi_select):
    i = 0
    clicked = []
    not_selected = []
    total_scores = {}
    for tile in tiles:
        logger.info("tile number one %s predicting... ",str(i))
        scores = predict_image_label(tile)
        thresholds = {label:thresholds_for_label[label] for label in active_labels[0]}
        logger.debug("Thresholds are %s", thresholds)
        prediction = [scores[index]> thresholds[label] for index,label in zip(active_labels[1],active_labels[0])]
        logger.info("Prediction %s", prediction)
        if any(prediction):
            logger.info("tile %s is {}".format(' '.join(map(str,active_labels[0]))),str(i))
            click_tile(i)
            clicked.append(i)
        else:
            not_selected.append(i)
        total_scores[i] = [scores[index] for index in active_labels[1]]
        i+=1
    logger.debug("The following were not selected %s",not_selected)
    if not multi_select: 
        logger.debug("Total scores %s", total_scores)
        return not_selected, total_scores
    while len(clicked) !=0 and multi_select:
        if len(clicked) == 1:
            time.sleep(2)
        tile_el = driver.find_elements_by_class_name('rc-imageselect-tile')
        new_clicked = []
        for clic in clicked: 
            image = tile_el[clic].find_element_by_tag_name('img')
            url = image.get_attribute("src")
            logger.debug("url of image is %s",url)
            loaded_image = load_image_from_url(url)
            scores = predict_image_label(loaded_image)
            prediction = [scores[index]> thresholds[label] for index,label in zip(active_labels[1],active_labels[0])]
            if any(prediction):
                logger.info("tile %s is {}".format(' '.join(map(str,active_labels[0]))),str(i))
                click_tile(clic)
                new_clicked.append(clic)
            else:
                total_scores[clic] = [scores[index] for index in active_labels[1]]
        clicked = new_clicked
        logger.debug("Total scores %s", total_scores)
    return None, total_scores



def find_most_likely(unselected, total_scores):
    if unselected:
        max_scores = {index:max(score) for index, score in total_scores.items() if index in unselected}
    else:
        max_scores = {index:max(score) for index,score in total_scores.items()}
    
    
    maximum = 0
    index_of_maximun = -1

    for ind,score in max_scores.items():
        if score> maximum:
            index_of_maximun = ind
            maximum = score
    logger.info("Maximum probability %s to belong to the labels has tile number %s", maximum, index_of_maximun)
    return index_of_maximun

def render_new_element(ind, active_labels):
    tile_el = driver.find_elements_by_class_name('rc-imageselect-tile')
    image = tile_el[ind].find_element_by_tag_name('img')
    url = image.get_attribute("src")
    logger.debug("url of image is %s",url)
    loaded_image = load_image_from_url(url)
    scores = predict_image_label(loaded_image)
    return [scores[index] for index in active_labels[1]]

def solve():
    prev_title = None
    while True:
        time.sleep(2)
        title = driver.find_element(By.CSS_SELECTOR,"div.rc-imageselect-desc-no-canonical, div.rc-imageselect-desc")
        while title == prev_title:
            title = driver.find_element(By.CSS_SELECTOR,"div.rc-imageselect-desc-no-canonical, div.rc-imageselect-desc")
        prev_title = title
        task = title.text
        task = task.split('\n')
        logger.info("task is %s", task)
        if task[0].startswith('Select all images with'):
            break
        skip()
    labels_to_find = task[1].split(' or ')

    active_labels = get_most_similar_label(labels_to_find)
    logger.info("Active labels are %s", active_labels[0])
    if len(active_labels[0]) == 0:
        skip()
        return solve()
    image_tiles = driver.find_element(By.XPATH,"//img[starts-with(@class,'rc-image-tile')]")

    image_class = image_tiles.get_attribute("class")
    dimension = int(image_class[-1])
    image_url = image_tiles.get_attribute("src")
    download_image(image_url, 'images/image.jpeg')
    tiles = split_image("images/image.jpeg",dimension)
    unselected, total_scores = solve_for_tiles(tiles,active_labels,dimension, len(task)==3)
    verify()
    result = check_for_pending_images()
    refresh = False
    while True:
        
        if not result or result == 'Please try again.':
            return result
        if (result == 'Please select all matching images.' and len(task) == 3) or result == 'Please also check the new images.':
            if refresh:
                total_scores[ind] = render_new_element(ind, active_labels)
            ind = find_most_likely(unselected, total_scores)
            click_tile(ind)
            refresh=True
            verify()
            result = check_for_pending_images()
        elif result == 'Please select all matching images.':
            ind = find_most_likely(unselected, total_scores)
            click_tile(ind)
            unselected.remove(ind)
            verify()
            result = check_for_pending_images()
        else:
            logger.error('something went wrong with result was %s ',result)
            break


suc = 0
TOTAL = config['SELENIUM']['totalruns']
for i in range(int(TOTAL)):
    try:
        driver.get("http://localhost:8000/")
        driver.implicitly_wait(30)
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.recaptcha-checkbox-border"))).click()
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[starts-with(@name, 'c-') and starts-with(@src, 'https://www.google.com/recaptcha')]")))
        logger.debug("iframe located")
        result = solve()
        while result == 'Please try again.':
            result = solve()
        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")))
        element = driver.find_element(By.CLASS_NAME, 'recaptcha-checkbox-border')
        if element.get_attribute('style') :
            suc+=1
            logger.info("Recaptcha solved %s/%s",suc,i+1)
    except:
        logger.error("Failed to resolve recaptcha")
    finally:
        try:
            driver.quit()  
        except:
            logger.warn("Couldn't quit driver")  
        driver = webdriver.Chrome(pathtodriver)
    driver.quit()
logger.info("%s/%s success rate",suc, TOTAL)