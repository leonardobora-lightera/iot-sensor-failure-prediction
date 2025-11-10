ERROR CODE
	
DESCRIPTION


1 - APPMANAGER_KP_FAIL
	
Device lost a Keep Alive (in this case confirm that keep alive fail-safe flag was increased)


2 - APPMANAGER_ALERT_FAIL
	
Device lost a Alert


3 - APPMANAGER_RETRANSMISSION_FAIL
	
Device lost a retransmission (alert or other)


4 - APPMANAGER_ERROR_MESSAGE_FAIL
	
Device lost a error message with code errors


5 - KP_UNCONFIRMED
	
Device was reset because unconfirmed kp flag reached the maximum


6 - CHIP_FAIL_IN_FIRST_CONNECTION
	
CPIN fail in initial configuration


7 - CHIP_FAIL_IN_REGIME
	
Chip not detected during registration


8 - IMSI_ICCID_FAIL_IN_FIRST_CONECTION
	
Device recognaze chip but get CIMI and QCCID fail


9 - REGISTRATION_TIMEOUT
	
Registration timeout during normal operation or APN selection


10 - QMTOPEN
	
QMTOPEN fail


11 - QMTCONNECT
	
QMTCONN fail


12 - APN_DOWNLINK_SAVED_FAIL
	
Downlink APN already saved fails, then save this error code


13 - APN_DOWNLINK_RECEIVED_FAIL
	
Downlink APN received fails in registration test, then save this error code


14 - NO_APN_FOUND
	
The APN list has been scanned 3 times in initialization, but it has not been possible to register


15 - NO_REGISTER
	
Registration during normal operation fails


16 - COMAPP_SEND
	
Publication command fail


17 - FOTA_START_FAILED
	
FOTA start failed


18 - FOTA_SEND_PACKAGE_FAILED
	
Device failed to send request for next FOTA package


19 - FOTA_RECEIVED_PACKAGE_CRC
	
Device received packet with wrong CRC


20 - FOTA_RECEIVED_PACKAGE_NUMBER
	
Device received wrong number packet


21 - FOTA_RECEIVED_PACKAGE_FLASH
	
Device failed to save packet received on external flash


22 - FOTA_FAIL_TO_SEND_ERROR_MESSAGE
	
Device failed to send FOTA error message


23 - MODEM_RESETED_IN_OPERATION
	
Modem reset asynchronously


24 – ERROR_CODE_CHIP_FAIL_TIMEOUT
	
Chip was not detected after script timeout expires


25 – ERROR_CODE_CHIP_FAIL_REQUEST_PIN
	
Chip is not working because is necessary PIN insertion


26 – ERROR_CODE_CHIP_FAIL_REQUEST_PUK:
	
Chip is not working because is necessary PUK insertion


27 – ERROR_CODE_CHIP_FAIL_STRING_READY_NOT_DETECTED
	
Chip is not working because modem parser detects "CPIN" and "OK" string, but not "READY" string


28 – ERROR_CODE_REGISTRATION_DENIED
	
Registration status (from CEREG) is 3 (denied)
 