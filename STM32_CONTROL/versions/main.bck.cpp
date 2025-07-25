#include <Arduino.h>


// VARS
const int MD1200BAUDS = 38400;  // From what I've read it is always 38400
//const int EPYSLEEPY = 600000;  / 10 minutes
const int EPYSLEEPY = 300000;  // 5 minutes
//const int EPYSLEEPY = 150000;  // 2,5 minutes

// declarations
int getTemp();
int setFanTrsh(int);

void setup() {
  // Setup connection to MD1200
  // Serial1 because we're using RX/TX pins
  Serial1.begin(MD1200BAUDS);

  // Just debug
  Serial.begin(9600);
}

void loop() {

  int fanPercnt = getTemp();
  
  if (fanPercnt < 10) {
    setFanTrsh(fanPercnt);
  }

  /* 
  check temperature and
  set fan speed every X minutes
  */
  delay(EPYSLEEPY);

}

// Get current temperature 
int getTemp() {

  int bp1 = 0;
  int bp2 = 0;
  int exp0 = 0;
  int exp1 = 0;
  int simm0 = 0;
  int simm1 = 0;
  String MD1200output;
  
  Serial1.println("_temp_rd");

  // wait for MD1200 to answer
  delay(30);
  
  while (Serial1.available()) {
    MD1200output = Serial1.readStringUntil('\n');

    // Check backplane 1
    if (MD1200output.startsWith("BP_1")) {
        // check index number of =
        int eq = MD1200output.indexOf('=');
        // check index number of c
        int c = MD1200output.indexOf('c');
        // check if both exists
        if (eq != -1 && c != -1) {
          /* 
          take value between "= " and "c". 
          NOTICE that eq + 1 is there because in 
          "BP_1[2] = 25c" there is a space between = and 25.
          */
          bp1 = MD1200output.substring(eq + 1, c).toInt();
        }
    }

    // Check backplane 2
    if (MD1200output.startsWith("BP_2")) {
      int eq = MD1200output.indexOf('=');
      int c = MD1200output.indexOf('c');
      if (eq != -1 && c != -1) {
        bp2 = MD1200output.substring(eq + 1, c).toInt();
      }
    }

    // Uncomment if you want to also get temperature for expanders
    /*

    // Check expander 0
    if (MD1200output.startsWith("EXP0")) {
      int eq = MD1200output.indexOf('=');
      int c = MD1200output.indexOf('c');
      if (eq != -1 && c != -1) {
        exp0 = MD1200output.substring(eq + 1, c).toInt();
      }
    }

    // Check expander 1
    if (MD1200output.startsWith("EXP1")) {
      int eq = MD1200output.indexOf('=');
      int c = MD1200output.indexOf('c');
      if (eq != -1 && c != -1) {
        exp1 = MD1200output.substring(eq + 1, c).toInt();
      }
    }

    // Check controller 0
    if (MD1200output.startsWith("SIM0")) {
      int eq = MD1200output.indexOf('=');
      int c = MD1200output.indexOf('c');
      if (eq != -1 && c != -1) {
        simm0 = MD1200output.substring(eq + 1, c).toInt();
      }
    }

    // Check controller 1
    if (MD1200output.startsWith("SIM1")) {
      int eq = MD1200output.indexOf('=');
      int c = MD1200output.indexOf('c');
      if (eq != -1 && c != -1) {
        simm1 = MD1200output.substring(eq + 1, c).toInt();
      }
    }

    */

    // Stop when prompt returns
    if (MD1200output.endsWith(">")) {
      break;
    }
  }

  // Do (BP_1 + BP_2) / 2 to get the average of backplane
  if (bp1 != -1 && bp2 != -1) {
    int bpAvg = (bp1 + bp2) / 2;

    // define default
    int outPrcntg = 21;

    // a 
    switch (bpAvg) {
      case 23:
        outPrcntg = 21;
        break;
        // Minimum is 21 (akhsually 20)
      case 25:
        outPrcntg = 23;
        break;
      case 27:
        outPrcntg = 24;
        break;
      case 29:
        outPrcntg = 26;
        break;
      case 31:
        outPrcntg = 27;
        break;
      case 33:
        outPrcntg = 30;
        break;
      case 35:
        outPrcntg = 34;
        break;
      case 37:
        outPrcntg = 38;
        break;
        /*
          I don't wan't to become deaf so max is 40.
        */ 
      
      default:
        return -1;
    
    }

    return outPrcntg;

  } else {
    return -1; // failed to read temp
  }

  /*
  BP_1[2] - Back plane, maybe left 
  BP_2[3] - Back plane, maybe right
  SIM0[0] - Controller A 
  SIM1[1] - Controller B
  EXP0[4] - Expander 0
  EXP1[5] - Expander 1

  AVG - average of all sensors
  */
}

// take percentage as int and set it.
int setFanTrsh(int fanTrshInp) {
  String outputStatement = "set_speed " + String(fanTrshInp);

  Serial.println("Sending " + outputStatement + " to MD1200");

  if (Serial1.println(outputStatement)) {
    return 1;
  }
  else {
    return -1;
  }

}