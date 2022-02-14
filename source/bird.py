class Bird():
    
    def __init__(self, rect):
        self.rect = rect
        self.jump = False
        self.gravity = 0
        self.game_over = False
        self.angle = 0

    def update_angle(self): # determines angle of bird image based off gravity's pull
        if self.gravity < -1: # these numbers are just numbers that looked good
            self.angle = 30
        else:
            self.angle = self.gravity * -10

    def bird_reset(self):
        self.gravity = 0
        self.game_over = False
        self.angle = 0