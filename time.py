from datetime import datetime


today = datetime.now()
# attrs = vars(today)
str = today.strftime('%m/%d/%Y-%H:%M:%S')
print("Today's date:", str)
