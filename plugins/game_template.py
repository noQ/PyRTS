from pyrts.core.controller.session import ControllerPlugin

class gametemplate(ControllerPlugin):
    """ Game example """
    
    def __init__(self, **kwargs):
        print "Loading test"
        self.game_type  = None
        super(hungryfrog, self).__init__(**kwargs)


    def setup_teams(self, type):
        ''' setup game teams 1 vs 1 '''
        if type in "1x1":
            self.game_type = type
            return ["Blue Team", "Red Team"]
    
    def can_start_game(self, session):
        total_users = len(session.users)
        if total_users > 0:
            print "total users:" + str(total_users)
        users_ready = 0 
        if total_users == 2:
            for user in session.users:
                if user.ready:
                    users_ready += 1
        if total_users == users_ready:
            print "Yes, start the game!"
            return True
        return False
    
    def get_joinable_team(self, teams, uid, name):
        if name is None:
            import random
            choose = random.randrange(0, len(teams))
            return teams[choose].name
        return name
