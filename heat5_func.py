
import time
import datetime
import os
import undetected_chromedriver as uc
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def enviar_para_telegram(caminho_imagem, legenda, chat_id, context):
    try:
        with open(caminho_imagem, 'rb') as img:
            context.bot.send_photo(chat_id=chat_id, photo=img, caption=legenda)
            print("✅ Imagem (HEAT) enviada.")
    except Exception as e:
        print("❌ Erro ao enviar imagem (HEAT):", e)

def tirar_screenshot_heatmap(ativo_base="ETH", exchange="Binance", chat_id=None, context=None, cancelado=None):
    if cancelado and chat_id in cancelado and cancelado[chat_id]:
        context.bot.send_message(chat_id=chat_id, text="❌ Processo cancelado. Voltando ao início...")
        return

    tempo_total = time.time()
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://www.coinglass.com/pro/futures/LiquidationHeatMap")
        try:
            wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[contains(text(),'Hyperliquid Whale Tracker')]/following-sibling::div//button"
            ))).click()
        except:
            pass

        input_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'MuiAutocomplete-input')]")))
        input_box.click()
        time.sleep(0.2)
        input_box.send_keys(ativo_base)
        time.sleep(1.0)

        opcoes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@role='option']")))
        encontrados = []
        for i in range(len(opcoes)):
            try:
                opcoes_atualizadas = driver.find_elements(By.XPATH, "//li[@role='option']")
                texto = opcoes_atualizadas[i].text.strip()
                if texto.startswith(f"{exchange} {ativo_base}"):
                    encontrados.append(texto)
            except Exception as e:
                print(f"⚠️ Ignorado item corrompido no autocomplete: {e}")

        if not encontrados:
            context.bot.send_message(chat_id=chat_id, text=f"❌ Nenhum par encontrado para {ativo_base}. Aguarde...")
            return

        par = encontrados[0]
        for op in opcoes:
            try:
                if op.text.strip() == par:
                    op.click()
                    break
            except:
                continue

        wait.until(EC.presence_of_element_located((By.XPATH, "//canvas")))
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(3.0)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nome_formatado = par.replace(" ", "_").replace("/", "_").lower()
        original_file = f"heatmap_full_{nome_formatado}_{timestamp}.png"
        cropped_file = f"heatmap_{nome_formatado}_{timestamp}.png"
        driver.save_screenshot(original_file)

        imagem = Image.open(original_file)
        imagem_cortada = imagem.crop((282, 93, 1943, 876))
        imagem_cortada.save(cropped_file)
        imagem_cortada.close()

        legenda = f"🔥 {par} Heatmap – {timestamp}"
        enviar_para_telegram(cropped_file, legenda, chat_id, context)

    finally:
        driver.quit()
        print(f"✅ Finalizado em {time.time() - tempo_total:.2f}s")
