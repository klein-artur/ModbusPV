# Modbus PV

Modbus PV is an implementation of a Solar (Photovoltaik) overview panel, based on an raspberry pi and it's official display.
The connection to the PV happens through Modbus TCP, hence the name. 
Other connections, for example to a forecast api are also integrated. Please be aware that this is a very quick and dirty implementation, so 
do not throw with stones. Better give it your own signature by contributing and make it better. I will have a look over each pullrequest. Maybe this can get something big. Maybe not. My idea was intentionally to use it just for me and my family. I know there are solutions out there, but none did fit to exactly what I need... At the end I think some can contribute to this, especially to the Modbus TCP connection to my Huawei PV.

Whoever is interested just in the Modbus Part, have a look at "The Modbus Connection"

## So what is the goal

My goal was, to have a panel, where everyone can read, very very simple, if it makes sense to start some consumption heavy device, like the laundry dryer or the dishwasher. If it makes sense to wait some hours or maybe a whole day... Everything should be real time (not the five minutes resolution from the fusionsolar api). That's why I choosed to connect to modbus directly. 

The panel is the default Raspberry Pi display with an Raspberry Pi 4. The whole UI is web based and chromium is opened in kiosk mode. The Websites sizes are hardcoded to fit on that screen. 
At the top, just six bars are visible, showing the current situation and the situation over the next six hours. 

## The Modbus Connection

The heart of this whole thing is the modbus connection to the PV (currently only Huawei Inverters (SUN2000-10KTL-*something*) are implemented. I see no need for me to implement other, so feel free to do it). There is a python file called "Server.py" which holds an endless loop, reading data from the PV and doing what needs to be done with it. 

To have modbus TCP running, you have to have it activated on the inverters side. Talk to your installation guy, if you do not know where.

The Modbus connection happens through https://github.com/riptideio/pymodbus, mainly in the files Server/huawei/ModbusDataReader.py and Server/huawei/ModbusTCPReader.py. Again. Feel free to make interfaces and make it configurable however you want.

The data readen from the modbus interface are then combined with some forecast data from https://rapidapi.com/stromdao-stromdao-default/api/solarenergyprediction/ (you will need an account). And all of this is saved in an sqlite database.

## The API

On top of all of this is a very simple API, mimicing a RESTFull API. This is the part where I did the most "it is just for me" job. So do your thing and make it a good API... All files are in "apiv1"

## The UI
The UI itself is just a webpage, accessing the API to get data. I for myself also implemented an apple watch app to have access to the data through this API. Maybe I will also make that repo public... 

## Device Control
The system can control devices based on how much power the PV is producing. Currently only Shelly Smart Plugs are implemented. Code is in `DeviceControl.py` and the config for the devices is in `deviceconfig.json`.

## Forecasting
To fetch forecasts this implementation uses the `SolarEnergyPrediction` API from https://www.stromdao.de on RapidAPI https://rapidapi.com/stromdao-stromdao-default/api/solarenergyprediction/

## I am not responsible for this mess!!
Please be aware that I will not guarantee that this does not destroy anything... The Modbus connection is just reading data, but who knows what can happen.. 

# Installation and Starting

 - Have some MySQL server. There are tons of tutorials how to install one on raspberry pi. 
 - Install pymodbus (https://github.com/riptideio/pymodbus).
 - Copy the `config_excample.py` file from the `Server` directory, call the copy `config.py` and add your data there. **DO NOT ADD THIS TO THE REPO, IT CONTAINS PRIVATE DATA!**
 - Copy the `mysqlconfig_example.py` file from the `Server/db` directory, call it `mysqlconfig.py`. Add your database infos there. Also do not add this to the repo. 
 - Copy the `deviceconfig_example.json` file from the `Server` directory. call the copy `deviceconfig.json`. Add your devices to control there. Currently only Shelly Smart Plugs are implemented. **DO NOT ADD THIS TO THE REPO, IT CONTAINS PRIVATE DATA!**
 - Copy the `config_example.php` file from the `apiv1` directory and call it `config.php`. Change the values to fit your needs. Do also not add this to the repo.

 ## Starting:
 If you only want the server to run, it is enough to start the `Server.py` file and serve the `apiv1` or `apiv2` through any webserver.
 If you want to start the whole system, call `launchModbusPV.py`. It will start the server and the UI by opening chromium in kiosk mode. 

 # Next Steps

 I have some basic ideas what next steps will come:

 - Make the whole UI responsive.
