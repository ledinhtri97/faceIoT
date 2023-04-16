// Add the LCD library.
#include <LiquidCrystal_I2C.h>

// Initialize "LiquidCrystal_I2C" for the monitor LCD with the following config.
LiquidCrystal_I2C lcd(
    0x27, // address I2C is 0x27.
    16,   // With 16 columns.
    2     // With 2 rows.
);

const int SENSOR_OBSTACLE = A0;
const int TIME_DELAY = 1000;
const int MAX_TIMES_SHOW = 5;
const String EMPTY_LINE_16C = "                ";

int valueSensor = -1;
int countShow = 0;
String nameGuest;

void setup()
{
  Serial.begin(9600);
  pinMode(SENSOR_OBSTACLE, INPUT);

  // Start up the library.
  lcd.init();

  // Clear the screen, making sure there is no old content left before.
  lcd.clear();

  // Turn on the screen backlight.
  lcd.backlight();

  // At column 1, row 1, print the content...
  lcd.setCursor(0, 0);
  lcd.print("IoT Demo");

  // At column 1, row 2, print the content...
  lcd.setCursor(0, 1);
  lcd.print("TriLD");

  // Wait 3 TIME_DELAYs.
  delay(TIME_DELAY * 3);

  // Clear the screen.
  lcd.clear();

  // At column 1, row 1, print the content...
  lcd.setCursor(0, 0);
  lcd.print("OBSTACLE:");
}

void lcdshow(String text) {
  lcd.setCursor(0, 1);
  lcd.print(text);
  countShow += 1;
}

void loop()
{
  // Increase the count by 1 unit.
  valueSensor = analogRead(SENSOR_OBSTACLE);
  Serial.print("#s0!");
  Serial.println(valueSensor);

  // At column 8, row 1, print the content...
  lcd.setCursor(10, 0);
  lcd.print("     ");
  lcd.setCursor(10, 0);
  lcd.print(valueSensor);

  if (Serial.available()) {
    String commands = Serial.readString();
    int lastcmdIndex = commands.lastIndexOf('$');
    String cmd = commands.substring(lastcmdIndex + 1);
    
    int separatorIndex = cmd.indexOf('|');
    String functionName = cmd.substring(0, separatorIndex);
    String argument = cmd.substring(separatorIndex + 1);

    Serial.println(argument);

    if (countShow >= MAX_TIMES_SHOW && functionName == "lcdshow") {
      countShow = 0;
      nameGuest = argument;
      lcd.setCursor(0, 1);
      lcd.print(EMPTY_LINE_16C);
      lcdshow(nameGuest);
    }
  }

  if (countShow < MAX_TIMES_SHOW) {
    lcdshow(nameGuest);
  }
  else {
    if (countShow == MAX_TIMES_SHOW) {
      lcd.setCursor(0, 1);
      lcd.print(EMPTY_LINE_16C);
      countShow = MAX_TIMES_SHOW + 1; //make sure that no wellcome anymore and no clean text
    }
  }

  // Wait for TIME_DELAY ms to count continue.
  delay(TIME_DELAY);
}
