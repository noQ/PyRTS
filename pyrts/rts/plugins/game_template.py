def init_controller():
    #Return the information needed on the controller
    #for this game
    return {}

def init_session(session):
    #Initialize any game state here
    #Start any game threads 
    pass

def stop_session(session):
    #Free any resources allocated in init
    #Stop any game threads 
    pass

def send_msg(client, msg, omit_myself=True):
    for team in client.session.teams.values():
        for uid,user in team:
            if client.uid!=uid:
                user.send(msg)

def on_join(client):
    send_msg(client, "j"+client.uid)

def on_leave(client):
    send_msg(client, "l"+client.uid)
            
def on_event(client, data):
    send_msg(client, "e"+client.uid, omit_myself=False)

