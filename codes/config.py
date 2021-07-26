import configparser,os,sys,logging
from datetime import datetime

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.getcwd()

# application_path = os.path.dirname(sys.executable)
logDir = os.path.join(application_path,'logs')
if not os.path.exists(logDir): os.makedirs(logDir)
logging.basicConfig(filename=os.path.join(logDir,"Logs.log"),
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.info(f"Application path : {application_path}")

def updateConfigCounts(**args):
    config = configparser.ConfigParser()
    config.read(os.path.join(application_path,'config.txt'))
    day = config['counts_cur'].getint('day')
    today = datetime.today().day
    if today == day:
        for key,val in args.items():
            config.set('counts_cur',key,str(val))
    else:
        for key,val in args.items():
            config.set('counts_cur',key,str(0))
        # updateConfigCounts(groups = 0,individuals = 0,count = 0,day = today)
        # initGrpCnt=initTtlCnt=initIndvCnt=0
    config.set('counts_cur','day',str(today))
    config.write(open('config.txt', 'w'))

if os.path.exists(os.path.join(application_path,'config.txt')):
    # application_path = os.path.dirname(sys.executable)
    config = configparser.ConfigParser()
    config.read(os.path.join(application_path,'config.txt'))
    INPUT_VIDEO = config['data'].get('INPUT_VIDEO')
    shop_num = config['data'].get('shop_num')
    shop_name = config['data'].get('shop_name')
    day = config['counts_cur'].getint('day')
    today = datetime.today().day
    optionalVar = config['optional']
    dashboardVar = config['dashboard']
    dashboard_url, dashboard_port = dashboardVar.get('url'),dashboardVar.getint('port')
    if today == day:
        initGrpCnt = config['counts_cur'].getint('groups')
        initTtlCnt = config['counts_cur'].getint('count')
        initIndvCnt = config['counts_cur'].getint('individuals')
    else:
        updateConfigCounts(groups = 0,individuals = 0,count = 0,day = today)
        initGrpCnt=initTtlCnt=initIndvCnt=0

else:
    #print("File config.txt doesn't exist")
    logger.critical("File config.txt doesn't exist")
    # sys.exit()

