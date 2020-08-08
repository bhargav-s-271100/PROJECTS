# import curses and GPIO
import curses
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

# set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BOARD)

I1 = 7
I2 = 11
En1 = 12

I3 = 13
I4 = 16
En2 = 32

GPIO.setup(I1, GPIO.OUT)
GPIO.setup(I2, GPIO.OUT)
GPIO.setup(En1, GPIO.OUT)
GPIO.setup(I3, GPIO.OUT)
GPIO.setup(I4, GPIO.OUT)
GPIO.setup(En2, GPIO.OUT)

# Get the curses window, turn off echoing of keyboard to screen, turn on
# instant (no waiting) key response, and use special values for cursor keys
screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.halfdelay(3)
screen.keypad(True)

enable1 = GPIO.PWM(En1, 1000)  # create PWM instance with frequency
enable1.start(0)  # start PWM of required Duty Cycle
enable2 = GPIO.PWM(En2, 1000)  # create PWM instance with frequency
enable2.start(0)  # start PWM of required Duty Cycle

try:
    while True:

        enable1.ChangeDutyCycle(50)  # provide duty cycle in the range 0-100
        enable2.ChangeDutyCycle(50)  # provide duty cycle in the range 0-100
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            GPIO.output(I1, GPIO.HIGH)
            GPIO.output(I2, GPIO.LOW)
            GPIO.output(I3, GPIO.HIGH)
            GPIO.output(I4, GPIO.LOW)

        elif char == curses.KEY_DOWN:
            GPIO.output(I1, GPIO.LOW)
            GPIO.output(I2, GPIO.HIGH)
            GPIO.output(I3, GPIO.LOW)
            GPIO.output(I4, GPIO.HIGH)

        elif char == curses.KEY_RIGHT:
            GPIO.output(I1, GPIO.HIGH)
            GPIO.output(I2, GPIO.LOW)
            GPIO.output(I3, GPIO.LOW)
            GPIO.output(I4, GPIO.HIGH)

        elif char == curses.KEY_LEFT:
            GPIO.output(I1, GPIO.LOW)
            GPIO.output(I2, GPIO.HIGH)
            GPIO.output(I3, GPIO.HIGH)
            GPIO.output(I4, GPIO.LOW)

        elif char == ord('s'):
            GPIO.output(I1, GPIO.LOW)
            GPIO.output(I2, GPIO.LOW)
            GPIO.output(I3, GPIO.LOW)
            GPIO.output(I4, GPIO.LOW)

finally:
    # Close down curses properly, inc turn echo back on!
    curses.nocbreak();
    screen.keypad(0);
    curses.echo()
    curses.endwin()
    GPIO.cleanup()
