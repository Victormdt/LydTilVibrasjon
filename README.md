Lyd til vibrasjon

En python app laget for å konvertere lyd fra datamaskinen til vibrasjoner på spillkontrolleren. Den fanger opp lyd fra venstre og høyre kanal, så man får en 3D vibrasjon. Laget for personer med redusert hørsel, og personer som vil bruke det for musikk. Den har tre moduser:

1. Bass fokus (Tar med bare bass i vibrasjonen) Velegnet for spill og musikk
2. Fullt spektrum (Tar med all lyd i vibrasjonen) Velegnet for spill for personer med redusert hørsel
3. Rytme (Tar med rytmen i musikken i vibrasjonen) Velegnet for musikk

Krav:

1. Windows 10 - 11

2. Python 3.x

3. Xbox kontoller koblet til med usb kabel, eller bluetooth.

4. Playstation Kontroller (Hvis man har program som får Playstation kontrolleren til å bruke Xinput)

Programmet kan kjøre med ps4/ps5 kontroller, men pågrunn av at playstation bruker HID protokollen, så trenger man en programvare som bytter HID til XInput protokollen, så det kan kjøre native.

En XBOX One/ eller Series X/S kjører native, og trenger ikke noen oversetter.


Installering:

1. Last ned programmet
2. pip install -r requirements.txt (Laster ned alle nødvendige avhengigheter)
3. Python controller_rumble (Starter programmet)

Under Releases ligger en exe versjon hvis man ikke vil kjøre programmet gjennom python.


Alle tilbakemeldinger tas med åpne armer, og jobber med å få MacOs og Linux port.

Victormdt 2026

