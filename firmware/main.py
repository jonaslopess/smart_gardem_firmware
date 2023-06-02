# -*- coding: utf-8 -*-
# Importando a biblioteca para funções de data e hora
import time
from datetime import datetime, date

# Importando a biblioteca para escalonar as tarefas de leitura de dados
from apscheduler.schedulers.blocking import BlockingScheduler

# Importando a biblioteca GPIO
import RPi.GPIO as GPIO

# Importando a biblioteca para o sensor de umidade e temperatura e conversor ADC
import Adafruit_DHT
import Adafruit_MCP3008 as mcp

# Importando a biblioteca para interagir com o smart contract
from web3 import Web3, HTTPProvider
import json

# Importando a biblioteca de registros de dados local
from bd_tools import BancoDeDados

# Importando a bibliote para o controlador fuzzy
# Necessária instalação !pip install scikit-fuzzy
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Importando a bibliote para ler as configurações
from dotenv import load_dotenv
import os
load_dotenv()

# Provedor RPC para conexão com a rede de teste
RPC_URL = os.getenv('RPC_URL')

# Enderoço e ABI do smart contract na rede de teste
ADDRESS = os.getenv('ADDRESS')
with open('../contract/abi.json') as f:
    ABI = json.load(f)

# Conta e chave privada do dispositivo
ACCOUNT = os.getenv('ACCOUNT')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Conexão com o banco de dados
bd = BancoDeDados(nome="../database/banco.db")

# Configurando as portas de entrada e saída
AIR_TH = Adafruit_DHT.DHT11
AIR_TH_PIN = 4

SOLO1 = 0
SOLO2 = 1
SOLO3 = 2
LUMINOSIADE = 3

RELE_LUZ = 18
RELE_AGUA = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(RELE_LUZ, GPIO.OUT)
GPIO.output(RELE_LUZ, GPIO.LOW)

GPIO.setup(RELE_AGUA, GPIO.OUT)
GPIO.output(RELE_AGUA, GPIO.LOW)

ADC = mcp.MCP3008(clk=11, cs=8, miso=9, mosi=10)

# Definindo a função de configuração do controlador fuzzy
def fuzzy_config():
    air_temp = ctrl.Antecedent(np.arange(0, 51, 1), 'air_temp')
    air_h = ctrl.Antecedent(np.arange(0, 101, 1), 'air_humidity')
    s_moisture = ctrl.Antecedent(np.arange(0, 61, 1), 'soil_moisture')
    balance = ctrl.Antecedent(np.arange(0, 121, 1), 'balance')
    pumping = ctrl.Consequent(np.arange(0,12,1), 'pumping')
    
    s_moisture ['dry'] = fuzz.trapmf(s_moisture.universe, [0,0,10,20])
    s_moisture ['moderate'] = fuzz.trapmf(s_moisture.universe, [10,20,30,40])
    s_moisture ['wet'] = fuzz.trapmf(s_moisture.universe, [30,40,60,60])

    air_h ['low'] = fuzz.trapmf(air_h.universe, [0, 0, 50, 70])
    air_h ['high'] = fuzz.trapmf(air_h.universe, [50, 70, 100, 100])

    air_temp ['cool'] = fuzz.trapmf(air_temp.universe, [0,0,22,34])
    air_temp ['hot'] = fuzz.trapmf(air_temp.universe, [22,34,50,50])

    balance ['little'] = fuzz.trapmf(balance.universe, [0,0,25,45])
    balance ['average'] = fuzz.trapmf(balance.universe, [25,45,75,95])
    balance ['much'] = fuzz.trapmf(balance.universe, [75,95,120,120])

    pumping ['very short'] = fuzz.trapmf(pumping.universe, [0,0,1,3])
    pumping ['short'] = fuzz.trapmf(pumping.universe, [1,3,5,6])
    pumping ['average'] = fuzz.trapmf(pumping.universe, [5,6,8,9])
    pumping ['long'] = fuzz.trapmf(pumping.universe, [8,9,11,11])

    rule1 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['wet'] & balance['much'],pumping['short'])
    rule2 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['wet'] & balance['much'],pumping['very short'])
    rule3 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['wet'] & balance['much'],pumping['short'])
    rule4 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['wet'] & balance['much'],pumping['short'])
    rule5 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['moderate'] & balance['much'],pumping['average'])
    rule6 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['moderate'] & balance['much'],pumping['short'])
    rule7 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['moderate'] & balance['much'],pumping['average'])
    rule8 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['moderate'] & balance['much'],pumping['average'])
    rule9 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['dry'] & balance['much'], pumping['long'])
    rule10 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['dry'] & balance['much'], pumping['long'])
    rule11 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['dry'] & balance['much'], pumping['long'])
    rule12 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['dry'] & balance['much'], pumping['long'])
    rule13 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['wet'] & balance['little'],pumping['very short'])
    rule14 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['wet'] & balance['little'],pumping['very short'])
    rule15 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['wet'] & balance['little'],pumping['very short'])
    rule16 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['wet'] & balance['little'],pumping['very short'])
    rule17 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['moderate'] & balance['little'], pumping['short'])
    rule18 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['moderate'] & balance['little'],pumping['very short'])
    rule19 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['moderate'] & balance['little'],pumping['short'])
    rule20 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['moderate'] & balance['little'],pumping['very short'])
    rule21 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['dry'] & balance['little'], pumping['average'])
    rule22 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['dry'] & balance['little'], pumping['short'])
    rule23 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['dry'] & balance['little'], pumping['average'])
    rule24 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['dry'] & balance['little'], pumping['short'])
    rule25 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['wet'] & balance['average'], pumping['short'])
    rule26 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['wet'] & balance['average'], pumping['very short'])
    rule27 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['wet'] & balance['average'], pumping['short'])
    rule28 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['wet'] & balance['average'], pumping['very short'])
    rule29 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['moderate'] & balance['average'], pumping['average'])
    rule30 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['moderate'] & balance['average'], pumping['short'])
    rule31 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['moderate'] & balance['average'], pumping['average'])
    rule32 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['moderate'] & balance['average'], pumping['short'])
    rule33 = ctrl.Rule(air_h['low'] & air_temp['hot'] & s_moisture['dry'] & balance['average'], pumping['long'])
    rule34 = ctrl.Rule(air_h['high'] & air_temp['hot'] & s_moisture['dry'] & balance['average'], pumping['average'])
    rule35 = ctrl.Rule(air_h['low'] & air_temp['cool'] & s_moisture['dry'] & balance['average'], pumping['long'])
    rule36 = ctrl.Rule(air_h['high'] & air_temp['cool'] & s_moisture['dry'] & balance['average'], pumping['average'])

    sistema_controle = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24,rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35, rule36])
    return ctrl.ControlSystemSimulation(sistema_controle)

