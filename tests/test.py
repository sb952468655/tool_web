import re

text = r'''===============================================================================
Ports on Slot 1
===============================================================================
Port          Admin Link Port    Cfg  Oper LAG/ Port Port Port   C/QS/S/XFP/
Id            State      State   MTU  MTU  Bndl Mode Encp Type   MDIMDX
-------------------------------------------------------------------------------
1/1/1         Up    Yes  Up      1614 1614    - netw null xgige  10GBASE-LR  *
1/1/2         Down  No   Down    9212 9212    - netw null xgige  
1/2/1         Up    Yes  Up      1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/2         Up    Yes  Up      1522 1522    2 accs qinq xcme   GIGE-LX  20KM
1/2/3         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/4         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/5         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/6         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/7         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/8         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/9         Up    No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/10        Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/11        Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
1/2/12        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/13        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/14        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/15        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/16        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/17        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/18        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/19        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
1/2/20        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM

===============================================================================
Ports on Slot 2
===============================================================================
Port          Admin Link Port    Cfg  Oper LAG/ Port Port Port   C/QS/S/XFP/
Id            State      State   MTU  MTU  Bndl Mode Encp Type   MDIMDX
-------------------------------------------------------------------------------
2/1/1         Up    No   Down    1614 1614    - netw null xgige  
2/1/2         Down  No   Down    9212 9212    - netw null xgige  
2/2/1         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/2         Up    Yes  Up      1522 1522    2 accs qinq xcme   GIGE-LX  20KM
2/2/3         Down  No   Down    1522 1522    - accs qinq xcme   GIGE-LX  20KM
2/2/4         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/5         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/6         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/7         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/8         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/9         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/10        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/11        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/12        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/13        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/14        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/15        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/16        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/17        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/18        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/19        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM
2/2/20        Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM'''

p_port = r'''(\d{1,2}/\d{1,2}/\d{1,2}) {6,9}(Up|Down) {2,4}(Yes|No) {2,3}(Up|Down) {4,6}(\d{4}) (\d{4}) {4}(-|\d) (accs|netw) (null|qinq) (xgige|xcme) {2,3}((10GBASE-LR|GIGE-LX) {2}(\d{2}KM|\*))?'''

res = re.findall(p_port, text)

print(res)