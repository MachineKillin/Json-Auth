import random, json, requests, string, time
from datetime import datetime, date, timedelta
from flask import *

app = Flask("__app__")
start = time.time()
webhook = "yourwebhookurl"
privateh = "yourprivateheaderkey"

def authwebhook(data):
    jsons = {"content": str(data)}
    requests.post(webhook, json=jsons)

@app.route("/uptime")
def uptime():
    end = time.time()
    uptime = {"uptime": end - start}
    return jsonify(uptime)

@app.route("/api/info", methods=['POST'])
def info(): #TODO
    print("not implemented: /api/info")

@app.route("/api/register", methods=['POST'])
def register(): #key, username, password, discord, hwid
    #if request.headers['Auth'] != "Json-Auth":  return({"Success": 0, "Error": "Invalid Header."}) example
    datas = request.get_json()
    key = datas['key']
    username = datas['username']
    password = datas['password']
    discord = datas['discord']
    hwid = datas['hwid']
    if key == "": return({"Success": 0, "Error": "The field key cannot be blank."})
    if username == "": return({"Success": 0, "Error": "The field username cannot be blank."})
    if password == "": return({"Success": 0, "Error": "The field password cannot be blank."})
    if discord == "": return({"Success": 0, "Error": "The field discord cannot be blank."})
    with open("db.json", "r") as file: file_database = json.load(file)
    with open("keys.json", "r") as file: file_keys = json.load(file)
    for k in file_keys['keys']:
        if str(k).split("'")[1] == key:
            db = file_database['data']
            for user in db:
                if username == user['username']: return({"Success": 0, "Error": "This username is taken."})
            kay = k[key]
            program = kay['program']
            expire = kay['expire']
            with open('db.json') as fp:
                db = json.load(fp)
            db['data'].append({'username':username, 'password':password, 'discord':discord, 'programs':[{'program':program, 'hwid':hwid, 'reset':str(date.today().strftime("%m/%d/%Y")), 'expire':expire}]})
            with open('db.json', 'w') as json_file:
                json.dump(db, json_file, indent=4, separators=(',',': '))
            del k[key]
            authwebhook(f"License created: ```Username: {username}\nPassword: {password}\nDiscord: {discord}\nProgram: {program}\nHWID: {hwid}\nExpiration: {expire}```")
            return({"Success": 1, "Info": "License created."})
    return({"Success": 0, "Error": "Key does not exist"})

