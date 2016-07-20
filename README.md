# primedice-bot

primedice.com bot playing progression system

x1,12 multiplier @ 10% chance

+ pygame simple gui for 3,5'' TFT screen
+ node.js simple www logger
+ run as cronjob @reboot
+ dropped sqlite loggin in favour of python logging resulting in better performance 
+ dropped tor proxy connections couldn't make them work on large scale 
+ added withdraw api call and auto withdraw code 
+ added new config strings to configure the withdraw proccess 
+ added sing change after x losses in a row 