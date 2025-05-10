#include <Arduino.h>


// UART2 (PA3 = RX, PA2 = TX)
HardwareSerial mdSerial(PA10, PA9);
// HardwareSerial sigma(PA9, )



void setup() {

  mdSerial.begin(38400);



}

void loop() {
  mdSerial.write("skibidi");

  delay(5000); // wait before next loop
}