# Definição da funções auxiliares    
def checarTempUmidAr():
    umidade, temperatura = Adafruit_DHT.read_retry(AIR_TH, AIR_TH_PIN)
    # if umidade is not None and temperatura is not None:
    #     print ("Temperatura = {0:0.1f}  Umidade = {1:0.1f}".format(temperatura, umidade))
    # else:
    #umidade, temperatura = 60, 21.0
    if umidade is None or temperatura is None:
        print("Falha ao ler dados do DHT11 !!!")
    return umidade, temperatura

def checarUmidadeSolo():
    #umidade = ADC.read_adc(SOLO1)
    # print("Sensor SM1: ", umidade1 )
    #umidade2 = ADC.read_adc(SOLO2)
    # print("Sensor SM2: ", umidade2 )
    # umidade3 = ADC.read_adc(SOLO3)
    # print("Sensor SM3: ", umidade3 )
    #umidade = (umidade1 + umidade2) / 2
    umidade = 850
    umidade = umidade *(-0.195) + 200
    return umidade

def checarLuminosidade():
    luz = ADC.read_adc(LUMINOSIADE)
    # print("Sensor LDR: ", luz )
    # luz = 512
    return 100-(luz/10.24)

def checaSaldo():
    web3 = Web3(HTTPProvider(RPC_URL))
    contract = web3.eth.contract(address=ADDRESS, abi=ABI)

    start = time.time()
    value = contract.functions.getBalance().call()
    end=time.time()

    # bd.conecta()
    # bd.inserir_transaction_log(tx_hash="",type="getBalance",delay=end-start, cost=0, msg="value:"+str(value) )
    # bd.desconecta()
    
    return value
    
def irrigacao(tempo_irrigacao):
    while tempo_irrigacao > 0:
        # print("Irrigação Ligada")
        GPIO.output(RELE_AGUA,GPIO.HIGH)
        time.sleep(1)
        tempo_irrigacao = tempo_irrigacao - 1
    # print("Irrigação Desligada")
    GPIO.output(RELE_AGUA,GPIO.LOW)

def ligarIluminacao():
    GPIO.output(RELE_LUZ, 1)
    return

def desligarIluminacao():
    GPIO.output(RELE_LUZ, 0)
    return

