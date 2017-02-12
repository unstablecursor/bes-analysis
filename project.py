import os.path
from tornado_jinja2 import Jinja2Loader
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from jinja2 import *
import pandas as pd
import requests
from datetime import datetime
import tornado.web
import jinja2


from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class result_handler(tornado.web.RequestHandler):
    def post(self):
        now = datetime.now()
        code_list = []
        bond_mon_list = [[]]
        base_url = 'http://ws.spk.gov.tr/PortfolioValues/api/PortfoyDegerleri'
        portfolio = pd.DataFrame({'Name': [],
                                  'Number': [],
                                  'Price': []})
        backtrack = pd.DataFrame({'Date': [],
                                  'Market Value': [],
                                  'Cost': [],
                                  'Profit': []})


        company = self.get_argument('name')
        #date = self.get_argument('date')
        money = self.get_argument('money')

        month = self.get_argument('month')
        day = 1
        year = self.get_argument('year')
        date = "" + month + "-" + "1" + "-" + year
        enddate = "" + str(now.month) + "-" + "1" + "-" + str(now.year)

        parser_url = 'http://ws.spk.gov.tr/PortfolioValues/api/PortfoyDegerleri/2/'
        resp = requests.get("" + parser_url + date + "/" + date)
        while resp.text == "null":
            day += 1
            date = "" + month + "-" + str(day) + "-" + year
            resp = requests.get("" + parser_url + date + "/" + date)


        for item in resp.json():
            comp_name_str = (item['FonUnvani']).split(' ', 1)[0]
            if comp_name_str == company:
                code_list.append(item['FonKodu'])

        #TODO implement the share algorithm... Find the %s

        money_per_share = float(money)/len(code_list)
        cost = 0
        bon_emp_list = []
        for value in code_list:
            response = requests.get("" + base_url + "/" + value + "/2/" + "/" + date + "/" + date)
            print(date)
            print(value)
            bpd = response.json()[0]['BirimPayDegeri']
            number = int(money_per_share / bpd)
            vall = number * bpd
            bond_mon_list.append(vall)
            #number = int((float(money) * 0.3) / bpd)
            cost += number * bpd
            bon_emp_list.append(number * bpd)
            s = pd.Series([value, number, bpd], index=['Name', 'Number', 'Price'])
            portfolio = portfolio.append(s, ignore_index=True);

        bond_mon_list.append(bon_emp_list)
        portfolio['Value'] = portfolio.Number * portfolio.Price
        mv = portfolio['Value'].sum()
        t = pd.Series([date, mv, cost, 0], index=['Date', 'Market Value', 'Cost', 'Profit'])
        backtrack = backtrack.append(t, ignore_index=True)


        start = datetime.strptime(date, "%m-%d-%Y")
        stop = datetime.strptime(enddate, "%m-%d-%Y")
        from datetime import timedelta
        while start <= stop:
            start = start + timedelta(days=32)
            date = datetime.strftime(start, '%m-%d-%Y')
            month = date.split('-')[0]
            day = date.split('-')[1]
            year = date.split('-')[2]
            day = 1
            date = "" + str(month) + "-" + str(day) + "-" + str(year)
            start =  datetime.strptime(date, "%m-%d-%Y")
            if(start >= stop):
                break
            i = 0
            bon_emp_list = []
            for p in portfolio.iterrows():
                response = requests.get("" + base_url + "/" + p[1]['Name'] + "/2/" + "/" + date + "/" + date)
                while response.text == "null":
                    day += 1
                    date = "" + str(month) + "-" + str(day) + "-" + str(year)
                    response = requests.get("" + base_url + "/" + p[1]['Name'] + "/2/" + "/" + date + "/" + date)
                bpd = response.json()[0]['BirimPayDegeri']
                number = int(money_per_share / bpd)
                cost += number * bpd
                portfolio.ix[i, 'Price'] = bpd
                portfolio.ix[i, 'Number'] += number
                assert isinstance(bpd, object)
                vall = portfolio.ix[i, 'Number'] * bpd
                bon_emp_list.append(vall)



                i += 1
                print("Name:" + str(p[1]['Name']) + "\n Number: " + str(number) + "\nBPD: " + str(bpd) + "\nMoney Spend: " + str(number * bpd) + "\nCost: " + str(cost))
            bond_mon_list.append(bon_emp_list)
            portfolio['Value'] = portfolio.Number * portfolio.Price
            mv = portfolio['Value'].sum()

            profit_ = mv - cost

            s = pd.Series([date, mv, cost, profit_], index=['Date', 'Market Value', 'Cost', 'Profit'])
            backtrack = backtrack.append(s, ignore_index=True)

        #bond_mon = pd.DataFrame(bond_mon_list, columns=code_list)
        #bond_mon = pd.DataFrame(bond_mon_list)
        #backtrack.to_csv('performance.csv')
        #bond_mon.to_csv('bonds.csv')
        #portfolio.to_csv('portfolio.csv')
        self.render('result.html', tables=backtrack.to_html(), portfolio = portfolio.to_html())


if __name__ == '__main__':
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    settings = dict(template_loader=jinja2_loader)
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler), (r'/result', result_handler)],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),**settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