@app.route("/api/add", methods=['POST'])
def addprogram(): #username, program, days
    if request.headers['PRIV'] == privateh:
        datas = request.get_json()
        username = datas['username']
        program = datas['prog']
        days = datas['days']
        for User in json_file['data']:
            if User['username'] == username:
                expire = datetime.strftime(datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y") + timedelta(days=int(days)), "%m/%d/%Y")
                with open('db.json') as fp:
                    db = json.load(fp)
                db = db['data']
                db['programs'].append({'program':program, 'hwid':'', 'reset':str(date.today().strftime("%m/%d/%Y")), 'expire':expire.strftime("%m/%d/%Y")})
                with open('db.json', 'w') as json_file:
                    json.dump(db, json_file, indent=4, separators=(',',': '))
                authwebhook(f"{program} added to {username}|<@{User['discord']}>'s account. Expires: "+expire.strftime("%m/%d/%Y"))
                return({"Success": 1, "Info": f"{program} added to {username}'s account. Expires: "+expire})
        return({"Success": 0, "Error": "User does not exist"})
    return({"Success": 0, "Error": "You're not allowed to do this."})

@app.route("/api/generate", methods=['POST'])
def genkey(): #program, days
    datas = request.get_json()
    program = datas["prog"]
    days = datas["days"]
    if request.headers['PRIV'] == privateh:
        key = f"AUTHKEY-{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))}-{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))}-{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))}-{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))}"
        expire = datetime.strftime(datetime.strptime(date.today().strftime("%m/%d/%Y"), "%m/%d/%Y") + timedelta(days=int(days)), "%m/%d/%Y")
        with open('keys.json') as f:
            keys = json.load(f)
        keys['keys'].append({key:{'program':program, "expire":expire}})
        with open('keys.json', 'w') as json_file:
            json.dump(keys, json_file, indent=4, separators=(',',': '))
        authwebhook(f"Key generated: `Key:{key} Program:{program} Expire:{expire} IP:{request.remote_addr}`")
        return({"Success": 1, "Key": key, "Program": program, "Expire": expire})
    authwebhook(f"||@everyone|| Someone tried to generate a key for `{program}`! IP:{request.remote_addr}")
    return({"Success": 0, "Error": "You're not allowed to generate keys."})

@app.route("/api/hwid", methods=['POST'])
def resethwid(): #program, discord
    #if request.headers != "Json-Auth":  return({"Success": 0, "Error": "Invalid Header."})
    datas = request.get_json()
    program = datas["prog"]
    id = datas["discord"]
    with open("database.json", "r") as file:
        json_file = json.load(file)
        for User in json_file['data']:
            if User['discord'] == id:
                for prog in User['programs']:
                    if prog == program:
                        reset = datetime.strptime(prog['reset'], "%m/%d/%Y") + timedelta(days=2)
                        reset = reset.strftime("%m/%d/%Y")
                        if reset <= date.today().strftime("%m/%d/%Y"):
                            if prog['hwid'] != "":
                                prog['reset'] = str(date.today().strftime("%m/%d/%Y"))
                                prog['hwid'] = ""
                                return({"Success": 1, "Info": "Your HWID has been reset."})
                            authwebhook(f"{User['username']}|<@{id}> reset their hwid.")
                            return({"Success": 0, "Error": "You should already be able to reset your HWID."})
                        now = str(datetime.now().strftime("%m/%d/%Y"))
                        time = datetime.strptime(reset, "%m/%d/%Y")-datetime.strptime(now, "%m/%d/%Y")
                        authwebhook(f"{User['username']}|<@{id}> tried to reset their hwid but has {time.days} remaining until they can.")
                        return({"Success": 0, "Error": f"You cannot reset your HWID, you must wait {time.days} days."})
                authwebhook(f"{User['username']}|<@{id}> tried to reset their hwid for an unknown program.")
                return({"Success": 0, "Error": f"Program not found."})
        authwebhook(f"{User['username']}|<@{id}> tried to reset their hwid but their account doesnt exist in the database.")
        return({"Success": 0, "Error": f"Your account does not exist."})

@app.route("/api/auth", methods=['POST'])
def auth(): #username, password, hwid, program
    #if request.headers != "Json-Auth":  return({"Success": 0, "Error": "Invalid Header."})
    datas = request.get_json()
    username = datas["username"]
    password = datas["password"]
    hwid = datas["hwid"]
    program = datas["prog"]
    with open("db.json", "r") as file:
        json_file = json.load(file)
        for User in json_file['data']:
            if User['username'] == username:
                if User['password'] == password:
                    for prog in User['programs']:
                        if prog == program:
                            if prog['hwid'] != "":
                                if prog['hwid'] == hwid:
                                    now = str(datetime.now().strftime("%m/%d/%Y"))
                                    subtime = prog['expiry']
                                    a = datetime.strptime(subtime, "%m/%d/%Y")
                                    b = datetime.strptime(now, "%m/%d/%Y")
                                    remaining = a - b
                                    if now <= subtime:
                                        authwebhook(f"{username} | <@{User['discord']}> logged in successfully to {program} with {remaining.days} license days remaining.")
                                        return({"Success": 1, "Username": f"{User['username']}", "Expiration": f"{User['expiry']}", "Remaining": remaining.days})
                                    elif now > subtime:
                                        authwebhook(f"{username} | <@{User['discord']}> tried to login to {program} with an expired license.")
                                        return({"Success": 0, "Error": f"Your subscription has expired. Consider Renewing."})
                                    else:
                                        authwebhook(f"{username} | <@{User['discord']}> tried to login to {program} but their license had an unknown expiration value.")
                                        return({"Success": 0, "Error": "An unknown Error has occurred."})
                                else: 
                                    return({"Success": 0, "Error": "Invalid HWID."})
                            else:
                                prog['hwid'] = hwid
                                prog['reset'] = str(date.today().strftime("%m/%d/%Y"))
                                now = str(datetime.now().strftime("%m/%d/%Y"))
                                subtime = prog['expiry']
                                a = datetime.strptime(subtime, "%m/%d/%Y")
                                b = datetime.strptime(now, "%m/%d/%Y")
                                remaining = a - b
                                if now <= subtime:
                                    authwebhook(f"{username} | <@{User['discord']}> logged in successfully to {program} with {remaining.days} license days remaining.")
                                    return({"Success": 1, "Username": f"{User['username']}", "Expiration": f"{User['expiry']}", "Remaining": remaining.days})
                                elif now > subtime:
                                    authwebhook(f"{username} | <@{User['discord']}> tried tp login to {program} with an expired license.")
                                    return({"Success": 0, "Expiration": f"Your subscription has expired. Consider Renewing."})
                                else:
                                    authwebhook(f"{username} | <@{User['discord']}> tried to login to {program} but their license had an unknown expiration value.")
                                    return({"Success": 0, "Error": "An unknown Error has occurred."})
                    authwebhook(f"{username} | <@{User['discord']}> tried to login to an unknown program: {program}")
                    return({"Success": 0, "Error": "You do not have that program."}) #Invalid program
                else:
                    authwebhook(f"{username} tried to login with an invalid password: {password}")
                    return({"Success": 0, "Error": "Invalid Password."}) #Invalid password
            else:
                authwebhook(f"Unknown account: ```USERNAME:{username}\nPASSWORD:{password}\nPROGRAM:{program}\nHWID:{hwid}\nIP:{request.remote_addr}```")
                return({"Success": 0, "Error": "User does not exist"}) #Invalid username          

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"Error": "Something Happened: "+ str(e)}), 404

app.run("0.0.0.0", 80, debug=True)
