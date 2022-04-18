//DAS System

//Variables
int trigPin=13; //Sensor Trig pin connected to Arduino pin 13
int echoPin=11;  //Sensor Echo pin connected to Arduino pin 11
float pingTime;  //time for ping to travel from sensor to target and return
float targetDistance; //Distance to Target in inches
float speedOfSound=776.5; //Speed of sound in miles per hour when temp is 77 degrees.

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);// baud rate specification
  
  pinMode(trigPin, OUTPUT);//set to OUTPUT
  pinMode(echoPin, INPUT); //set to INPUT
  
  delay(1000);//Wait before accessing Sensor
}
void loop(){
  // put your main code here, to run repeatedly:
  
  digitalWrite(trigPin, LOW); //Set trigger pin low
  delayMicroseconds(2000); //Let signal settle
  
  digitalWrite(trigPin, HIGH); //Set trigPin high
  delayMicroseconds(15); //Delay in high state
  
  digitalWrite(trigPin, LOW); //ping has now been sent
  delayMicroseconds(10); //Delay in low state
  
  pingTime = pulseIn(echoPin, HIGH);  //pingTime is presented in microceconds
  
  pingTime=pingTime/1000000; //convert pingTime to seconds by dividing by 1000000 (microseconds in a second)
  
  pingTime=pingTime/3600; //convert pingtime to hours by dividing by 3600 (seconds in an hour)
  
  targetDistance= speedOfSound * pingTime;  //This will be in miles, since speed of sound was miles per hour
  
  targetDistance=targetDistance/2; //Remember ping travels to target and back from target, so you must divide by 2 for actual target distance.
  
  targetDistance= targetDistance*63360;    //Convert miles to inches by multipling by 63360 (inches per mile)
  
  targetDistance=targetDistance/39.87;//In meters for our DAS 
  
  Serial.println(targetDistance); 
  
  delay(1000); //delay tenth of a  second to slow things down a little.
}


/*
 Functions used :
 Serial.begin : baud rate of 9600 bps(bit per sec) for communication with the serial monitor
 pinMode : configures the pin as either Input or Output
 pulseIn : Reads a pulse (either HIGH or LOW) on a pin. 
           For example, if value is HIGH, pulseIn() waits for the pin to go from LOW to HIGH, starts timing, then waits for the pin to go LOW and stops timing.
           Returns the length of the pulse in microseconds or gives up and returns 0 if no complete pulse was received within the timeout.
 delay : time difference in seconds or milliseconds or mircoseconds
 digitalWrite : digital output of either a HIGH or LOW to that pin
*/