def uptade_monitored_property(property, value):
    web3 = Web3(HTTPProvider(RPC_URL))
    contract = web3.eth.contract(address=ADDRESS, abi=ABI)
    nonce = web3.eth.get_transaction_count(ACCOUNT)
    start = time.time()
    tx_dict = contract.functions.setMonitoringValue(
        property,
        value
    ).build_transaction({
        'gas' : 2100000,
        'gasPrice' : web3.eth.gas_price,
        'nonce' : nonce,
    })

    signed_tx = web3.eth.account.sign_transaction(tx_dict, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    end=time.time()
    
    bd.conecta()
    bd.inserir_transaction_log(tx_hash=str(tx_hash),type="setMonitoringValue",delay=end-start, cost=tx_receipt['gasUsed'], msg="property:"+str(property)+",value:"+str(value) )
    bd.desconecta()

def get_current_value(property):
    web3 = Web3(HTTPProvider(RPC_URL))
    contract = web3.eth.contract(address=ADDRESS, abi=ABI)

    #start = time.time()
    value = contract.functions.getMonitoringValue(property).call()
    #end=time.time()

    # bd.conecta()
    # bd.inserir_transaction_log(tx_hash="",type="getMonitoringValue",delay=end-start, cost=0, msg="property:"+str(property)+",value:"+str(value) )
    # bd.desconecta()
    
    return value


def registro_contrato(property, value):
    current_value = get_current_value(property)
    diff = (abs(current_value)*0.2) if current_value != 0 and abs(current_value) >= 5 else 1.0
    range = [current_value-diff, current_value+diff]
    print(f"Sensor value: {value}")
    print(f"Current registered value: {current_value}")
    if(value < range[0] or value > range[1]):
        print(f"Registring {property} value change.")
        uptade_monitored_property(property,int(value))
    else:
        print("No significant change. Skipping registration...")


def registro(dados):
    # for i in range(1,len(dados)):
    #     dados[i] = format(dados[i],'.2f')
    # Registrando dados no arquivo dados.csv
    # with open('dados.csv', 'a', encoding='UTF8', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(dados)
    
    # client = iota_client.Client()
    # dados_utf = (",".join(dados)).encode("utf8")
    # message = client.message(index=MSG_ID, data=dados_utf)

    registro_contrato('temperature',dados[1])
    registro_contrato('humidity',dados[2])
    registro_contrato('light',dados[3])
    registro_contrato('moisture',dados[4])

    bd.conecta()
    bd.inserir_monitoring_log(
        dados[0],
        dados[1],
        dados[2],
        dados[3],
        dados[4],
        dados[5],
        dados[6]
    )
    bd.desconecta()

def leitura():
    lumin = checarLuminosidade()
    umid_ar, temp_ar = checarTempUmidAr()
    umid_solo = checarUmidadeSolo()
    saldo_deposito = checaSaldo()
    data_hora = datetime.now()
    tempo_irrigacao = 0
    print("Data e hora atuais: "+str(data_hora))
    dados = [data_hora, temp_ar, umid_ar, lumin, umid_solo, saldo_deposito,tempo_irrigacao]
    return dados

def checarIrrgacao(controlador):
    dados = leitura()
    controlador.input['air_temp'] = dados[3]
    controlador.input['air_humidity'] = dados[2]
    controlador.input['soil_moisture'] = dados[1]
    controlador.input['balance'] = dados[5]
    controlador.compute()
    tempo_irrigacao = int(controlador.output['pumping'])
    irrigacao(tempo_irrigacao)
    dados[6] = tempo_irrigacao
    registro(dados)

def monitoramento():
    registro(leitura())



def backup():
    #current_date = date.today()
    bd.conecta()
    bd.get_backup(f'../database/backupdatabase_dump.sql')
    bd.desconecta()




# Procedimento principal
def main():
    current_hour = datetime.now().hour
    if current_hour >= 8 and current_hour <= 20:
        ligarIluminacao()
    monitoramento()
    controlador = fuzzy_config()

    scheduler = BlockingScheduler()
    scheduler.add_job(monitoramento, 'interval', hours=1)
    print("Agendada a leitura a cada interval de 1 hora")
    scheduler.add_job(checarIrrgacao, args=[controlador], trigger='cron', hour=8)
    scheduler.add_job(ligarIluminacao, args=[], trigger='cron', hour=8)
    print("Agendada a irrigação para as 8 horas")
    scheduler.add_job(checarIrrgacao, args=[controlador], trigger='cron', hour=14)
    print("Agendada a irrigação para as 14 horas")
    scheduler.add_job(checarIrrgacao, args=[controlador], trigger='cron', hour=20)
    scheduler.add_job(desligarIluminacao, args=[], trigger='cron', hour=20)
    print("Agendada a irrigação para as 20 horas")
    scheduler.add_job(backup, args=[], trigger='cron', day_of_week='fri', hour='23') 
    scheduler.start()

if __name__ == "__main__":
    main()